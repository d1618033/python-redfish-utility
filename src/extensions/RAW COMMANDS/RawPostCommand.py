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
""" RawPost Command for rdmc """

import sys
import json

from argparse import ArgumentParser
from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
                    InvalidCommandLineErrorOPTS, InvalidFileInputError, \
                    InvalidFileFormattingError, Encryption

class RawPostCommand(RdmcCommandBase):
    """ Raw form of the post command """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='rawpost',\
            usage='rawpost [FILENAME] [OPTIONS]\n\n\tRun to send a post from ' \
                    'the data in the input file.\n\texample: rawpost rawpost.' \
                    'txt\n\n\tExample input file:\n\t{\n\t    "path": "/' \
                    'redfish/v1/systems/(system ID)/Actions/ComputerSystem.'
                    'Reset",\n\t    "body": {\n\t        "ResetType": '\
                    '"ForceRestart"\n\t    }\n\t}',\
            summary='Raw form of the POST command.',\
            aliases=['rawpost'],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)

    def run(self, line):
        """ Main raw patch worker function

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
        results = None

        self.postvalidation(options)

        contentsholder = None

        if len(args) == 1:
            try:
                inputfile = open(args[0], 'r')
                contentsholder = json.loads(inputfile.read())
            except Exception as excp:
                raise InvalidFileInputError("%s" % excp)
        elif len(args) > 1:
            raise InvalidCommandLineError("Raw post only takes 1 argument.\n")
        else:
            raise InvalidCommandLineError("Missing raw post file input argument.\n")
        if options.encode:
            if "body" in contentsholder and "UserName" in contentsholder["body"] and \
                        "Password" in contentsholder["body"] and \
                        len(list(contentsholder["body"].keys())) == 2:
                encobj = Encryption()
                contentsholder["body"]["UserName"] = encobj.decode_credentials(\
                                            contentsholder["body"]["UserName"])
                contentsholder["body"]["Password"] = encobj.decode_credentials(\
                                            contentsholder["body"]["Password"])

        if options.headers:
            extraheaders = options.headers.split(',')
            for item in extraheaders:
                header = item.split(':')

                try:
                    headers[header[0]] = header[1]
                except:
                    raise InvalidCommandLineError("Invalid format for --headers option.")

        if "path" in contentsholder and "body" in contentsholder:
            returnresponse = False

            if options.response or options.getheaders:
                returnresponse = True

            results = self._rdmc.app.post_handler(contentsholder["path"], \
                  contentsholder["body"], headers=headers, \
                  response=returnresponse, silent=options.silent, service=options.service)
        else:
            raise InvalidFileFormattingError("Input file '%s' was not "\
                                             "formatted properly." % args[0])

        if results and returnresponse:
            if options.getheaders:
                sys.stdout.write(json.dumps(dict(results.getheaders())) + "\n")

            if options.response:
                sys.stdout.write(results.ori + "\n")

        #Return code
        return ReturnCodes.SUCCESS

    def postvalidation(self, options):
        """ Raw post validation function

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
            default=False
        )
