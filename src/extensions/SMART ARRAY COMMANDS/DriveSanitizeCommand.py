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
""" Drive Erase/ Sanitize Command for rdmc """

import sys

from optparse import OptionParser, SUPPRESS_HELP
from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, Encryption, \
                        InvalidCommandLineErrorOPTS

class DriveSanitizeCommand(RdmcCommandBase):
    """ Drive erase/sanitize command """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='drivesanitize',\
            usage='drivesanitize [OPTIONS]\n\n\tTo sanitize a physical drive ' \
                'by index.\n\texample: drivesanitize 1 --controller=1\n\n\tTo' \
                ' sanitize multiple drives by index.\n\texample: ' \
                'drivesanitize 1,2 --controller=1',\
            summary='Erase/Sanitizes physical drives',\
            aliases=['drivesanitize'],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)
        self.rebootobj = rdmcObj.commands_dict["RebootCommand"](rdmcObj)

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

        if options.encode and options.user and options.password:
            options.user = Encryption.decode_credentials(options.user)
            options.password = Encryption.decode_credentials(options.password)

        self.drivesanitizevalidation(options)

        self.selobj.selectfunction("SmartStorageConfig.")
        content = self._rdmc.app.get_save()

        if not args and not options.all:
            raise InvalidCommandLineError('You must include a physical drive ' \
                                                                'to sanitize.')
        elif not options.controller:
            raise InvalidCommandLineError('You must include a controller ' \
                                                                'to select.')
        else:
            if len(args) > 1:
                physicaldrives = args
            elif len(args) == 1:
                physicaldrives = args[0].replace(', ', ',').split(',')
            else:
                physicaldrives = None

            controllist = []

        if options.controller.isdigit() and not options.controller == '0':
            try:
                controllist.append(content[int(options.controller) - 1])
            except:
                pass
        else:
            for control in content:
                if options.controller.lower() == control["Location"].lower():
                    controllist.append(control)

        if not controllist:
            raise InvalidCommandLineError("Selected controller not " \
                                      "found in the current inventory list.")
        else:
            if self.sanitizedrives(controllist, physicaldrives, options.all):
                if options.reboot:
                    self.rebootobj.run("ColdBoot")
                    sys.stdout.write('Preparing for sanitization...\n')
                    self.monitorsanitization()
                else:
                    sys.stdout.write('Sanitization will occur on the next'\
                                                            ' system reboot.\n')
        #Return code
        return ReturnCodes.SUCCESS

    def sanitizedrives(self, controllist, drivelist, optall):
        """Gets drives ready for sanitization

        :param controllist: list of controllers
        :type controllist: list.
        :param drivelist: physical drives to sanitize
        :type drivelist: list.
        :param optall: flag for sanitizing all drives
        :type optall: bool.
        """
        sanitizedrivelist = []
        logicaldrivelist = []
        changes = False

        for controller in controllist:
            pdrivelist = [x['DataDrives'] for x in controller['LogicalDrives']]

            for plist in pdrivelist:
                for drive in plist:
                    logicaldrivelist.append(drive)

            if optall:
                sanitizedrivelist = [x['Location'] for x in \
                                    controller['PhysicalDrives']]
            else:
                for erasedrive in drivelist:
                    if erasedrive.isdigit():
                        erasedrive = int(erasedrive)

                    for idx, pdrive in enumerate(controller['PhysicalDrives']):
                        if erasedrive == idx+1:
                            if pdrive['Location'] in logicaldrivelist:
                                raise InvalidCommandLineError("Unable to" \
                                      " sanitize configured drive. Remove" \
                                      " any logical drive(s) associated " \
                                      "with drive %s and try again." % \
                                                        pdrive['Location'])

                            sys.stdout.write('Setting physical drive %s ' \
                                 'for sanitization\n' % pdrive['Location'])

                            sanitizedrivelist.append(pdrive['Location'])
                            break

            if sanitizedrivelist:
                changes = True
                contentsholder = {"Actions": [{"Action": "PhysicalDriveErase", \
                            "ErasePattern": "SanitizeRestrictedBlockErase", \
                            "PhysicalDriveList": sanitizedrivelist}], \
                                                "DataGuard": "Disabled"}

                self._rdmc.app.patch_handler(controller["@odata.id"], \
                                                                contentsholder)

        return changes

    def monitorsanitization(self):
        """ monitors sanitization percentage"""
        #TODO: Add code to give updates on sanitization

    def drivesanitizevalidation(self, options):
        """ drive sanitize validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        inputline = list()
        runlogin = False

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
                    inputline.extend(["-u", \
                                  self._rdmc.app.config.get_username()])
                if self._rdmc.app.config.get_password():
                    inputline.extend(["-p", \
                                  self._rdmc.app.config.get_password()])

        if inputline or not client:
            runlogin = True
            if not inputline:
                sys.stdout.write(u'Local login initiated...\n')

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
            help="""Use this flag to select the corresponding controller.""",
            default=None,
        )
        customparser.add_option(
            '--reboot',
            dest='reboot',
            help="""Include this flag to perform a coldboot command """ \
                """function after completion of operations and monitor """ \
                """sanitization.""",
            action="store_true",
            default=False,
        )
        customparser.add_option(
            '--all',
            dest='all',
            help="""Use this flag to sanitize all physical drives on a """ \
                """controller.""",
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
