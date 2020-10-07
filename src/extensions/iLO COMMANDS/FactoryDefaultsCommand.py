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
""" Factory Defaults Command for rdmc """
import sys

from argparse import ArgumentParser

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group, login_select_validation, \
                                logout_routine
from rdmc_helper import ReturnCodes, InvalidCommandLineError, InvalidCommandLineErrorOPTS, \
                    NoContentsFoundForOperationError, Encryption

class FactoryDefaultsCommand(RdmcCommandBase):
    """ Reset server to factory default settings """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='factorydefaults',\
            usage='factorydefaults [OPTIONS]\n\n\t'\
                'Reset iLO to factory defaults in the current logged in ' \
                'server.\n\texample: factorydefaults',\
            summary='Resets iLO to factory defaults. WARNING: user data will ' \
                'be removed use with caution.',\
            aliases=None,\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath

    def run(self, line):
        """ Main factorydefaults function

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
            raise InvalidCommandLineError("factorydefaults command takes no arguments.")

        self.factorydefaultsvalidation(options)

        sys.stdout.write("Resetting iLO to factory default settings.\n"\
                                        "Current session will be terminated.\n")

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
                if 'ResetToFactoryDefaults' in item:
                    if self.typepath.defs.isgen10:
                        action = item.split('#')[-1]
                    else:
                        action = "ResetToFactoryDefaults"

                    path = bodydict['Actions'][item]['target']
                    body = {"Action": action, "ResetType": "Default"}
                    break
        except:
            body = {"Action": "ResetToFactoryDefaults", \
                                "Target": "/Oem/Hp", "ResetType": "Default"}

        self._rdmc.app.post_handler(path, body, service=True)

        logout_routine(self, options)
        #Return code
        return ReturnCodes.SUCCESS

    def factorydefaultsvalidation(self, options):
        """ factory defaults validation function

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
