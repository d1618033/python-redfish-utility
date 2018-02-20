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
""" ESKM Command for rdmc """

from optparse import OptionParser
from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
                    InvalidCommandLineErrorOPTS, \
                    NoContentsFoundForOperationError

class ESKMCommand(RdmcCommandBase):
    """ Commands ESKM available actions """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='eskm',\
            usage='eskm [OPTIONS]\n\n\tClear the ESKM logs.\n\texample: eskm' \
                    ' clearlog\n\n\tTest the ESKM connections.\n\texample: ' \
                    'eskm testconnections',\
            summary="Command for all ESKM available actions.",\
            aliases=None,\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commandsDict["LoginCommand"](rdmcObj)

    def run(self, line):
        """ Main ESKMCommand function

        :param line: string of arguments passed in
        :type line: str.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        if not len(args) == 1:
            raise InvalidCommandLineError("eskm command only takes" \
                                                            " 1 parameter.")

        self.eskmvalidation(options)

        select = self.typepath.defs.hpeskmtype
        results = self._rdmc.app.filter(select, None, None)

        try:
            results = results[0]
        except:
            pass

        if results:
            path = results.resp.request.path
        else:
            raise NoContentsFoundForOperationError("ESKM not found.")

        if args[0].lower() == 'clearlog':
            actionitem = "ClearESKMLog"
        elif args[0].lower() == 'testconnections':
            actionitem = "TestESKMConnections"
        else:
            raise InvalidCommandLineError('Invalid command.')

        bodydict = results.resp.dict
        try:
            for item in bodydict['Actions']:
                if actionitem in item:
                    if self.typepath.defs.isgen10:
                        actionitem = item.split('#')[-1]

                    path = bodydict['Actions'][item]['target']
                    break
        except:
            pass

        body = {"Action": actionitem}
        self._rdmc.app.post_handler(path, body)

        return ReturnCodes.SUCCESS

    def eskmvalidation(self, options):
        """ eskmvalidation method validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        inputline = list()

        try:
            client = self._rdmc.app.get_current_client()
            if options.user and options.password:
                if not client.get_username():
                    client.set_username(options.user)
                if not client.get_password():
                    client.set_password(options.password)
        except:
            if options.user or options.password or options.url:
                if options.url:
                    inputline.extend([options.url])
                if options.user:
                    inputline.extend(["-u", options.user])
                if options.password:
                    inputline.extend(["-p", options.password])
            else:
                if self._rdmc.app.config.get_url():
                    inputline.extend([self._rdmc.app.config.get_url()])
                if self._rdmc.app.config.get_username():
                    inputline.extend(["-u", \
                                  self._rdmc.app.config.get_username()])
                if self._rdmc.app.config.get_password():
                    inputline.extend(["-p", \
                                  self._rdmc.app.config.get_password()])

        if len(inputline):
            self.lobobj.loginfunction(inputline)
        elif not client:
            raise InvalidCommandLineError("Please login or pass credentials" \
                                          " to complete the operation.")

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return
        customparser.add_option(
            '--url',
            dest='url',
            help="Use the provided iLO URL to login.",
            default=None,
        )
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
