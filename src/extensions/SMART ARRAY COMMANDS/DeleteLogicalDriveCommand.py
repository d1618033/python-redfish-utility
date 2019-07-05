###
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
###

# -*- coding: utf-8 -*-
""" Delete Logical Drive Command for rdmc """

import sys
from collections import OrderedDict

from optparse import OptionParser, SUPPRESS_HELP

from six.moves import input

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, Encryption, \
                    InvalidCommandLineErrorOPTS, NoContentsFoundForOperationError

def controller_parse(option, opt_str, value, parser):
    """ Controller Option Parsing

        :param option: command line option
        :type option: attributes
        :param opt_str: parsed option string
        :type opt_str: string
        :param value: parsed option value
        :type value: attribute
        :param parser: OptionParser instance
        :type parser: object
    """
    setattr(parser.values, option.dest, [])
    use_slot = False
    use_indx = False
    for _opt in value.split(','):
        if _opt.isdigit() and not use_slot:
            use_indx = True
            parser.values.controller.append(int(_opt))
        elif "slot" in _opt.lower() and not use_indx:
            use_slot = True
            parser.values.controller.append((_opt.replace('\"', '')).strip())
        else:
            raise InvalidCommandLineErrorOPTS("An invalid option or combination of options were " \
                                              "used to specify a smart array controller.")
    if use_indx:
        parser.values.controller.sort()

