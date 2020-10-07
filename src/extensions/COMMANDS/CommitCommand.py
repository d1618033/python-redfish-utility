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
""" Commit Command for RDMC """

import sys

from argparse import ArgumentParser, SUPPRESS

from redfish.ris.rmc_helper import NothingSelectedError

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, FailureDuringCommitError,\
                        NoChangesFoundOrMadeError, NoCurrentSessionEstablished

class CommitCommand(RdmcCommandBase):
    """ Constructor """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='commit',\
            usage='commit [OPTIONS]\n\n\tRun to apply all changes made during' \
                    ' the current session\n\texample: commit',\
            summary='Applies all the changes made during the current session.',\
            aliases=[],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)

        #remove reboot option if there is no reboot command
        try:
            self.rebootobj = rdmcObj.commands_dict["RebootCommand"](rdmcObj)
        except KeyError:
            self.parser.remove_option('--reboot')

    def commitfunction(self, options=None):
        """ Main commit worker function

        :param options: command line options
        :type options: list.
        """
        self.commitvalidation()

        sys.stdout.write("Committing changes...\n")

        if options:
            if options.biospassword:
                self._rdmc.app.current_client.bios_password = options.biospassword
        try:
            failure = False
            commit_opp = self._rdmc.app.commit()
            for path in commit_opp:
                if self._rdmc.opts.verbose:
                    sys.stdout.write('Changes are being made to path: %s\n' % path)
                if commit_opp.next():
                    failure = True
        except NothingSelectedError:
            raise NoChangesFoundOrMadeError("No changes found or made during commit operation.")
        else:
            if failure:
                raise FailureDuringCommitError('One or more types failed to commit. Run the '\
                                               'status command to see uncommitted data. '\
                                               'if you wish to discard failed changes refresh the '\
                                               'type using select with the --refresh flag.')

        if options.reboot:
            self.rebootobj.run(options.reboot)
            self.logoutobj.run("")

    def run(self, line):
        """ Wrapper function for commit main function

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

        self.commitfunction(options)

        #Return code
        return ReturnCodes.SUCCESS

    def commitvalidation(self):
        """ Commit method validation function """

        try:
            _ = self._rdmc.app.current_client
        except:
            raise NoCurrentSessionEstablished("Please login and make setting" \
                                      " changes before using commit command.")

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return
        customparser.add_argument(
            '-u',
            '--user',
            dest='user',
            help="Pass this flag along with the password flag if you are"\
            "running in local higher security modes.""",
            default=None
        )
        customparser.add_argument(
            '-p',
            '--password',
            dest='password',
            help="Pass this flag along with the username flag if you are"\
            "running in local higher security modes.""",
            default=None
        )
        customparser.add_argument(
            '--reboot',
            dest='reboot',
            help="Use this flag to perform a reboot command function after"\
            " completion of operations.  For help with parameters and"\
            " descriptions regarding the reboot flag, run help reboot.",
            default=None
        )
        customparser.add_argument(
            '--biospassword',
            dest='biospassword',
            help="Select this flag to input a BIOS password. Include this"\
            " flag if second-level BIOS authentication is needed for the"\
            " command to execute. This option is only used on Gen 9 systems.",
            default=None
        )
        customparser.add_argument(
            '-e',
            '--enc',
            dest='encode',
            action='store_true',
            help=SUPPRESS,
            default=False
        )
