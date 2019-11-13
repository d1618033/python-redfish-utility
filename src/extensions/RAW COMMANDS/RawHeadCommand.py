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
""" RawHead Command for rdmc """

import sys
import json

from argparse import ArgumentParser

import redfish

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
                    InvalidCommandLineErrorOPTS, UI, Encryption

class RawHeadCommand(RdmcCommandBase):
    """ Raw form of the head command """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='rawhead',\
            usage='rawhead [PATH]\n\n\tRun to to retrieve data from the ' \
                'passed in path\n\texample: rawhead "/redfish/v1/systems/'\
                '(system ID)"',\
            summary='Raw form of the HEAD command.',\
            aliases=['rawhead'],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)

    def run(self, line):
        """ Main raw head worker function

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

        self.headvalidation(options)

        if len(args) > 1:
            raise InvalidCommandLineError("Raw head only takes 1 argument.\n")
        elif not args:
            raise InvalidCommandLineError("Missing raw head input path.\n")

        if args[0].startswith('"') and args[0].endswith('"'):
            args[0] = args[0][1:-1]

        results = self._rdmc.app.head_handler(args[0], silent=options.silent, \
											  service=options.service)

        content = None
        tempdict = dict()

        if results and results.status == 200:
            if results._http_response:
                content = results.getheaders()
            else:
                content = results._headers

            tempdict = dict(content)

            if options.filename:
                output = json.dumps(tempdict, indent=2, cls=redfish.ris.JSONEncoder, sort_keys=True)
                filehndl = open(options.filename[0], "w")
                filehndl.write(output)
                filehndl.close()

                sys.stdout.write("Results written out to '%s'.\n" % options.filename[0])
            else:
                if options.service:
                    sys.stdout.write("%s\n" % tempdict)
                else:
                    UI().print_out_json(tempdict)
        else:
            return ReturnCodes.NO_CONTENTS_FOUND_FOR_OPERATION

        #Return code
        return ReturnCodes.SUCCESS

    def headvalidation(self, options):
        """ Raw head validation function

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
            '--silent',
            dest='silent',
            action="store_true",
            help="""Use this flag to silence responses""",
            default=None,
        )
        customparser.add_argument(
            '--sessionid',
            dest='sessionid',
            help="Optionally include this flag if you would prefer to "\
            "connect using a session id instead of a normal login.",
            default=None
        )
        customparser.add_argument(
            '-f',
            '--filename',
            dest='filename',
            help="""Use the provided filename to perform operations.""",
            action="append",
            default=None,
        )
        customparser.add_argument(
            '--service',
            dest='service',
            action="store_true",
            help="""Use this flag to enable service mode and increase the function speed""",
            default=False,
        )
