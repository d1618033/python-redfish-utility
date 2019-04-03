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
""" Login Command for RDMC """

import sys
import getpass

from optparse import OptionParser, SUPPRESS_HELP

import redfish.ris

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
                            InvalidCommandLineErrorOPTS, PathUnavailableError, Encryption

class LoginCommand(RdmcCommandBase):
    """ Constructor """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='login',\
            usage='login [URL] [OPTIONS] \n\n\tTo login' \
                    ' remotely run using iLO url and iLO credentials' \
                    '\n\texample: login <iLO url/hostname> -u <iLO username> '\
                    '-p <iLO password>\n\n\tTo login on a local server run' \
                    ' without arguments\n\texample: login',\
            summary='Connects to a server, establishes a secure session,'\
                    ' and discovers data from iLO.',\
            aliases=[],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self.url = None
        self.username = None
        self.password = None
        self.biospassword = None
        self._rdmc = rdmcObj
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """ wrapper function for main login function

        :param line: command line input
        :type line: string.
        """
        try:
            self.loginfunction(line)

            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS

            if not self._rdmc.app.current_client.monolith._visited_urls:
                self.logoutobj.run("")
                raise PathUnavailableError("The path specified by the --path flag is unavailable.")
        except Exception:
            raise

        #Return code
        return ReturnCodes.SUCCESS

    def loginfunction(self, line, skipbuild=None):
        """ Main worker function for login class

        :param line: entered command line
        :type line: list.
        :param skipbuild: flag to determine if monolith should be build
        :type skipbuild: boolean.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.loginvalidation(options, args)

        proxy = self._rdmc.opts.proxy if self._rdmc.opts.proxy else \
                                        self._rdmc.app.config.get_proxy()

        self._rdmc.app.login(username=self.username, \
                      password=self.password, base_url=self.url, \
                      verbose=self._rdmc.opts.verbose, path=options.path, skipbuild=skipbuild,\
                      includelogs=options.includelogs, biospassword=self.biospassword, \
                      is_redfish=self._rdmc.opts.is_redfish, proxy=proxy)

        # Warning for cache enabled, since we save session in plain text
        if not self._rdmc.encoding:
            sys.stdout.write("WARNING: Cache is activated. Session keys are stored in plaintext.\n")

        if self._rdmc.opts.debug:
            sys.stdout.write("WARNING: Logger is activated. Logging is stored in plaintext.\n")

        if options.selector:
            try:
                self._rdmc.app.select(selector=options.selector)

                if self._rdmc.opts.verbose:
                    sys.stdout.write("Selected option: '%s'" % options.selector)
                    sys.stdout.write('\n')
            except Exception as excp:
                raise redfish.ris.InstanceNotFoundError(excp)

    def loginvalidation(self, options, args):
        """ Login helper function for login validations

        :param options: command line options
        :type options: list.
        :param args: command line arguments
        :type args: list.
        """
        # Fill user name/password from config file
        if not options.user:
            options.user = self._rdmc.app.config.get_username()
        if not options.password:
            options.password = self._rdmc.app.config.get_password()
        if not options.biospassword:
            options.biospassword = self._rdmc.app.config.get_bios_password()

        # Password and user name validation
        if options.user and not options.password:
            # Option for interactive entry of password
            tempinput = getpass.getpass()

            if tempinput:
                options.password = tempinput
            else:
                raise InvalidCommandLineError("Empty or invalid password was entered.")

        if options.user:
            self.username = options.user

        if options.password:
            self.password = options.password

        if options.encode:
            self.username = Encryption.decode_credentials(self.username)
            self.password = Encryption.decode_credentials(self.password)

        if options.biospassword:
            self.biospassword = options.biospassword

        # Assignment of url in case no url is entered
        self.url = 'blobstore://.'

        if args:
            # Any argument should be treated as an URL
            self.url = args[0]

            # Verify that URL is properly formatted for https://
            if "https://" not in self.url:
                self.url = "https://" + self.url
            if not self.username or not self.password:
                raise InvalidCommandLineError("Empty username or password was entered.")
        else:
            # Check to see if there is a URL in config file
            if self._rdmc.app.config.get_url():
                self.url = self._rdmc.app.config.get_url()

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

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
            '--includelogs',
            dest='includelogs',
            action="store_true",
            help="Optionally include logs in the data retrieval process.",
            default=False,
        )
        customparser.add_option(
            '--selector',
            dest='selector',
            help="Optionally include this flag to select a type to run"\
             " the current command on. Use this flag when you wish to"\
             " select a type without entering another command, or if you"\
              " wish to work with a type that is different from the one"\
              " you currently have selected.",
            default=None,
        )
        customparser.add_option(
            '--path',
            dest='path',
            help="Optionally set a starting point for data collection during"\
            " login. If you do not specify a starting point, the default path"\
            " will be /redfish/v1/. Note: The path flag can only be specified"\
            " at the time of login. Warning: Only for advanced users, and"\
            " generally not needed for normal operations.",
            default=None,
        )
        customparser.add_option(
            '--biospassword',
            dest='biospassword',
            help="Select this flag to input a BIOS password. Include this"\
            " flag if second-level BIOS authentication is needed for the"\
            " command to execute. This option is only used on Gen 9 systems.",
            default=None,
        )
        customparser.add_option(
            '-e',
            '--enc',
            dest='encode',
            action='store_true',
            help=SUPPRESS_HELP,
            default=False,
        )
