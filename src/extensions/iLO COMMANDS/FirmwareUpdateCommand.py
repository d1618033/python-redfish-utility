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
""" Firmware Update Command for rdmc """

import sys
import time

from optparse import OptionParser
from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
                    InvalidCommandLineErrorOPTS, FirmwareUpdateError, \
                    NoContentsFoundForOperationError

class FirmwareUpdateCommand(RdmcCommandBase):
    """ Reboot server that is currently logged in """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='firmwareupdate',\
            usage='firmwareupdate [URI] [OPTIONS]\n\n\tApply a firmware ' \
                    'update to the current logged in server.\n\texample: ' \
                    'firmwareupdate <iLO url/hostname>/images/image.bin',\
            summary='Perform a firmware update on the currently logged in ' \
                                                                    'server.',\
            aliases=['firmwareupdate'],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commandsDict["LoginCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commandsDict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """ Main firmware update worker function

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

        if len(args) == 1:
            self.firmwareupdatevalidation(options)
        else:
            raise InvalidCommandLineError("Invalid number of parameters." \
                          " Firmware update takes exactly 1 parameter.")

        if args[0].startswith('"') and args[0].endswith('"'):
            args[0] = args[0][1:-1]

        action = None
        uri = "FirmwareURI"
        select = self.typepath.defs.hpilofirmwareupdatetype
        results = self._rdmc.app.filter(select, None, None)
        try:
            results = results[0]
        except:
            pass

        if results:
            update_path = results.resp.request.path
        else:
            raise NoContentsFoundForOperationError("Unable to find %s" % select)

        bodydict = results.resp.dict

        try:
            for item in bodydict['Actions']:
                if self.typepath.defs.isgen10:
                    if 'SimpleUpdate' in item:
                        action = item.split('#')[-1]
                    uri = "ImageURI"
                    options.tpmenabled = False
                elif 'InstallFromURI' in item:
                    action = 'InstallFromURI'

                if action:
                    put_path = bodydict['Actions'][item]['target']
                    break
        except:
            put_path = update_path
            action = "Reset"

        if options.tpmenabled:
            body = {"Action": action,\
                       uri: args[0], "TPMOverrideFlag": True}
        else:
            body = {"Action": action, uri: args[0]}

        self._rdmc.app.post_handler(put_path, body, silent=True, service=True)

        sys.stdout.write("\nStarting upgrading process...\n\n")

        self.showupdateprogress(update_path)
        self.logoutobj.logoutfunction("")

        #Return code
        return ReturnCodes.SUCCESS

    def showupdateprogress(self, path):
        """ handler function for updating the progress

        :param path: path to update service.
        :tyep path: str
        """
        counter = 0
        written = False
        uploadingpost = False
        spinner = ['|', '/', '-', '\\']
        position = 0

        while True:
            if counter == 100:
                raise FirmwareUpdateError("Error occurred while updating "\
                                          "the firmware.")
            else:
                counter += 1

            results = self._rdmc.app.get_handler(path, silent=True)
            results = results.dict
            try:
                results = results['Oem']['Hpe']
            except:
                pass

            if not results:
                raise FirmwareUpdateError("Unable to contact Update Service. Please"\
                                    " re-login and try again.")

            if results["State"].lower().startswith("idle"):
                time.sleep(2)
            elif results["State"].lower().startswith("uploading"):
                counter = 0
                if not uploadingpost:
                    uploadingpost = True
                else:
                    if written == False:
                        written = True
                        sys.stdout.write("iLO is uploading the necessary files."\
                                         " Please wait...")
                time.sleep(0.5)
            elif results["State"].lower().startswith(("progressing", "updating", \
                                                        "verifying", "writing")):
                counter = 0
                for _ in range(2):
                    if position < 4:
                        sys.stdout.write("Updating: "+ spinner[position]+"\r")
                        position += 1
                        time.sleep(0.1)
                    else:
                        position = 0
                        sys.stdout.write("Updating: "+ spinner[position]+"\r")
                        position += 1
                        time.sleep(0.1)
            elif results["State"].lower().startswith("complete"):
                sys.stdout.write(u'\n\nFirmware update has completed and iLO' \
                                 ' may reset. \nIf iLO resets the' \
                                 ' session will be terminated.\nPlease wait' \
                                 ' for iLO to initialize completely before' \
                                 ' logging in again.\nA reboot may be required'\
                                 ' for firmware changes to take effect.\n')
                break
            elif results["State"].lower().startswith("error"):
                raise FirmwareUpdateError("Error occurred while updating "\
                                                                "the firmware.")

    def firmwareupdatevalidation(self, options):
        """ Firmware update method validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        inputline = list()

        try:
            client = self._rdmc.app.get_current_client()
        except Exception:
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
        customparser.add_option(
            '--tpmenabled',
            dest='tpmenabled',
            action='store_true',
            help="Use this flag if the server you are currently logged into"\
            " has a TPM chip installed.",
            default=False
        )
