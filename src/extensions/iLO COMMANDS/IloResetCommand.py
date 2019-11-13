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
""" iLO Reset Command for rdmc """

import sys

from argparse import ArgumentParser

from redfish.ris.rmc_helper import IloResponseError

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
                InvalidCommandLineErrorOPTS, NoContentsFoundForOperationError, Encryption

class IloResetCommand(RdmcCommandBase):
    """ Reset iLO on the server that is currently logged in """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='iloreset',\
            usage='iloreset [OPTIONS]\n\n\tReset iLO on the current logged in'\
                                            ' server.\n\texample: iloreset',\
            summary='Reset iLO on the current logged in server.',\
            aliases=['iloreset'],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = self._rdmc.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)

    def run(self, line):
        """ Main iLO reset worker function

        :param line: string of arguments passed in
        :type line: str.
        """
        try:
            (options, _) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.iloresetvalidation(options)

        sys.stdout.write('\nAfter iLO resets the session will be terminated.' \
                         '\nPlease wait for iLO to initialize completely ' \
                         'before logging in again.\n')
        sys.stdout.write('This process may take up to 3 minutes.\n\n')

        select = "Manager."
        results = self._rdmc.app.select(selector=select)

        try:
            results = results[0]
        except:
            pass

        if results:
            put_path = results.resp.request.path
        else:
            raise NoContentsFoundForOperationError("Unable to find %s" % select)

        bodydict = results.resp.dict

        try:
            for item in bodydict['Actions']:
                if 'Reset' in item:
                    if self.typepath.defs.isgen10:
                        action = item.split('#')[-1]
                    else:
                        action = 'Reset'

                    put_path = bodydict['Actions'][item]['target']
                    break
        except:
            action = "Reset"

        body = {"Action": action}

        postres = self._rdmc.app.post_handler(put_path, body, silent=True, \
                                                    service=True, response=True)
        if postres.status == 200:
            sys.stdout.write("A management processor reset is in progress.\n")
        else:
            sys.stderr.write("An error occured during iLO reset.\n")
            raise IloResponseError("")
        #Return code
        return ReturnCodes.SUCCESS

    def iloresetvalidation(self, options):
        """ reboot method validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        inputline = list()

        try:
            client = self._rdmc.app.current_client
        except Exception:
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

        if inputline:
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

        add_login_arguments_group(customparser)
