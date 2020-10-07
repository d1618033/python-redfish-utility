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
""" Factory Reset Controller Command for rdmc """

import sys

from argparse import ArgumentParser
from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group, login_select_validation, \
                                logout_routine
from rdmc_helper import ReturnCodes, InvalidCommandLineError, InvalidCommandLineErrorOPTS, \
                        Encryption

class FactoryResetControllerCommand(RdmcCommandBase):
    """ Factory reset controller command """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='factoryresetcontroller',\
            usage='factoryresetcontroller [OPTIONS]\n\n\tRun without ' \
                'arguments for the current controller options.\n\texample: ' \
                'factoryresetcontroller\n\n\tTo factory reset a controller ' \
                'by index.\n\texample: factoryresetcontroller --controller=2' \
                '\n\texample: factoryresetcontroller --controller="Slot1" ',\
            summary='Factory resets a controller by index or location.',\
            aliases=['factoryresetcontroller'],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)

    def run(self, line):
        """ Main disk inventory worker function

        :param line: command line input
        :type line: string.
        """
        try:
            (options, _) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.frcontrollervalidation(options)

        self.selobj.selectfunction("SmartStorageConfig.")
        content = self._rdmc.app.getprops()

        if options.controller:
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
        for controller in controllist:
            contentsholder = {"Actions": [{"Action": "FactoryReset"}], \
                                                "DataGuard": "Disabled"}
            self._rdmc.app.patch_handler(controller["@odata.id"], contentsholder)

        for idx, val in enumerate(content):
            sys.stdout.write("[%d]: %s\n" % (idx + 1, val["Location"]))

        logout_routine(self, options)
        #Return code
        return ReturnCodes.SUCCESS

    def frcontrollervalidation(self, options):
        """ Factory reset controller validation function

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
            help="""Use this flag to select the corresponding controller """\
                """using either the slot number or index.""",
            default=None,
        )
