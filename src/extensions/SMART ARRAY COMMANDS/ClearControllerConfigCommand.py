###
# Copyright 2016 Hewlett Packard Enterprise, Inc. All rights reserved.
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
""" Clear Controller Configuration Command for rdmc """

import sys

from optparse import OptionParser
from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
                                                    InvalidCommandLineErrorOPTS

class ClearControllerConfigCommand(RdmcCommandBase):
    """ Drive erase/sanitize command """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='clearcontrollerconfig',\
            usage='clearcontrollerconfig [OPTIONS]\n\n\tTo clear a controller'\
            ' config.\n\texample: clearcontrollerconfig --controller=1',\
            summary='Clears smart array controller configuration.',\
            aliases=['clearcontrollerconfig'],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)

    def run(self, line):
        """ Main disk inventory worker function

        :param line: command line input
        :type line: string.
        """
        try:
            (options, _) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.clearcontrollerconfigvalidation(options)

        self.selobj.selectfunction("SmartStorageConfig.")
        content = self._rdmc.app.get_save()

        if not options.controller:
            raise InvalidCommandLineError('You must include a controller '\
                                                                'to select.')

        if options.controller:
            controllist = []
            contentsholder = {"Actions": [{"Action": \
                                    "ClearConfigurationMetadata"}], \
                                                        "DataGuard": "Disabled"}

            if options.controller.isdigit() and not options.controller == '0':
                try:
                    controllist.append(content[int(options.controller) - 1])
                except:
                    pass
            else:
                for control in content:
                    if options.controller.lower() == \
                                                    control["Location"].lower():
                        controllist.append(control)

            if not controllist:
                raise InvalidCommandLineError("Selected controller not " \
                                        "found in the current inventory list.")
            else:
                for controller in controllist:
                    self._rdmc.app.patch_handler(controller["@odata.id"], \
                                                                contentsholder)

        #Return code
        return ReturnCodes.SUCCESS

    def clearcontrollerconfigvalidation(self, options):
        """ clear controller config validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        inputline = list()
        runlogin = False

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

        if inputline or not client:
            runlogin = True
            if not inputline:
                sys.stdout.write(u'Local login initiated...\n')

        if runlogin:
            self.lobobj.loginfunction(inputline)

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
            '--controller',
            dest='controller',
            help="""Use this flag to select the corresponding controller.""",
            default=None,
        )
