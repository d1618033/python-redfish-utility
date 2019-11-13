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
""" Upload Component Command for rdmc """

import os
import sys
import json
import time

import shutil

from random import choice
from string import ascii_lowercase
from argparse import ArgumentParser

import ctypes
from ctypes import c_char_p, c_int, c_uint32

from six.moves import input

import redfish.hpilo.risblobstore2 as risblobstore2
from redfish.ris.rmc_helper import InvalidPathError

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group
from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, Encryption, UploadError, \
            InvalidCommandLineError, IncompatibleiLOVersionError, TimeOutError


def human_readable_time(seconds):
    """ Returns human readable time

    :param seconds: Amount of seconds to parse.
    :type seconds: string.
    """
    seconds = int(seconds)
    hours = seconds / 3600
    seconds = seconds % 3600
    minutes = seconds / 60
    seconds = seconds % 60

    return str(hours) + " hour(s) " + str(minutes) + \
            " minute(s) " + str(seconds) + " second(s) "


class UploadComponentCommand(RdmcCommandBase):
    """ Constructor """

    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self, \
            name='uploadcomp', \
            usage='uploadcomp [OPTIONS]\n\n\tRun to upload the component on ' \
                'to iLO Repository\n\n\tUpload component to the iLO ' \
                'repository.\n\texample: uploadcomp --component <path> ' \
                '--compsig <path_to_signature>\n\n\tFlash the component ' \
                'instead of add to the iLO repository.\n\texample: ' \
                'uploadcomp --component <binary_path> --update_target ' \
                '--update_repository', \
            summary='Upload components/binary to the iLO Repository.', \
            aliases=['Uploadcomp'], \
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)
        self.fwpkgprepare = rdmcObj.commands_dict["FwpkgCommand"].preparefwpkg

    def run(self, line):
        """ Wrapper function for upload command main function

        :param line: string of arguments passed in
        :type line: str.
        """
        try:
            (options, _) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.uploadcommandvalidation(options)
        fwpkg = False
        if options.component.endswith('.fwpkg'):
            fwpkg = True
            comp, loc, ctype = self.fwpkgprepare(self, options.component)
            if ctype == 'C':
                options.component = comp[0]
            else:
                options.component = os.path.join(loc, comp[0])

        if self.typepath.defs.isgen9:
            raise IncompatibleiLOVersionError(\
                      'iLO Repository commands are only available on iLO 5.')

        filestoupload = self._check_and_split_files(options)

        if self.componentvalidation(options, filestoupload):
            start_time = time.time()
            ret = ReturnCodes.FAILED_TO_UPLOAD_COMPONENT

            if 'blobstore' in self._rdmc.app.current_client.base_url:
                ret = self.uploadlocally(filestoupload, options)
            else:
                ret = self.uploadfunction(filestoupload, options)

            sys.stdout.write("%s\n" % human_readable_time(time.time() - start_time))

            if len(filestoupload) > 1:
                path, _ = os.path.split((filestoupload[0])[1])
                shutil.rmtree(path)
            elif fwpkg:
                shutil.rmtree(loc)
            if options.logout:
                self.logoutobj.run("")
        else:
            ret = ReturnCodes.SUCCESS

        return ret

    def componentvalidation(self, options, filelist):
        """ Check for duplicate component in repository

        :param options: command line options
        :type options: list.
		:param filelist: list of files to be uploaded (multiple files will be
               generated for items over 32K in size)
        :type filelist: list of strings
        """
        validation = True
        prevfile = None

        path = '/redfish/v1/UpdateService/ComponentRepository/?$expand=.'
        results = self._rdmc.app.get_handler(path, service=True, silent=True)

        results = results.dict

        if 'Members' in results and results['Members']:
            for comp in results['Members']:
                for filehndl in filelist:
                    if comp['Filename'].upper() == unicode(filehndl[0]).upper()\
                        and not options.forceupload and prevfile != filehndl[0].upper():
                        ans = input("A component with the same name (%s) has " \
                                    "been found. Would you like to upload and "\
                                    "overwrite this file? (y/n)" % comp['Filename'])

                        if ans.lower() == 'n':
                            sys.stdout.write('Upload stopped by user due to filename conflict.'\
                                             ' If you would like to bypass this check include the'\
                                             ' "--forceupload" flag.\n')
                            validation = False
                            break
                    if comp['Filename'].upper() == unicode(filehndl[0]).upper()\
                        and prevfile != filehndl[0].upper() and comp['Locked']:
                        sys.stdout.write('Component is currently locked by a taskqueue task or '\
                                         'installset. Remove any installsets or taskqueue tasks '\
                                         'containing the file and try again.\n')
                        validation = False
                        break
                    prevfile = str(comp['Filename'].upper())
        return validation

    def _check_and_split_files(self, options):
        """ Check and split the file to upload on to iLO Repository

        :param options: command line options
        :type options: list.
        """

        def check_file_wr(filename, rw):
            try:
                fd = open(filename, rw)
                fd.close()
            except IOError:
                raise InvalidFileInputError("The file \'%s\' could not be opened for upload" % \
                                            filename)

        maxcompsize = 32 * 1024 * 1024
        size = os.path.getsize(options.component)
        filelist = []

        # Lets get the component filename
        _, filename = os.path.split(options.component)
        check_file_wr(os.path.normpath(options.component), 'r')

        # This is to upload the binary directly to flash scenario
        if not options.componentsig:
            if not self.findcompsig(filename):
                return [(filename, options.component, options.componentsig, 0)]

        if size > maxcompsize:
            sys.stdout.write("Component is more than 32MB in size. ")
            sys.stdout.write("Component size = %s\n" % str(size))
            section = 1

            sigpath, _ = os.path.split(options.componentsig)
            check_file_wr(os.path.normpath(options.componentsig), 'r')
            filebasename = filename[:filename.rfind('.')]
            tempfoldername = "bmn" + ''.join(choice(ascii_lowercase) for i in range(12))

            tempdir = os.path.join(self._rdmc.app.config.get_cachedir(), tempfoldername)

            sys.stdout.write("Spliting component. Temporary " \
                                            "cache directory at %s\n" % tempdir)

            if not os.path.exists(tempdir):
                os.makedirs(tempdir)

            with open(options.component, 'rb') as component:
                while True:
                    data = component.read(maxcompsize)
                    if len(data) != 0:
                        sectionfilename = filebasename + "_part" + str(section)
                        sectionfilepath = os.path.join(tempdir, sectionfilename)

                        sectioncompsigpath = os.path.join(sigpath, sectionfilename + ".compsig")

                        writefile = open(sectionfilepath, 'wb')
                        writefile.write(data)
                        writefile.close()

                        item = (filename, sectionfilepath, sectioncompsigpath, section - 1)

                        filelist.append(item)
                        section += 1

                    if len(data) != maxcompsize:
                        break

            return filelist
        else:
            return [(filename, options.component, options.componentsig, 0)]

    def uploadfunction(self, filelist, options=None):
        """ Main upload command worker function

        :param filelist: List of files to upload.
        :type filelist: list.
        :param options: command line options
        :type options: list.
        """

        # returns a tuple with the state and the result dict
        state, result = self.get_update_service_state()

        if (state != "COMPLETED" and
                state != "COMPLETE" and
                state != "ERROR" and
                state != "IDLE"):
            sys.stdout.write("iLO UpdateService is busy. Please try again.")

            return ReturnCodes.UPDATE_SERVICE_BUSY

        sessionkey = self._rdmc.app.current_client.session_key

        etag = ""
        hpe = result['Oem']['Hpe']
        urltosend = "/cgi-bin/uploadFile"

        if 'PushUpdateUri' in hpe:
            urltosend = hpe['PushUpdateUri']
        elif 'HttpPushUri' in result:
            urltosend = result['HttpPushUri']
        else:
            return ReturnCodes.FAILED_TO_UPLOAD_COMPONENT

        for item in filelist:
            ilo_upload_filename = item[0]

            ilo_upload_compsig_filename = ilo_upload_filename[\
                                  :ilo_upload_filename.rfind('.')] + ".compsig"

            componentpath = item[1]
            compsigpath = item[2]

            _, filename = os.path.split(componentpath)

            if not etag:
                etag = "sum" + filename.replace('.', '')
                etag = etag.replace('-', '')
                etag = etag.replace('_', '')

            section_num = item[3]
            sessionkey = (sessionkey)

            parameters = {'UpdateRepository': options.update_repository, \
                          'UpdateTarget': options.update_target, \
                          'ETag': etag, 'Section': section_num}

            data = [('sessionKey', sessionkey), ('parameters', json.dumps(parameters))]

            if not compsigpath:
                compsigpath = self.findcompsig(componentpath)
            if compsigpath:
                with open(compsigpath, 'rb') as fle:
                    output = fle.read()
                data.append(('compsig', (ilo_upload_compsig_filename, output, \
                                                                'application/octet-stream')))
                output = None

            with open(componentpath, 'rb') as fle:
                output = fle.read()
            data.append(('file', (ilo_upload_filename, output, 'application/octet-stream')))

            res = self._rdmc.app.post_handler(str(urltosend), data, response=True, \
                 headers={'Cookie': 'sessionKey=' + sessionkey})

            if res.status != 200:
                return ReturnCodes.FAILED_TO_UPLOAD_COMPONENT
            else:
                sys.stdout.write("Component " + filename + \
                                                " uploaded successfully\n")

            if not self.wait_for_state_change():
                # Failed to upload the component.
                raise UploadError("Error while processing the component.")


        return ReturnCodes.SUCCESS

    def wait_for_state_change(self, wait_time=420):
        """ Wait for the iLO UpdateService to a move to terminal state.
        :param options: command line options
        :type options: list.
        :param wait_time: time to wait on upload
        :type wait_time: int.
        """
        total_time = 0
        spinner = ['|', '/', '-', '\\']
        state = ""
        sys.stdout.write("Waiting for iLO UpdateService to finish processing the component\n")

        while total_time < wait_time:
            state, _ = self.get_update_service_state()

            if state == "ERROR":
                return False
            elif state != "COMPLETED" and state != "IDLE" and state != "COMPLETE":
                # Lets try again after 8 seconds
                count = 0

                # fancy spinner
                while count <= 32:
                    sys.stdout.write('Updating: %s\r' % spinner[count % 4])
                    time.sleep(0.25)
                    count += 1

                total_time += 8
            else:
                break

        if total_time > wait_time:
            raise TimeOutError("UpdateService in " + state + " state for " + str(wait_time) + "s")

        return True

    def get_update_service_state(self):
        """ Get the current UpdateService state

        :param options: command line options
        :type options: list.
        """
        path = "/redfish/v1/UpdateService"
        results = self._rdmc.app.get_handler(path, service=True, silent=True)

        if results and results.status == 200 and results.dict:
            output = results.dict

            if self._rdmc.opts.verbose:
                sys.stdout.write("UpdateService state = " + \
                                 (output['Oem']['Hpe']['State']).upper() + "\n")

            return (output['Oem']['Hpe']['State']).upper(), results.dict
        else:
            return 'UNKNOWN', {}

    def findcompsig(self, comppath):
        """Try to find compsig if not included
        :param comppath: Path of file to find compsig for.
        :type comppath: str.
        """
        compsig = ''

        cutpath = comppath.split(os.sep)
        _file = cutpath[-1]
        _file_rev = _file[::-1]
        filename = _file[:((_file_rev.find('.')) * -1) - 1]

        try:
            location = os.sep.join(cutpath[:-1])
        except:
            location = os.curdir

        if not location:
            location = os.curdir

        files = [f for f in os.listdir(location) if os.path.isfile(os.path.join(location, f))]

        for filehndl in files:
            if filehndl.startswith(filename) and filehndl.endswith('.compsig'):
                sys.stdout.write('Compsig found for file.\n')

                if location != '.':
                    compsig = location + os.sep + filehndl
                else:
                    compsig = filehndl

                break

        return compsig

    def uploadlocally(self, filelist, options=None):
        """Upload component locally

        :param filelist: List of files to upload.
        :type filelist: list.
        :param options: command line options
        :type options: list.
        """
        try:
            dll = self._rdmc.app.current_client.connection._conn.channel.dll
            dll.uploadComponent.argtypes = [c_char_p, c_char_p, c_char_p, c_uint32]
            dll.uploadComponent.restype = c_int

            multiupload = False

            for item in filelist:

                ilo_upload_filename = item[0]
                componentpath = item[1]
                compsigpath = item[2]

                if not compsigpath:
                    compsigpath = self.findcompsig(componentpath)

                _, filename = os.path.split(componentpath)

                # 0x00000001  // FUM_WRITE_NAND
                # 0x00000002  // FUM_USE_NAND
                # 0x00000004  // FUM_NO_FLASH
                # 0x00000008  // FUM_FORCE
                # 0x00000010  // FUM_SIDECAR
                # 0x00000020  // FUM_APPEND

                if not compsigpath and options.update_target:
                    # Just update the firmware
                    dispatchflag = ctypes.c_uint32(0x00000000)
                elif not compsigpath and not options.update_target and \
                                                    options.update_repository:
                    # uploading a secuare flash binary image onto the NAND
                    dispatchflag = ctypes.c_uint32(0x00000001 | 0x00000004)
                else:
                    # Uploading a component with a side car file.
                    dispatchflag = ctypes.c_uint32(0x00000001 | 0x00000004 | 0x00000010)

                if multiupload:
                    # For second upload to append if the component is > 32MB in size
                    dispatchflag = ctypes.c_uint32(0x00000001 | 0x00000004 | \
                                                        0x00000010 | 0x00000020)

                sys.stdout.write("Uploading component " + filename + "\n")
                ret = dll.uploadComponent(\
                  ctypes.create_string_buffer(compsigpath.encode('utf-8')),
                  ctypes.create_string_buffer(componentpath.encode('utf-8')),
                  ctypes.create_string_buffer(ilo_upload_filename), dispatchflag)

                if ret != 0:
                    sys.stdout.write("Component " + filename + " upload failed\n")

                    return ReturnCodes.FAILED_TO_UPLOAD_COMPONENT
                else:
                    sys.stdout.write("Component " + filename + " uploaded successfully\n")

                multiupload = True

        except Exception as excep:
            raise excep

        return ReturnCodes.SUCCESS

    def uploadcommandvalidation(self, options):
        """ upload command method validation function

        :param options: command line options
        :type options: list.
        """
        inputline = list()
        client = None

        if not options.component:
            raise InvalidCommandLineError("The component option is required"\
                                          " for this operation.")

        if not os.path.exists(options.component):
            raise InvalidPathError("Component not found at specified path.")

        if options.componentsig  and (not os.path.exists(options.componentsig)):
            raise InvalidCommandLineError("Component signature not found.")

        try:
            client = self._rdmc.app.current_client
        except:
            if options.user or options.password or options.url:
                if options.url:
                    inputline.extend([options.url])
                if options.user:
                    if options.encode:
                        options.user = Encryption.decode_credentials(options.user)
                    inputline.extend(["-u", options.user])
                if options.password:
                    if options.encode:
                        options.password = Encryption.decode_credentials(options.password)
                    inputline.extend(["-p", options.password])
                if options.https_cert:
                    inputline.extend(["--https", options.https_cert])
            else:
                if self._rdmc.app.config.get_url():
                    inputline.extend([self._rdmc.app.config.get_url()])
                if self._rdmc.app.config.get_username():
                    inputline.extend(["-u", self._rdmc.app.config.get_username()])
                if self._rdmc.app.config.get_password():
                    inputline.extend(["-p", self._rdmc.app.config.get_password()])
                if self._rdmc.app.config.get_ssl_cert():
                    inputline.extend(["--https", self._rdmc.app.config.get_ssl_cert()])

        if not inputline and not client:
            sys.stdout.write('Local login initiated...\n')
        if not client or inputline:
            self.lobobj.loginfunction(inputline)

    def definearguments(self, customparser):
        """ Define command line argument for the upload command

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        add_login_arguments_group(customparser)

        customparser.add_argument(
            '-j',
            '--json',
            dest='json',
            action="store_true",
            help="Optionally include this flag if you wish to change the"\
            " displayed output to JSON format. Preserving the JSON data"\
            " structure makes the information easier to parse.",
            default=False
        )
        customparser.add_argument(
            '--logout',
            dest='logout',
            action="store_true",
            help="Optionally include the logout flag to log out of the"\
            " server after this command is completed. Using this flag when"\
            " not logged in will have no effect",
            default=None,
        )
        customparser.add_argument(
            '--component',
            dest='component',
            help="""Component or binary file path to upload to the update service.""",
            default="",
        )
        customparser.add_argument(
            '--compsig',
            dest='componentsig',
            help='Component signature file path needed by iLO to authenticate the '\
            'component file. If not provided will try to find the ' \
            'signature file from component file path.',
            default="",
        )
        customparser.add_argument(
            '--forceupload',
            dest='forceupload',
            action="store_true",
            help='Add this flag to force upload components with the same name '\
                    'already on the repository.',
            default=False,
        )
        customparser.add_argument(
            '--update_repository',
            dest='update_repository',
            action="store_false",
            help='Add this flag to skip uploading component/binary to the '\
            'iLO Repository.',
            default=True,
        )
        customparser.add_argument(
            '--update_target',
            dest='update_target',
            action="store_true",
            help='Add this flag if you wish to flash the component/binary.',
            default=False,
        )
