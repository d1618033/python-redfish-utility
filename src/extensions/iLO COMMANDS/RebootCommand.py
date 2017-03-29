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
""" Reboot Command for rdmc """

import sys
import time

from optparse import OptionParser
from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
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
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._hprmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commandsDict["LoginCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commandsDict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """ Main reboot worker function

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

        if len(args) < 2:
            self.rebootvalidation(options)
        else:
            raise InvalidCommandLineError("Invalid number of parameters." \
                                      " Reboot takes a maximum of 1 parameter.")

        if not args:
            sys.stdout.write(u'\nAfter the server is rebooted the session' \
             ' will be terminated.\nPlease wait for the server' \
             ' to boot completely to login again.\n')
            sys.stdout.write(u'Rebooting server in 3 seconds...\n')
            time.sleep(3)
        else:
            self.printreboothelp(args[0])

        select = "ComputerSystem."
        results = self._hprmc.app.filter(select, None, None)
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
            bodydict = results.resp.dict['Oem'][self.typepath.defs.oemhp]\
                                                                    ['Actions']
            if args[0].lower() == 'coldboot':
                resettype = 'SystemReset'
            else:
                resettype = 'PowerButton'
        else:
            bodydict = results.resp.dict['Actions']
            resettype = 'Reset'

        try:
            for item in bodydict:
                if resettype in item:
                    if self.typepath.defs.isgen10:
                        action = item.split('#')[-1]
                    else:
                        action = resettype
                    put_path = bodydict[item]['target']
                    break
        except:
            action = "Reset"

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

        self._hprmc.app.post_handler(put_path, body)
        self.logoutobj.logoutfunction("")

        #Return code
        return ReturnCodes.SUCCESS

    def printreboothelp(self, flag):
        """helper print function for reboot function

        :param flag: command line option
        :type flag: str
        """
        if flag.upper() == "ON":
            sys.stdout.write(u'\nSession will now be terminated.\nPlease wait' \
                        ' for the server to boot completely to login again.\n')
            sys.stdout.write(u'Turning on the server in 3 seconds...\n')
            time.sleep(3)
        elif flag.upper() == "FORCEOFF":
            sys.stdout.write(u'\nServer is powering off the session will be' \
             ' terminated.\nPlease wait for the server to boot completely' \
             ' to login again.\n')
            sys.stdout.write(u'Powering off the server in 3 seconds...\n')
            time.sleep(3)
        elif flag.upper() == "FORCERESTART":
            sys.stdout.write(u'\nAfter the server is rebooted the session' \
                         ' will be terminated.\nPlease wait for the server' \
                         ' to boot completely to login again.\n')
            sys.stdout.write(u'Rebooting server in 3 seconds...\n')
            time.sleep(3)
        elif flag.upper() == "NMI":
            sys.stdout.write(u'\nThe session will be now be terminated.\n' \
                             'Please wait for the server to boot completely' \
                             ' to login again.\n')
            sys.stdout.write(u'Generating interrupt in 3 seconds...\n')
            time.sleep(3)
        elif flag.upper() == "PUSHPOWERBUTTON":
            sys.stdout.write(u'\nThe server is powering on/off and the ' \
                             'session will be terminated.\nPlease wait for ' \
                             'the server to boot completely ' \
                             'to login again.\n')
            sys.stdout.write(u'Powering off the server in 3 seconds...\n')
            time.sleep(3)
        elif flag.upper() == "COLDBOOT":
            sys.stdout.write(u'\nAfter the server is rebooted the session' \
                         ' will be terminated.\nPlease wait for the server' \
                         ' to boot completely to login again.\n')
            sys.stdout.write(u'Cold Booting server in 3 seconds...\n')
        elif flag.upper() == "PRESS":
            sys.stdout.write(u'\nThe server is powering on/off and the ' \
                             'session will be terminated.\nPlease wait for ' \
                             'the server to boot completely ' \
                             'to login again.\n')
            sys.stdout.write(u'Pressing the power button in 3 seconds...\n')
            time.sleep(3)
        elif flag.upper() == "PRESSANDHOLD":
            sys.stdout.write(u'\nServer is powering off the session will be' \
             ' terminated.\nPlease wait for the server to boot completely' \
             ' to login again.\n')
            sys.stdout.write(u'Pressing and holding the power button in 3 '\
                                                                'seconds...\n')
            time.sleep(3)
        else:
            raise InvalidCommandLineError("Invalid parameter: '%s'. Please run"\
                                  " 'help reboot' for parameters." % flag)

    def rebootvalidation(self, options):
        """ reboot method validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        inputline = list()
        runlogin = False

        try:
            client = self._hprmc.app.get_current_client()
        except Exception:
            if options.user or options.password or options.url:
                if options.url:
                    inputline.extend([options.url])
                if options.user:
                    inputline.extend(["-u", options.user])
                if options.password:
                    inputline.extend(["-p", options.password])
            else:
                if self._hprmc.app.config.get_url():
                    inputline.extend([self._hprmc.app.config.get_url()])
                if self._hprmc.app.config.get_username():
                    inputline.extend(["-u", \
                                  self._hprmc.app.config.get_username()])
                if self._hprmc.app.config.get_password():
                    inputline.extend(["-p", \
                                  self._hprmc.app.config.get_password()])

        if len(inputline) or not client:
            runlogin = True
            if not len(inputline):
                sys.stdout.write(u'Local login initiated...\n')
        if options.includelogs:
            inputline.extend(["--includelogs"])

        if runlogin:
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
            '--includelogs',
            dest='includelogs',
            action="store_true",
            help="Optionally include logs in the data retrieval process.",
            default=False,
        )
