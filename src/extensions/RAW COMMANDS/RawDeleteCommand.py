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
""" RawDelete Command for rdmc """

import sys
import json

from argparse import ArgumentParser
from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group
from rdmc_helper import ReturnCodes, InvalidCommandLineError, Encryption, \
                                                    InvalidCommandLineErrorOPTS

class RawDeleteCommand(RdmcCommandBase):
    """ Raw form of the delete command """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='rawdelete',\
            usage='rawdelete [PATH] [OPTIONS]\n\n\tRun to to delete data from' \
                    ' the passed in path.\n\texample: rawdelete "/redfish/v1/' \
                    'Sessions/(session ID)"', \
            summary='Raw form of the DELETE command.',\
            aliases=['rawdelete'],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)

    def run(self, line):
        """ Main raw delete worker function

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

        headers = {}

        self.deletevalidation(options)

        if len(args) > 1:
            raise InvalidCommandLineError("Raw delete only takes 1 argument.\n")
        elif not args:
            raise InvalidCommandLineError("Missing raw delete input path.\n")

        if args[0].startswith('"') and args[0].endswith('"'):
            args[0] = args[0][1:-1]

        if options.expand:
            args[0] = args[0] + '?$expand=.'

        try:
            currentsess = self._rdmc.app.current_client.session_location
        except:
            currentsess = None

        if options.headers:
            extraheaders = options.headers.split(',')

            for item in extraheaders:
                header = item.split(':')

                try:
                    headers[header[0]] = header[1]
                except:
                    InvalidCommandLineError("Invalid format for --headers option.")

        if currentsess and (args[0] in currentsess):
            self._rdmc.app.logout()
            sys.stdout.write("Your session has been deleted.\nPlease log "\
                                        "back in if you wish to continue.\n")
        else:
            returnresponse = False

            if options.response or options.getheaders:
                returnresponse = True

            results = self._rdmc.app.delete_handler(args[0], \
                headers=headers, silent=options.silent, service=options.service)

            if returnresponse and results:
                if options.getheaders:
                    sys.stdout.write(json.dumps(dict(results.getheaders())) + "\n")

                if options.response:
                    sys.stdout.write(results.read)
            elif results.status == 404:
                return ReturnCodes.NO_CONTENTS_FOUND_FOR_OPERATION
            elif results.status != 200:
                return ReturnCodes.UI_CLI_USAGE_EXCEPTION

        #Return code
        return ReturnCodes.SUCCESS

    def deletevalidation(self, options):
        """ Raw delete validation function

        :param options: command line options
        :type options: list.
        """
        inputline = list()

        try:
            _ = self._rdmc.app.current_client
        except:
            if options.user or options.password or options.url:
                if options.url:
                    inputline.extend([options.url])
                if options.user:
                    if options.encode:
                        options.user = Encryption.decode_credentials(options.user)
                    inputline.extend(["-u", options.user])
                if options.password:
                    if options.encode:
                        options.password = Encryption.decode_credentials(options.password)
                    inputline.extend(["-p", options.password])
                if options.https_cert:
                    inputline.extend(["--https", options.https_cert])
            else:
                if self._rdmc.app.config.get_url():
                    inputline.extend([self._rdmc.app.config.get_url()])
                if self._rdmc.app.config.get_username():
                    inputline.extend(["-u", self._rdmc.app.config.get_username()])
                if self._rdmc.app.config.get_password():
                    inputline.extend(["-p", self._rdmc.app.config.get_password()])
                if self._rdmc.app.config.get_ssl_cert():
                    inputline.extend(["--https", self._rdmc.app.config.get_ssl_cert()])

            self.lobobj.loginfunction(inputline, skipbuild=True)

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        add_login_arguments_group(customparser)

        customparser.add_argument(
            '--response',
            dest='response',
            action="store_true",
            help="Use this flag to return the iLO response body.",
            default=False
        )
        customparser.add_argument(
            '--getheaders',
            dest='getheaders',
            action="store_true",
            help="Use this flag to return the iLO response headers.",
            default=False
        )
        customparser.add_argument(
            '--headers',
            dest='headers',
            help="Use this flag to add extra headers to the request."\
            "\t\t\t\t\t Usage: --headers=HEADER:VALUE,HEADER:VALUE",
            default=None,
        )
        customparser.add_argument(
            '--silent',
            dest='silent',
            action="store_true",
            help="""Use this flag to silence responses""",
            default=False,
        )
        customparser.add_argument(
            '--service',
            dest='service',
            action="store_true",
            help="""Use this flag to enable service mode and increase the function speed""",
            default=False,
        )
        customparser.add_argument(
            '--expand',
            dest='expand',
            action="store_true",
            help="""Use this flag to expand the path specified using the """\
                                            """expand notation '?$expand=.'""",
            default=False,
        )
