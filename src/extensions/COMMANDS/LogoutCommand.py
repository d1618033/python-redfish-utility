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
""" Logout Command for RDMC """

import sys

from optparse import OptionParser
from rdmc_base_classes import RdmcCommandBase

from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS

class LogoutCommand(RdmcCommandBase):
    """ Constructor """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='logout',\
            usage='logout\n\n\tRun to end the current session and disconnect' \
                    ' from the server\n\texample: logout',\
            summary='Ends the current session and disconnects from the' \
                    ' server.',\
            aliases=[],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj

    def logoutfunction(self, line):
        """ Main logout worker function

        :param line: command line input
        :type line: string.
        """
        try:
            (_, _) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self._rdmc.app.logout("")

    def run(self, line):
        """ Wrapper function for main logout function

        :param line: command line input
        :type line: string.
        """
        try:
            sys.stdout.write(u"Logging session out.\n")
            self.logoutfunction(line)
        except Exception, excp:
            raise excp

        #Return code
        return ReturnCodes.SUCCESS

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

