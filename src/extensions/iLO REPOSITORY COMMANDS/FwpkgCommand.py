# ##
# Copyright 2016 Hewlett Packard Enterprise, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ##

# -*- coding: utf-8 -*-
""" Fwpkg Command for rdmc """

import os
import sys
import json
import random
import shutil
import zipfile

from optparse import OptionParser, SUPPRESS_HELP
from string import ascii_lowercase


from rdmc_base_classes import RdmcCommandBase

from rdmc_helper import IncompatibleiLOVersionError, ReturnCodes, Encryption, \
                        InvalidCommandLineErrorOPTS, InvalidCommandLineError,\
                        InvalidFileInputError, UploadError, TaskQueueError, FirmwareUpdateError

def _get_comp_type(payload):
    """ Get's the component type and returns it

    :param payload: json payload of .fwpkg file
    :type payload: dict.
    :returns: returns the type of component. Either A,B,C, or D.
    :rtype: string
    """
    ctype = ''
    if "Uefi" in payload['UpdatableBy'] and "RuntimeAgent" in payload['UpdatableBy']:
        ctype = 'D'
    else:
        for device in payload['Devices']['Device']:
            for image in device['FirmwareImages']:
                if image['DirectFlashOk']:
                    ctype = 'A'
                    if image['ResetRequired']:
                        ctype = 'B'
                        break
                elif image['UefiFlashable']:
                    ctype = 'C'
                    break
                else:
                    ctype = 'D'

    return ctype

