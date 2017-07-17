###
# Copyright 2017 Hewlett Packard Enterprise, Inc. All rights reserved.
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
""" Exit Command for rdmc """

import sys

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS

class ExitCommand(RdmcCommandBase):
    """ Exit class to handle exiting from interactive mode """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='exit',\
            usage='exit\n\n\tRun to exit from the interactive shell\n\t' \
            'example: exit',\
            summary='Exits from the interactive shell.',\
            aliases=['quit'])

        self._rdmc = rdmcObj
        self.logoutobj = rdmcObj.commandsDict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """If an argument is present, print help else exit

        :param line: command line input
        :type line: string.
        """
        try:
            (_, args) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        if args is None or len(args) == 0 or not line:
            self.logoutobj.run("")
            sys.stdout.write(u'Bye for now\n')

            #System exit
            sys.exit(ReturnCodes.SUCCESS)
        else:
            sys.stderr.write("Exit command does not take any parameters.\n")
            raise InvalidCommandLineErrorOPTS("Invalid command line arguments.")