class DeleteLogicalDriveCommand(RdmcCommandBase):
    """ Delete logical drive command """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='deletelogicaldrive',\
            usage='deletelogicaldrive [OPTIONS]\n\n\tTo delete a logical ' \
                'drive a controller by index.\n\texample: deletelogicaldrive ' \
                '1 --controller=1\n\n\tTo delete multiple logical drives by ' \
                'index.\n\texample: deletelogicaldrive 1,2 --controller=1' \
                '\n\n\tTo delete all logical drives on a controller.\n\t' \
                'example: deletelogicaldrive --controller=1 --all\n\n\t' \
                'NOTE: Slot position may be used to reference a controller rather than an index.' \
                '\n\n\tNOTE: You can also delete logical drives by \"VolumeUniqueIdentifier\".' \
                '\n\n\tNOTE: You can also delete logical drives by \"LogicalDriveName\".', \
            summary='Deletes logical drives from the selected controller.', \
            aliases=['deletelogicaldrive'],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)

    def run(self, line):
        """ Main disk inventory worker function

        :param line: command line input
        :type line: string.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.deletelogicaldrivevalidation(options)

        if not args and not options.all:
            raise InvalidCommandLineError('You must include a logical drive to delete.')
        elif not options.controller:
            raise InvalidCommandLineError('You must include a controller to select.')
        else:
            if len(args) > 1:
                logicaldrives = args
            elif len(args) == 1:
                logicaldrives = args[0].replace(', ', ',').split(',')
            else:
                logicaldrives = None

        self.selobj.selectfunction("SmartStorageConfig.")
        content = OrderedDict()
        for controller in self._rdmc.app.getprops():
            try:
                content[int(controller.get('Location', None).split(' ')[-1])] = controller
            except (AttributeError, KeyError):
                pass

        controldict = {}
        use_slot = False
        use_indx = False

        for _opt in options.controller:
            found = False
            for pos, control in enumerate(content):
                if isinstance(_opt, int) and not use_slot:
                    if pos == (_opt - 1):
                        controldict[_opt] = content[control]
                        found = True
                        use_indx = True
                elif _opt.lower() == content[control]["Location"].lower() and not use_indx:
                    controldict[int(content[control]["Location"].split(' ')[-1])] = content[control]
                    found = True
                    use_slot = True
                if found:
                    break

            if not found:
                sys.stderr.write("\nController \'%s\' not found in the current inventory list.\n" %\
                                    _opt)

        self.deletelogicaldrives(controldict, logicaldrives, options.all, options.force)

        #Return code
        return ReturnCodes.SUCCESS

    def deletelogicaldrives(self, controldict, drivelist, allopt, force):
        """Gets logical drives ready for deletion

        :param controldict: ordered dictionary of controllers
        :type controldict: dictionary
        :param drivelist: logical drives to delete
        :type drivelist: list.
        :param allopt: flag for deleting all logical drives
        :type allopt: bool.
        """

        for controller in controldict:
            changes = False

            numdrives = len(controldict[controller]['LogicalDrives'])
            deletecount = 0

            if allopt:
                controldict[controller]['LogicalDrives'] = []
                controldict[controller]['DataGuard'] = "Disabled"
                self.lastlogicaldrive(controldict[controller])
                changes = True
            else:
                for deldrive in drivelist:
                    found = False

                    if deldrive.isdigit():
                        deldrive = int(deldrive)

                    for idx, ldrive in enumerate(controldict[controller]['LogicalDrives']):
                        if deldrive == ldrive['VolumeUniqueIdentifier'] or deldrive == idx+1 or \
                        deldrive == ldrive['LogicalDriveName']:
                            if not force:
                                while True:
                                    ans = input("Are you sure you would"\
                                            " like to continue deleting drive"\
                                            ' %s? (y/n)' % ldrive['LogicalDriveName'])

                                    if ans.lower() == 'y':
                                        break
                                    elif ans.lower() == 'n':
                                        sys.stdout.write("Stopping command without "\
                                                "deleting logical drive.\n")
                                        return
                            sys.stdout.write('Setting logical drive %s ' \
                                             'for deletion\n' % ldrive['LogicalDriveName'])

                            controldict[controller]['LogicalDrives'][idx]['Actions'] = \
                                        [{"Action": "LogicalDriveDelete"}]

                            controldict[controller]['DataGuard'] = "Permissive"
                            deletecount += 1

                            changes = True
                            found = True
                            break

                    if not found:
                        raise NoContentsFoundForOperationError('Logical '\
                                        'drive %s not found.'% str(deldrive))

                if deletecount == numdrives:
                    self.lastlogicaldrive(controldict[controller])

            if changes:
                self._rdmc.app.put_handler(controldict[controller]["@odata.id"], \
                        controldict[controller],\
                        headers={'If-Match': self.getetag(controldict[controller]['@odata.id'])})
                self._rdmc.app.reloadmonolith(controldict[controller]["@odata.id"])

    def lastlogicaldrive(self, controller):
        """Special case that sets required properties after last drive deletion

        :param controller: controller change settings on
        :type controller: dict.
        """
        changelist = ['PredictiveSpareRebuild', 'SurfaceScanAnalysisPriority', \
                  'FlexibleLatencySchedulerSetting', 'DegradedPerformanceOptimization', \
                  'CurrentParallelSurfaceScanCount', 'SurfaceScanAnalysisDelaySeconds', \
                  'MonitorAndPerformanceAnalysisDelaySeconds', \
                  'InconsistencyRepairPolicy', 'DriveWriteCache', \
                  'ExpandPriority', 'EncryptionEULA', 'NoBatteryWriteCache', \
                  'ReadCachePercent', 'WriteCacheBypassThresholdKiB', \
                  'RebuildPriority', 'QueueDepth', 'ElevatorSort']

        for item in changelist:
            if item in list(controller.keys()):
                controller[item] = None

    def getetag(self, path):
        """ get etag from path """
        etag = None
        instance = self._rdmc.app.current_client.monolith.path(path)
        if instance:
            etag = instance.resp.getheader('etag') if 'etag' in instance.resp.getheaders() \
                                            else instance.resp.getheader('ETag')
        return etag

    def deletelogicaldrivevalidation(self, options):
        """ delete logical drive validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        inputline = list()
        runlogin = False

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

        if inputline or not client:
            runlogin = True
            if not inputline:
                sys.stdout.write('Local login initiated...\n')

        if runlogin:
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
            help="""If you are not logged in yet, including this flag along""" \
                """ with the password and URL flags can be used to log into""" \
                """ a server in the same command.""",
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
            '--controller',
            dest='controller',
            action='callback',
            callback=controller_parse,
            help="""Use this flag to select the corresponding controller "\
                "using either the slot number or index.""",
            type="string",
            default=[],
        )
        customparser.add_option(
            '--all',
            dest='all',
            help="""Use this flag to delete all logical drives on a """ \
                """controller.""",
            action="store_true",
            default=False,
        )
        customparser.add_option(
            '--force',
            dest='force',
            help="""Use this flag to override the "are you sure?" text when """ \
                """deleting a logical drive.""",
            action="store_true",
            default=False,
        )
        customparser.add_option(
            '-e',
            '--enc',
            dest='encode',
            action='store_true',
            help=SUPPRESS_HELP,
            default=False,
        )