class FwpkgCommand(RdmcCommandBase):
    """ Fwpkg command class """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self, \
            name='flashfwpkg', \
            usage='flashfwpkg [FWPKG PATH] [OPTIONS]\n\n\tRun to upload and flash ' \
              'components from fwpkg files.\n\n\tUpload component and flashes it or sets a task'\
              'queue to flash.\n\texample: flashfwpkg component.fwpkg.\n\n\t'
              'Skip extra checks before adding taskqueue. (Useful when adding '
              'many flashfwpkg taskqueue items in sequence.)\n\texample: fwpkg '\
              'component.fwpkg --ignorechecks',\
            summary='Flashes fwpkg components using the iLO repository.',\
            aliases=['Fwpkg'], \
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)
        self.uploadobj = rdmcObj.commands_dict["UploadComponentCommand"](rdmcObj)
        self.taskqueueobj = rdmcObj.commands_dict["UpdateTaskQueueCommand"](rdmcObj)
        self.fwupdateobj = rdmcObj.commands_dict["FirmwareUpdateCommand"](rdmcObj)

    def run(self, line):
        """ Main fwpkg worker function

        :param line: string of arguments passed in
        :type line: str.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.fwpkgvalidation(options)

        if self.typepath.defs.isgen9:
            raise IncompatibleiLOVersionError(\
                      'iLO Repository commands are only available on iLO 5.')

        if not len(args) == 1:
            raise InvalidCommandLineError("Fwpkg command only takes one argument.")

        if self._rdmc.app.getiloversion() <= 5.120 and args[0].lower().startswith('iegen10'):
            raise IncompatibleiLOVersionError('Please upgrade to iLO 5 1.20 or '\
                       'greater to ensure correct flash of this firmware.')
        tempdir = ''
        if not args[0].endswith('.fwpkg'):
            InvalidFileInputError("Invalid file type. Please make sure the file "\
                                  "provided is a valid .fwpkg file type.")

        try:
            components, tempdir, comptype = self.preparefwpkg(self, args[0])
            if comptype == 'D':
                raise InvalidFileInputError("Unable to flash this fwpkg file.")
            elif comptype == 'C':
                try:
                    self.taskqueuecheck()
                except TaskQueueError as excp:
                    if options.ignore:
                        sys.stderr.write(str(excp)+'\n')
                    else:
                        raise excp
            self.applyfwpkg(options, tempdir, components, comptype)

            if comptype == 'A':
                message = "Firmware has successfully been flashed.\n"
                if 'ilo' in args[0].lower():
                    message += "iLO will reboot to complete flashing. Session will be"\
                                " terminated.\n"
            elif comptype == 'B':
                message = "Firmware has successfully been flashed and a reboot is required for "\
                                                                "this firmware to take effect.\n"
            elif comptype == 'C':
                message = "This firmware is set to flash on reboot.\n"
            sys.stdout.write(message)
        finally:
            if tempdir:
                shutil.rmtree(tempdir)
            if 'ilo' in args[0].lower():
                self.logoutobj.run("")
        return ReturnCodes.SUCCESS

    def taskqueuecheck(self):
        """ Check taskqueue for potential issues before starting """

        select = "ComputerSystem."
        results = self._rdmc.app.select(selector=select, rel=True)

        try:
            results = results[0]
        except:
            pass

        powerstate = results.resp.dict['PowerState']
        tasks = self._rdmc.app.getcollectionmembers(\
                                '/redfish/v1/UpdateService/UpdateTaskQueue/')

        for task in tasks:
            if task['State'] == 'Exception':
                raise TaskQueueError("Exception found in taskqueue which will "\
                               "prevent firmware from flashing. Please run "\
                               "iLOrest command: taskqueue --cleanqueue to clear"\
                               " any errors before continuing.")
            if task['UpdatableBy'] == 'Uefi' and not powerstate == 'Off' or \
                task['Command'] == "Wait":
                raise TaskQueueError("Taskqueue item found that will "\
                               "prevent firmware from flashing immediately. Please "\
                               "run iLOrest command: taskqueue --resetqueue to "\
                               "reset the queue if you wish to flash immediately "\
                               "or include --ignorechecks to add this firmware "\
                               "into the task queue anyway.")
        if tasks:
            sys.stdout.write("Items are in the taskqueue that may delay the "\
                             "flash until they are finished processing. Use the"\
                             " taskqueue command to monitor updates.\n")

    @staticmethod
    def preparefwpkg(self, pkgfile):
        """ Prepare fwpkg file for flashing

        :param pkgfile: Location of the .fwpkg file
        :type pkgfile: string.
        :returns: returns the files needed to flash, directory they are located
                                                            in, and type of file.
        :rtype: string, string, string
        """
        files = []
        imagefiles = []
        payloaddata = None
        tempfoldername = ''.join(random.choice(ascii_lowercase) for i in range(12))

        tempdir = os.path.join(self._rdmc.app.config.get_cachedir(), tempfoldername)
        if not os.path.exists(tempdir):
            os.makedirs(tempdir)
        try:
            zfile = zipfile.ZipFile(pkgfile)
            zfile.extractall(tempdir)
            zfile.close()
        except:
            raise InvalidFileInputError("Unable to unpack file.")

        files = os.listdir(tempdir)

        if 'payload.json' in files:
            with open(os.path.join(tempdir, 'payload.json'), "r") as pfile:
                data = pfile.read()
            payloaddata = json.loads(data)
        else:
            raise InvalidFileInputError("Unable to find payload.json in fwpkg file.")

        comptype = _get_comp_type(payloaddata)

        if comptype == 'C':
            imagefiles = [self.type_c_change(tempdir, pkgfile)]
        else:
            for device in payloaddata['Devices']['Device']:
                for firmwareimage in device['FirmwareImages']:
                    if firmwareimage['FileName'] not in imagefiles:
                        imagefiles.append(firmwareimage['FileName'])

        return imagefiles, tempdir, comptype

    def type_c_change(self, tdir, pkgloc):
        """ Special changes for type C

        :param tempdir: path to temp directory
        :type tempdir: string.
        :param components: components to upload
        :type components: list.

        :returns: The location of the type C file to upload
        :rtype: string.
        """

        shutil.copy(pkgloc, tdir)

        fwpkgfile = os.path.split(pkgloc)[1]
        zfile = fwpkgfile[:-6] + '.zip'
        zipfileloc = os.path.join(tdir, zfile)

        os.rename(os.path.join(tdir, fwpkgfile), zipfileloc)

        return zipfileloc

    def applyfwpkg(self, options, tempdir, components, comptype):
        """ Apply the component to iLO

        :param options: command line options
        :type options: list.
        :param tempdir: path to temp directory
        :type tempdir: string.
        :param components: components to upload
        :type components: list.
        :param comptype: type of component. Either A,B,C, or D.
        :type comptype: str.
        """

        for component in components:
            taskqueuecommand = ' create %s ' % os.path.basename(component)
            if options.tover:
                taskqueuecommand = ' create %s --tpmover' % component
            if component.endswith('.fwpkg') or component.endswith('.zip'):
                uploadcommand = '--component %s' % component
            else:
                uploadcommand = '--component %s' % os.path.join(tempdir, component)

            if options.forceupload:
                uploadcommand += ' --forceupload'
            if comptype in ['A', 'B']:
                uploadcommand += ' --update_target --update_repository'

            sys.stdout.write("Uploading firmware: %s\n" % os.path.basename(component))
            try:
                self.uploadobj.run(uploadcommand)
            except UploadError:
                if comptype in ['A', 'B']:
                    select = self.typepath.defs.hpilofirmwareupdatetype
                    results = self._rdmc.app.select(selector=select)

                    try:
                        results = results[0]
                    except:
                        pass

                    if results:
                        update_path = results.resp.request.path
                        error = self._rdmc.app.get_handler(update_path, silent=True)
                        self.fwupdateobj.printerrmsg(error)
                    else:
                        raise FirmwareUpdateError("Error occurred while updating the firmware.")
                else:
                    raise UploadError('Error uploading component.')

            if comptype == 'C':
                sys.stdout.write("Setting a taskqueue item to flash UEFI flashable firmware.\n")
                self.taskqueueobj.run(taskqueuecommand)

    def fwpkgvalidation(self, options):
        """ fwpkg validation function

        :param options: command line options
        :type options: list.
        """
        inputline = list()
        client = None

        if options.encode and options.user and options.password:
            options.user = Encryption.decode_credentials(options.user)
            options.password = Encryption.decode_credentials(options.password)

        try:
            client = self._rdmc.app.get_current_client()
            if options.user and options.password:
                if not client.get_username():
                    client.set_username(options.user)
                if not client.get_password():
                    client.set_password(options.password)
        except:
            if options.user or options.password or options.url:
                if options.url:
                    inputline.extend([options.url])
                if options.user:
                    inputline.extend(["-u", options.user])
                if options.password:
                    inputline.extend(["-p", options.password])
            else:
                if self._rdmc.app.config.get_url():
                    inputline.extend([self._rdmc.app.config.get_url()])
                if self._rdmc.app.config.get_username():
                    inputline.extend(["-u", self._rdmc.app.config.get_username()])
                if self._rdmc.app.config.get_password():
                    inputline.extend(["-p", self._rdmc.app.config.get_password()])

        if not inputline and not client:
            sys.stdout.write('Local login initiated...\n')
        if not client or inputline:
            self.lobobj.loginfunction(inputline)

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        customparser.add_option(
            '--url',
            dest='url',
            help="Use the provided iLO URL to login.",
            default=None,
        )
        customparser.add_option(
            '-u',
            '--user',
            dest='user',
            help="If you are not logged in yet, including this flag along"\
            " with the password and URL flags can be used to log into a"\
            " server in the same command.""",
            default=None,
        )
        customparser.add_option(
            '-p',
            '--password',
            dest='password',
            help="""Use the provided iLO password to log in.""",
            default=None,
        )
        customparser.add_option(
            '--forceupload',
            dest='forceupload',
            action="store_true",
            help='Add this flag to force upload firmware with the same name '\
                    'already on the repository.',
            default=False,
        )
        customparser.add_option(
            '--ignorechecks',
            dest='ignore',
            action="store_true",
            help='Add this flag to ignore all checks to the taskqueue '\
                    'before attempting to process the .fwpkg file.',
            default=False,
        )
        customparser.add_option(
            '--tpmover',
            dest='tover',
            action="store_true",
            help="If set then the TPMOverrideFlag is passed in on the "\
            "associated flash operations",
            default=False
        )
        customparser.add_option(
            '-e',
            '--enc',
            dest='encode',
            action='store_true',
            help=SUPPRESS_HELP,
            default=False,
        )
