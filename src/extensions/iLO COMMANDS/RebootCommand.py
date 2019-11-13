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
""" Reboot Command for rdmc """

import sys
import time

from argparse import ArgumentParser
from six.moves import input
from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group
from rdmc_helper import ReturnCodes, InvalidCommandLineError, Encryption, \
                InvalidCommandLineErrorOPTS, NoContentsFoundForOperationError

class RebootCommand(RdmcCommandBase):
    """ Reboot server that is currently logged in """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='reboot',\
            usage='reboot [OPTIONS]\n\n\tTurning the system on\n\texample: ' \
                'reboot On\n\n\tOPTIONAL PARAMETERS AND DESCRIPTIONS:' \
                '\n\tOn \t\t(Turns the system on.)\n\tForceOff  ' \
                '\t(Performs an immediate non-graceful shutdown.)' \
                '\n\tForceRestart \t(DEFAULT) (Performs' \
                ' an immediate non-graceful shutdown,\n\t\t\t' \
                ' followed by a restart of the system.)\n\tNmi  ' \
                '\t\t(Generates a Non-Maskable Interrupt to cause' \
                ' an\n\t\t\t immediate system halt.)\n\tPushPowerButton ' \
                '(Simulates the pressing of the physical power ' \
                'button\n\t\t\t on this system.)\n\n\tOEM PARAMETERS AND'\
                ' DESCRIPTIONS:\n\tPress\t\t(Simulates the pressing of the'\
                ' physical power button\n\t\t\t on this system.)\n\t'\
                'PressAndHold\t(Simulates pressing and holding of the power'\
                ' button\n\t\t\t on this systems.)\n\tColdBoot\t(Immidiately'\
                ' Removes power from the server,\n\t\t\tfollowed by a restart'\
                ' of the system)',\
            summary='Reboot operations for the current logged in server.',\
            aliases=['reboot'],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """ Main reboot worker function

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

        if len(args) < 2:
            self.rebootvalidation(options)
        else:
            raise InvalidCommandLineError("Invalid number of parameters." \
                                      " Reboot takes a maximum of 1 parameter.")

        if not args:
            sys.stdout.write('\nAfter the server is rebooted the session' \
             ' will be terminated.\nPlease wait for the server' \
             ' to boot completely to login again.\n')
            sys.stdout.write('Rebooting server in 3 seconds...\n')
            time.sleep(3)
        else:
            self.printreboothelp(args[0])

        select = "ComputerSystem."
        results = self._rdmc.app.select(selector=select)
        oemlist = ['press', 'pressandhold', 'coldboot']

        try:
            results = results[0]
        except:
            pass

        if results:
            put_path = results.resp.request.path
        else:
            raise NoContentsFoundForOperationError("Unable to find %s" % select)

        if args and args[0].lower() in oemlist:
            bodydict = results.resp.dict['Oem'][self.typepath.defs.oemhp]

            if args[0].lower() == 'coldboot':
                resettype = 'SystemReset'
            else:
                resettype = 'PowerButton'
        else:
            bodydict = results.resp.dict
            resettype = 'Reset'

        try:
            for item in bodydict['Actions']:
                if resettype in item:
                    if self.typepath.defs.isgen10:
                        action = item.split('#')[-1]
                    else:
                        action = resettype

                    put_path = bodydict['Actions'][item]['target']
                    break
        except:
            action = resettype

        if args and not args[0].lower() == "forcerestart":
            if args[0].lower() == "on":
                body = {"Action": action, "ResetType": "On"}
            elif args[0].lower() == "forceoff":
                body = {"Action": action, "ResetType": "ForceOff"}
            elif args[0].lower() == "nmi":
                body = {"Action": action, "ResetType": "Nmi"}
            elif args[0].lower() == "pushpowerbutton":
                body = {"Action": action, "ResetType": "PushPowerButton"}
            elif args[0].lower() == "press":
                body = {"Action": action, "PushType": "Press"}
            elif args[0].lower() == "pressandhold":
                body = {"Action": action, "PushType": "PressAndHold"}
            elif args[0].lower() == "coldboot":
                body = {"Action": action, "ResetType": "ColdBoot"}
        else:
            body = {"Action": action, "ResetType": "ForceRestart"}

        if options.confirm is True:
            count = 0
            while True:
                count = count+1
                confirmation = input("Rebooting system, type yes to confirm or no to abort:")
                if confirmation.lower() in ('no', 'n') or count > 3:
                    sys.stdout.write('Aborting reboot.\n')
                    return ReturnCodes.SUCCESS
                elif confirmation.lower() in ('yes', 'y'):
                    break

        self._rdmc.app.post_handler(put_path, body)
        self.logoutobj.run("")

        #Return code
        return ReturnCodes.SUCCESS

    def printreboothelp(self, flag):
        """helper print function for reboot function

        :param flag: command line option
        :type flag: str
        """
        if flag.upper() == "ON":
            sys.stdout.write('\nSession will now be terminated.\nPlease wait' \
                        ' for the server to boot completely to login again.\n')
            sys.stdout.write('Turning on the server in 3 seconds...\n')
            time.sleep(3)
        elif flag.upper() == "FORCEOFF":
            sys.stdout.write('\nServer is powering off the session will be' \
             ' terminated.\nPlease wait for the server to boot completely to login again.\n')
            sys.stdout.write('Powering off the server in 3 seconds...\n')
            time.sleep(3)
        elif flag.upper() == "FORCERESTART":
            sys.stdout.write('\nAfter the server is rebooted the session' \
                         ' will be terminated.\nPlease wait for the server' \
                         ' to boot completely to login again.\n')
            sys.stdout.write('Rebooting server in 3 seconds...\n')
            time.sleep(3)
        elif flag.upper() == "NMI":
            sys.stdout.write('\nThe session will be now be terminated.\n' \
                             'Please wait for the server to boot completely to login again.\n')
            sys.stdout.write('Generating interrupt in 3 seconds...\n')
            time.sleep(3)
        elif flag.upper() == "PUSHPOWERBUTTON":
            sys.stdout.write('\nThe server is powering on/off and the ' \
                             'session will be terminated.\nPlease wait for ' \
                             'the server to boot completely to login again.\n')
            sys.stdout.write('Powering off the server in 3 seconds...\n')
            time.sleep(3)
        elif flag.upper() == "COLDBOOT":
            sys.stdout.write('\nAfter the server is rebooted the session' \
                         ' will be terminated.\nPlease wait for the server' \
                         ' to boot completely to login again.\n')
            sys.stdout.write('Cold Booting server in 3 seconds...\n')
        elif flag.upper() == "PRESS":
            sys.stdout.write('\nThe server is powering on/off and the ' \
                             'session will be terminated.\nPlease wait for ' \
                             'the server to boot completely to login again.\n')
            sys.stdout.write('Pressing the power button in 3 seconds...\n')
            time.sleep(3)
        elif flag.upper() == "PRESSANDHOLD":
            sys.stdout.write('\nServer is powering off the session will be' \
             ' terminated.\nPlease wait for the server to boot completely' \
             ' to login again.\n')
            sys.stdout.write('Pressing and holding the power button in 3 seconds...\n')
            time.sleep(3)
        else:
            raise InvalidCommandLineError("Invalid parameter: '%s'. Please run"\
                                  " 'help reboot' for parameters." % flag)

    def rebootvalidation(self, options):
        """ reboot method validation function

        :param options: command line options
        :type options: list.
        """
        inputline = list()

        try:
            _ = self._rdmc.app.current_client
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

            if not inputline:
                sys.stdout.write('Local login initiated...\n')
            self.lobobj.loginfunction(inputline)

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        add_login_arguments_group(customparser)

        customparser.add_argument(
            '--confirm',
            dest='confirm',
            action="store_true",
            help="Optionally include to request user confirmation for reboot.",
            default=False,
        )
