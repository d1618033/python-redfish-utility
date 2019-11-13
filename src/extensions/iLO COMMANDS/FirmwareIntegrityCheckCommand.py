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
""" Firmware Update Command for rdmc """

import sys
import time

from datetime import datetime

from argparse import ArgumentParser
from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group
from rdmc_helper import ReturnCodes, InvalidCommandLineError, IloLicenseError, Encryption, \
                    InvalidCommandLineErrorOPTS, IncompatibleiLOVersionError, TimeOutError

class FirmwareIntegrityCheckCommand(RdmcCommandBase):
    """ Reboot server that is currently logged in """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='fwintegritycheck',\
            usage='fwintegritycheck [OPTIONS]\n\n\tPerform a firmware ' \
                    'integrity check on the current logged in server.\n\t' \
                    'example: fwintegritycheck\n\n\tPerform a firmware integrity check and '\
                    'return results of the check.\n\texmaple: fwintegritycheck --results',\
            summary='Perform a firmware integrity check on the currently logged in server.',\
            aliases=['fwintegritycheck'],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """ Main firmware update worker function

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
            raise InvalidCommandLineError('fwintegritycheck command takes no arguments')

        self.firmwareintegritycheckvalidation(options)
        if self.typepath.defs.isgen9:
            raise IncompatibleiLOVersionError('fwintegritycheck command is ' \
                                                    'only available on iLO 5.')

        licenseres = self._rdmc.app.select(selector='HpeiLOLicense.')
        try:
            licenseres = licenseres[0]
        except:
            pass
        if not licenseres.dict['LicenseFeatures']['FWScan']:
            raise IloLicenseError("This command is not available with this iLO license.")

        select = self.typepath.defs.hpilofirmwareupdatetype
        results = self._rdmc.app.select(selector=select)

        try:
            results = results[0]
        except:
            pass

        bodydict = results.resp.dict

        path = bodydict['Oem']['Hpe']['Actions']\
            ['#HpeiLOUpdateServiceExt.StartFirmwareIntegrityCheck']['target']

        self._rdmc.app.post_handler(path, {})

        if options.results:
            results_string = "Awaiting results of firmware integrity check..."
            sys.stdout.write(results_string)
            polling = 50
            found = False
            while polling > 0:
                if not polling % 5:
                    sys.stdout.write('.')
                get_results = self._rdmc.app.get_handler(bodydict['@odata.id'],\
                    service=True, silent=True)
                if get_results:
                    curr_time = datetime.strptime(bodydict['Oem']['Hpe']\
                                        ['CurrentTime'], "%Y-%m-%dT%H:%M:%SZ")
                    scan_time = datetime.strptime(get_results.dict['Oem']['Hpe']\
                        ['FirmwareIntegrity']['LastScanTime'], "%Y-%m-%dT%H:%M:%SZ")

                    if scan_time > curr_time:
                        sys.stdout.write('\nScan Result: %s\n' % get_results.dict\
                            ['Oem']['Hpe']['FirmwareIntegrity']['LastScanResult'])
                        found = True
                        break

                    polling -= 1
                    time.sleep(1)
            if not found:
                sys.stdout.write('\nPolling timed out before scan completed.\n')
                TimeOutError("")

        return ReturnCodes.SUCCESS

    def firmwareintegritycheckvalidation(self, options):
        """ Firmware update method validation function

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

        customparser.add_argument(
            '--results',
            dest='results',
            help="Optionally include this flag to show results of firmware integrity check.",
            default=False,
            action='store_true'
        )
