###
# Copyright 2019 Hewlett Packard Enterprise, Inc. All rights reserved.
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
""" Help Command for RDMC """

import sys

from argparse import ArgumentParser
from rdmc_base_classes import RdmcCommandBase, RdmcOptionParser
from rdmc_helper import ReturnCodes, InvalidCommandLineError, InvalidCommandLineErrorOPTS

class HelpCommand(RdmcCommandBase):
    """ Constructor """
    def __init__(self, **kwargs):
        RdmcCommandBase.__init__(self,\
            name='help',\
            usage='help [COMMAND]\n\n\tFor more detailed command descriptions' \
                    ' use the help command feature\n\texample: help login',\
            summary='Displays command line syntax and help menus for individual commands.'\
                    ' Example: help login',\
            aliases=[],\
            argparser=ArgumentParser())
        self.config_required = False
        self._rdmc = None
        if 'rdmc' in kwargs:
            self._rdmc = kwargs['rdmc']

    def run(self, line):
        """ Wrapper function for help main function

        :param line: command line input
        :type line: string.
        """
        try:
            (_, args) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        if not args or not line:
            RdmcOptionParser().print_help()
            if self._rdmc:
                cmddict = self._rdmc.get_commands()
                sorted_keys = sorted(list(cmddict.keys()))

                for key in sorted_keys:
                    if key[0] == '_':
                        continue
                    else:
                        sys.stdout.write('\n%s\n' % key)

                    for cmd in cmddict[key]:
                        cmd.print_summary()
        else:
            if self._rdmc:
                cmddict = self._rdmc.get_commands()
                sorted_keys = list(cmddict.keys())

                for key in sorted_keys:
                    for cmd in cmddict[key]:
                        if cmd.ismatch(args[0]):
                            cmd.print_help()
                            return ReturnCodes.SUCCESS

                raise InvalidCommandLineError("Command '%s' not found." % args[0])
        #Return code
        return ReturnCodes.SUCCESS
