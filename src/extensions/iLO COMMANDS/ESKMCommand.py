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
""" ESKM Command for rdmc """

from argparse import ArgumentParser

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group, login_select_validation, \
                                logout_routine
from rdmc_helper import ReturnCodes, InvalidCommandLineError, InvalidCommandLineErrorOPTS, \
                    NoContentsFoundForOperationError, Encryption

class ESKMCommand(RdmcCommandBase):
    """ Commands ESKM available actions """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='eskm',\
            usage='eskm [OPTIONS]\n\n\tClear the ESKM logs.\n\texample: eskm' \
                    ' clearlog\n\n\tTest the ESKM connections.\n\texample: eskm testconnections',\
            summary="Command for all ESKM available actions.",\
            aliases=None,\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath

    def run(self, line):
        """ Main ESKMCommand function

        :param line: string of arguments passed in
        :type line: str.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        if not len(args) == 1:
            raise InvalidCommandLineError("eskm command only takes one parameter.")

        self.eskmvalidation(options)

        select = self.typepath.defs.hpeskmtype
        results = self._rdmc.app.select(selector=select)

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

        logout_routine(self, options)
        #Return code
        return ReturnCodes.SUCCESS

    def eskmvalidation(self, options):
        """ eskmvalidation method validation function

        :param options: command line options
        :type options: list.
        """
        login_select_validation(self, options)

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        add_login_arguments_group(customparser)
