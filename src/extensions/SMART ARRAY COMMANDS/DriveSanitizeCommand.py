###
# Copyright 2020 Hewlett Packard Enterprise, Inc. All rights reserved.
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

from argparse import ArgumentParser
from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group, login_select_validation, \
                                logout_routine
from rdmc_helper import ReturnCodes, InvalidCommandLineError, InvalidCommandLineErrorOPTS, \
                        Encryption, NoContentsFoundForOperationError

class DriveSanitizeCommand(RdmcCommandBase):
    """ Drive erase/sanitize command """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='drivesanitize',\
            usage='drivesanitize [OPTIONS]\n\n\tTo sanitize a physical drive ' \
                'by index.\n\texample: drivesanitize 1 --controller=1\n\n\tTo' \
                ' sanitize multiple drives by index.\n\texample: ' \
                'drivesanitize 1,2 --controller=1 \n\texample: drivesanitize ' \
                '1,2 --controller="Slot1"',\
            summary='Erase/Sanitize physical drive(s)',\
            aliases=['drivesanitize'],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)
        self.rebootobj = rdmcObj.commands_dict["RebootCommand"](rdmcObj)

    def run(self, line):
        """ Main disk inventory worker function

        :param line: command line input
        :type line: string.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.drivesanitizevalidation(options)

        self.selobj.selectfunction("SmartStorageConfig.")
        content = self._rdmc.app.getprops()

        if not args and not options.all:
            raise InvalidCommandLineError('You must include a physical drive to sanitize.')
        elif not options.controller:
            raise InvalidCommandLineError('You must include a controller to select.')
        else:
            if len(args) > 1:
                physicaldrives = args
            elif len(args) == 1:
                physicaldrives = args[0].replace(', ', ',').split(',')
            else:
                physicaldrives = None

            controllist = []

        try:
            if options.controller.isdigit():
                if int(options.controller) > 0:
                    controllist.append(content[int(options.controller) - 1])
            else:
                slotcontrol = options.controller.lower().strip('\"').split('slot')[-1].lstrip()
                for control in content:
                    if slotcontrol.lower() == control["Location"].lower().split('slot')[-1].lstrip():
                        controllist.append(control)
            if not controllist:
                raise InvalidCommandLineError("")
        except InvalidCommandLineError:
            raise InvalidCommandLineError("Selected controller not found in the current inventory "\
                                          "list.")

        if self.sanitizedrives(controllist, physicaldrives, options.all):
            if options.reboot:
                self.rebootobj.run("ColdBoot")
                sys.stdout.write('Preparing for sanitization...\n')
                self.monitorsanitization()
            else:
                sys.stdout.write('Sanitization will occur on the next system reboot.\n')

        logout_routine(self, options)
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
                sanitizedrivelist = [x['Location'] for x in controller['PhysicalDrives']]
            else:
                for erasedrive in drivelist:
                    if erasedrive.isdigit():
                        erasedrive = int(erasedrive)

                    try:
                        for idx, pdrive in enumerate(controller['PhysicalDrives']):
                            if erasedrive == idx+1 or erasedrive == str(pdrive["Location"]):
                                if pdrive['Location'] in logicaldrivelist:
                                    raise InvalidCommandLineError("Unable to" \
                                          " sanitize configured drive. Remove" \
                                          " any logical drive(s) associated " \
                                          "with drive %s and try again." % pdrive['Location'])

                                sys.stdout.write('Setting physical drive %s ' \
                                     'for sanitization\n' % pdrive['Location'])

                                sanitizedrivelist.append(pdrive['Location'])
                                break
                            elif idx not in pdrivelist and erasedrive not in str(drivelist):
                                raise InvalidCommandLineError("Selected drive %s could not " \
                                            "be found in the current drive list." % erasedrive)
                                break
                    except KeyError as excp:
                        raise NoContentsFoundForOperationError("The property \'%s\' is missing "\
                                                               "or invalid." % str(excp))

            if sanitizedrivelist:
                changes = True
                contentsholder = {"Actions": [{"Action": "PhysicalDriveErase", \
                            "ErasePattern": "SanitizeRestrictedBlockErase", \
                            "PhysicalDriveList": sanitizedrivelist}], "DataGuard": "Disabled"}

                self._rdmc.app.patch_handler(controller["@odata.id"], contentsholder)

        return changes

    def monitorsanitization(self):
        """ monitors sanitization percentage"""
        #TODO: Add code to give updates on sanitization

    def drivesanitizevalidation(self, options):
        """ drive sanitize validation function

        :param options: command line options
        :type options: list.
        """
        login_select_validation(self, options)

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        add_login_arguments_group(customparser)

        customparser.add_argument(
            '--controller',
            dest='controller',
            help="""Use this flag to select the corresponding controller """ \
                """using either the slot number or index.""",
            default=None,
        )
        customparser.add_argument(
            '--reboot',
            dest='reboot',
            help="""Include this flag to perform a coldboot command """ \
                """function after completion of operations and monitor """ \
                """sanitization.""",
            action="store_true",
            default=False,
        )
        customparser.add_argument(
            '--all',
            dest='all',
            help="""Use this flag to sanitize all physical drives on a """ \
                """controller.""",
            action="store_true",
            default=False,
        )
