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
""" Clear Rest API State Command for rdmc """
import sys

from argparse import ArgumentParser
from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group, login_select_validation, \
                                logout_routine
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
                    InvalidCommandLineErrorOPTS, Encryption, \
                    NoContentsFoundForOperationError

class ClearRestApiStateCommand(RdmcCommandBase):
    """ Clear the rest api state of the server """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='clearrestapistate',\
            usage='clearrestapistate [OPTIONS]\n\n\t'\
                'Clears the persistent rest api state.\n\texample: ' \
                'clearrestapistate\n\n\tNote: Some types such as Bios, '\
                'Iscsi, and SmartStorageConfig will be unavailable until '\
                'a system reboot occurs after running this command.',\
            summary='Clears the persistent state of the REST API. Some '\
            'portions of the API may not be available until after the server reboots.',\
            aliases=None,\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath

    def run(self, line):
        """ Main clearrestapistate function.

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

        if args:
            raise InvalidCommandLineError("clearrestapistate command takes no arguments.")

        self.clearrestapistatevalidation(options)

        select = 'Manager.'
        results = self._rdmc.app.select(selector=select)

        try:
            results = results[0]
        except:
            pass

        if results:
            path = results.resp.request.path
        else:
            raise NoContentsFoundForOperationError("Manager. not found.")

        bodydict = results.resp.dict['Oem'][self.typepath.defs.oemhp]
        try:
            for item in bodydict['Actions']:
                if 'ClearRestApiState' in item:
                    if self.typepath.defs.isgen10:
                        action = item.split('#')[-1]
                    else:
                        action = "ClearRestApiState"
                    path = bodydict['Actions'][item]['target']
                    body = {"Action": action}
                    break
        except:
            body = {"Action": "ClearRestApiState", "Target": "/Oem/Hp"}
        self._rdmc.app.post_handler(path, body)

        logout_routine(self, options)
        #Return code
        return ReturnCodes.SUCCESS

    def clearrestapistatevalidation(self, options):
        """ clearrestapistate method validation function.

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
