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
""" Smart Array Command for rdmc """

import sys

from optparse import OptionParser
from rdmc_base_classes import RdmcCommandBase, HARDCODEDLIST
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
                                                InvalidCommandLineErrorOPTS, UI

class SmartArrayCommand(RdmcCommandBase):
    """ Smart array command """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='smartarray',\
            usage='smartarray [OPTIONS]\n\n\tRun without arguments for the ' \
                'current list of smart array controllers.\n\texample: ' \
                'smartarray\n\n\tTo get more details on a specific controller '\
                'select it by index.\n\texample: smartarray --controller=2' \
                '\n\n\tTo get more details on a specific controller select ' \
                'it by location.\n\texample: smartarray --controller="slot 1"' \
                '\n\n\tIn order to get a list of all physical drives for the ' \
                'each controller.\n\texample: smartarray --physicaldrives' \
                '\n\n\tTo obtain details about physical drives for a ' \
                'specific controller.\n\texample: smartarray --controller=3 ' \
                '--physicaldrives\n\n\tTo obtain details about a specific ' \
                'drive for a specific controller.\n\texample: smartarray ' \
                '--controller=3 --pdrive=1\n\n\tIn order to get a list of ' \
                'all logical drives for the each controller.\n\texample: ' \
                'smartarray --logicaldrives\n\n\tTo obtain details about ' \
                'logical drives for a specific controller.\n\texample: ' \
                'smartarray --controller=3 --logicaldrives\n\n\tTo obtain ' \
                'details about a specific drive for a specific controller.' \
                '\n\texample: smartarray --controller=3 --ldrive=1',\
            summary='Discovers all storage controllers installed in the ' \
                    'server and managed by the SmartStorage.',\
            aliases=['smartarray'],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commandsDict["LoginCommand"](rdmcObj)
        self.getobj = rdmcObj.commandsDict["GetCommand"](rdmcObj)
        self.selobj = rdmcObj.commandsDict["SelectCommand"](rdmcObj)

    def run(self, line):
        """ Main smart array worker function

        :param line: command line input
        :type line: string.
        """
        try:
            (options, _) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.smartarrayvalidation(options)

        self.selobj.selectfunction("SmartStorageConfig")
        content = self._rdmc.app.get_save()

        if options.controller:
            self.selection_output(options, content)
        else:
            self.discovery_output(options, content)

        #Return code
        return ReturnCodes.SUCCESS

    def selection_output(self, options, content):
        """ Selection of output for smart array command

        :param options: command line options
        :type options: list.
        :param options: list of contents
        :type options: list.
        """
        controllist = []
        outputcontent = False

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
            for controller in controllist:
                if options.physicaldrives or options.pdrive:
                    outputcontent = True
                    self.get_drives(options, controller["PhysicalDrives"], \
                                                                physical=True)

                if options.logicaldrives or options.ldrive:
                    outputcontent = True
                    self.get_drives(options, controller["LogicalDrives"], \
                                                                logical=True)

                if not outputcontent:
                    for k in controller.keys():
                        if k.lower() in HARDCODEDLIST or '@odata' in k.lower():
                            del controller[k]

                    UI().print_out_json_ordered(controller)

    def discovery_output(self, options, content):
        """ Discovery of output for smart array command

        :param options: command line options
        :type options: list.
        :param options: list of contents
        :type options: list.
        """
        for idx, val in enumerate(content):
            sys.stdout.write("[%d]: %s\n" % (idx + 1, val["Location"]))

            if options.physicaldrives:
                self.get_drives(options, val["PhysicalDrives"], physical=True)

            if options.logicaldrives:
                self.get_drives(options, val["LogicalDrives"], logical=True)

    def get_drives(self, options, drives, physical=False, logical=False):
        """ Selection of output for smart array command

        :param options: command line options
        :type options: list.
        :param drives: list of drives
        :type drives: list.
        :param physical: options to enable physical drives
        :type physical: boolean.
        :param logical: options to enable logical drives
        :type logical: boolean.
        """
        if not options.pdrive and physical:
            sys.stdout.write("Physical Drives:\n")

        if not options.ldrive and logical:
            sys.stdout.write("Logical Drives:\n")

        if drives:
            if options.pdrive:
                driveloc = None

                if options.pdrive.isdigit():
                    try:
                        driveloc = drives[int(options.pdrive) - 1]["Location"]
                    except:
                        pass
                else:
                    for drive in drives:
                        if options.pdrive.lower() == drive["Location"].lower():
                            driveloc = drive["Location"]

                if not driveloc:
                    raise InvalidCommandLineError("Selected drive not " \
                                          "found in the current drives list.")
                else:
                    self.get_selected_drive(driveloc)
            elif options.ldrive:
                driveloc = None

                if options.ldrive.isdigit():
                    try:
                        driveloc = drives[int(options.ldrive) - 1]
                    except:
                        pass
                else:
                    for drive in drives:
                        if options.ldrive.lower() == \
                                        drive["VolumeUniqueIdentifier"].lower():
                            driveloc = drive

                if not driveloc:
                    raise InvalidCommandLineError("Selected drive not " \
                                          "found in the current drives list.")
                else:
                    UI().print_out_json_ordered(driveloc)
            else:
                for idx, drive in enumerate(drives):
                    if physical:
                        sys.stdout.write("[%d]: %s\n" % (idx + 1, \
                                                            drive["Location"]))
                    elif logical:
                        if not "VolumeUniqueIdentifier" in drive:
                            drivedata = "Pending drive"
                        else:
                            drivedata = drive["VolumeUniqueIdentifier"]

                        sys.stdout.write("[%d]: %s\n" % (idx + 1, drivedata))
        else:
            if physical:
                sys.stdout.write("No physical drives found.\n")
            elif logical:
                sys.stdout.write("No logical drives found.\n")

        sys.stdout.write("\n")

    def get_selected_drive(self, location):
        """ Function to get all selected drives

        :param location: list of all locations
        :type location: list.
        """
        self.selobj.selectfunction("HpSmartStorageDiskDrive.")

        for drive in self._rdmc.app.get_save():
            if drive["Location"] in location:
                for k in drive.keys():
                    if k.lower() in HARDCODEDLIST or '@odata' in k.lower():
                        del drive[k]

                UI().print_out_json_ordered(drive)

    def smartarrayvalidation(self, options):
        """ Smart array validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        inputline = list()
        runlogin = False

        try:
            client = self._rdmc.app.get_current_client()
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

        if len(inputline) or not client:
            runlogin = True
            if not len(inputline):
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
            '--controller',
            dest='controller',
            help="""Use this flag to select the corresponding controller.""",
            default=None,
        )
        customparser.add_option(
            '--physicaldrives',
            dest='physicaldrives',
            action="store_true",
            help="""Use this flag to return the physical drives for the """
            """controller selected.""",
            default=None,
        )
        customparser.add_option(
            '--logicaldrives',
            dest='logicaldrives',
            action="store_true",
            help="""Use this flag to return the logical drives for the """
            """controller selected.""",
            default=None,
        )
        customparser.add_option(
            '--pdrive',
            dest='pdrive',
            help="""Use this flag to select the corresponding physical disk.""",
            default=None,
        )
        customparser.add_option(
            '--ldrive',
            dest='ldrive',
            help="""Use this flag to select the corresponding logical disk.""",
            default=None,
        )
