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
""" Add License Command for rdmc """

from argparse import ArgumentParser
from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group, login_select_validation, \
                                logout_routine
from rdmc_helper import ReturnCodes, InvalidCommandLineError, InvalidCommandLineErrorOPTS, \
                        Encryption

class IloLicenseCommand(RdmcCommandBase):
    """ Add an iLO license to the server """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='ilolicense',\
            usage='ilolicense [LICENSE_KEY] [OPTIONS]\n\n\t'\
                'Set an iLO license on the current logged in server.\n\t' \
                'example: ilolicense xxxxx-xxxxx-xxxxx-xxxxx-xxxxx',\
            summary='Adds an iLO license key to the currently logged in server.',\
            aliases=None,\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath

    def run(self, line):
        """Main ilolicense Function

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

        self.addlicensevalidation(options)

        if not len(args) == 1:
            raise InvalidCommandLineError("ilolicense command only takes one argument")

        path = self.typepath.defs.addlicensepath
        body = {"LicenseKey": "%s" % args[0]}
        self._rdmc.app.post_handler(path, body)

        logout_routine(self, options)
        #Return code
        return ReturnCodes.SUCCESS

    def addlicensevalidation(self, options):
        """ ilolicense validation function

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
