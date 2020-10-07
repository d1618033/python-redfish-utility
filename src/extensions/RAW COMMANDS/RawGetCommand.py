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
""" RawGet Command for rdmc """

import sys
import json

from argparse import ArgumentParser

import redfish

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group, login_select_validation, \
                                logout_routine
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
                    InvalidCommandLineErrorOPTS, UI, Encryption

class RawGetCommand(RdmcCommandBase):
    """ Raw form of the get command """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='rawget',\
            usage='rawget [PATH] [OPTIONS]\n\n\tRun to to retrieve data from ' \
                    'the passed in path.\n\texample: rawget "/redfish/v1/systems/(system ID)"',\
            summary='Raw form of the GET command.',\
            aliases=['rawget'],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj

    def run(self, line):
        """ Main raw get worker function

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

        headers = {}

        self.getvalidation(options)

        if options.path.startswith('"') and options.path.endswith('"'):
            options.path = options.path[1:-1]

        if options.expand:
            options.path = options.path + '?$expand=.'

        if options.headers:
            extraheaders = options.headers.split(',')
            for item in extraheaders:
                header = item.split(':')

                try:
                    headers[header[0]] = header[1]
                except:
                    InvalidCommandLineError("Invalid format for --headers option.")

        returnresponse = False
        if options.response or options.getheaders:
            returnresponse = True

        results = self._rdmc.app.get_handler(options.path, headers=headers,\
                silent=options.silent, service=options.service)

        if results and results.status == 200 and options.binfile:
            output = results.read

            filehndl = open(options.binfile[0], "wb")
            filehndl.write(output)
            filehndl.close()

        elif results and returnresponse:
            if options.getheaders:
                sys.stdout.write(json.dumps(dict(\
                                 results.getheaders())) + "\n")

            if options.response:
                sys.stdout.write(results.read)
        elif results and results.status == 200:
            if results.dict:
                if options.filename:
                    output = json.dumps(results.dict, indent=2, cls=redfish.ris.JSONEncoder, \
                                        sort_keys=True)

                    filehndl = open(options.filename[0], "w")
                    filehndl.write(output)
                    filehndl.close()

                    sys.stdout.write("Results written out to '%s'.\n" % options.filename[0])
                else:
                    if options.service:
                        sys.stdout.write("%s\n" % results.dict)
                    else:
                        UI().print_out_json(results.dict)
        else:
            return ReturnCodes.NO_CONTENTS_FOUND_FOR_OPERATION

        logout_routine(self, options)
        #Return code
        return ReturnCodes.SUCCESS

    def getvalidation(self, options):
        """ Raw get validation function

        :param options: command line options
        :type options: list.
        """
        login_select_validation(self, options, skipbuild=True)

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        add_login_arguments_group(customparser)

        customparser.add_argument(
            'path',
            help="Uri on iLO",
        )
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
            '-f',
            '--filename',
            dest='filename',
            help="""Write results to the specified file.""",
            action="append",
            default=None,
        )
        customparser.add_argument(
            '-b',
            '--writebin',
            dest='binfile',
            help="""Write the results to the specified file in binary.""",
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
        customparser.add_argument(
            '--expand',
            dest='expand',
            action="store_true",
            help="""Use this flag to expand the path specified using the """\
                                            """expand notation '?$expand=.'""",
            default=False,
        )
