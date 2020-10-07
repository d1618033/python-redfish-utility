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
""" Types Command for RDMC """

import sys

from argparse import ArgumentParser

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group, login_select_validation, \
                                logout_routine
from rdmc_helper import ReturnCodes, InvalidCommandLineError, InvalidCommandLineErrorOPTS

class TypesCommand(RdmcCommandBase):
    """ Constructor """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='types',\
            usage='types [TYPE] [OPTIONS]\n\n\tRun to display currently ' \
            'available selectable types\n\texample: types',\
            summary='Displays all selectable types within the currently logged in server.',\
            aliases=['types'],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)

    def typesfunction(self, line, returntypes=False):
        """ Main types worker function

        :param line: command line input
        :type line: string.
        :param returntypes: flag to determine if types should be printed
        :type returntypes: boolean.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.typesvalidation(options)

        if not args:
            typeslist = list()
            typeslist = sorted(set(self._rdmc.app.types(options.fulltypes)))

            if not returntypes:
                sys.stdout.write("Type options:")
                sys.stdout.write('\n')

                for item in typeslist:
                    sys.stdout.write(item)
                    sys.stdout.write('\n')
            else:
                return typeslist
        else:
            raise InvalidCommandLineError("The 'types' command does not take any arguments.")

        logout_routine(self, options)

    def run(self, line):
        """ Wrapper function for types main function

        :param line: command line input
        :type line: string.
        """
        self.typesfunction(line)

        #Return code
        return ReturnCodes.SUCCESS

    def typesvalidation(self, options):
        """ types method validation function

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
            '--fulltypes',
            dest='fulltypes',
            action='store_true',
            help="Optionally include this flag if you would prefer to "\
            "return the full type name instead of the simplified versions" \
            " (Redfish only option).",
            default=None
        )
