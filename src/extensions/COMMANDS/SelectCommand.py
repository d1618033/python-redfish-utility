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
""" Select Command for RDMC """

import sys

from argparse import ArgumentParser

import redfish.ris

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group, logout_routine
from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, LOGGER, Encryption

class SelectCommand(RdmcCommandBase):
    """ Constructor """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='select',\
            usage='select [TYPE] [OPTIONS]\n\n\tRun without a type to display' \
            ' currently selected type\n\texample: select\n\n\tIn order to ' \
            'remove the need of including the version\n\twhile selecting you' \
            ' can simply enter the type name\n\tuntil the first period\n\t' \
            'example: select HpBios.',\
            summary='Selects the object type to be used.',\
            aliases=['sel'],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)

    def selectfunction(self, line):
        """ Main select worker function

        :param line: command line input
        :type line: string.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.selectvalidation(options)

        try:
            if args:
                if options.ref:
                    LOGGER.warn("Patches from current selection will be cleared.")
                selector = args[0]
                selections = self._rdmc.app.select(selector=selector, path_refresh=options.ref)

                if self._rdmc.opts.verbose and selections:
                    templist = list()
                    sys.stdout.write("Selected option(s): ")

                    for item in selections:
                        if item.type not in templist:
                            templist.append(item.type)

                    sys.stdout.write('%s' % ', '.join(map(str, templist)))
                    sys.stdout.write('\n')
            else:
                selector = self._rdmc.app.selector

                if selector:
                    sellist = [sel for sel in self._rdmc.app.\
                       monolith.typesadded if selector.lower() in sel.lower()]
                    sys.stdout.write("Current selection: ")
                    sys.stdout.write('%s' % ', '.join(map(str, sellist)))
                    sys.stdout.write('\n')
                else:
                    raise redfish.ris.NothingSelectedError

        except redfish.ris.InstanceNotFoundError as infe:
            raise redfish.ris.InstanceNotFoundError(infe)

        logout_routine(self, options)

    def selectvalidation(self, options):
        """ Select data validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        runlogin = False
        inputline = list()

        try:
            client = self._rdmc.app.current_client
        except:
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
                if self._rdmc.config.url:
                    inputline.extend([self._rdmc.config.url])
                if self._rdmc.config.username:
                    inputline.extend(["-u", self._rdmc.config.username])
                if self._rdmc.config.password:
                    inputline.extend(["-p", self._rdmc.config.password])
                if self._rdmc.config.ssl_cert:
                    inputline.extend(["--https", self._rdmc.config.ssl_cert])

        if not inputline and not client:
            try:
                if self._rdmc.opts.verbose > 1:
                    sys.stdout.write("Local login initiated...\n")
                else:
                    raise Exception
            except Exception:
                LOGGER.info("Local login initiated...\n")
        if inputline:
            runlogin = True
        if options.includelogs:
            inputline.extend(["--includelogs"])
        if options.path:
            inputline.extend(["--path", options.path])
        if not client or runlogin:
            self.lobobj.loginfunction(inputline)

    def run(self, line):
        """ Wrapper function for main select function

        :param line: entered command line
        :type line: list.
        """
        self.selectfunction(line)

        #Return code
        return ReturnCodes.SUCCESS

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        add_login_arguments_group(customparser)

        customparser.add_argument(
            '--refresh',
            dest='ref',
            action="store_true",
            help="Optionally reload the data of selected type and clear "\
                                            "patches from current selection.",
            default=False,
        )
        customparser.add_argument(
            '--biospassword',
            dest='biospassword',
            help="Select this flag to input a BIOS password. Include this"\
            " flag if second-level BIOS authentication is needed for the"\
            " command to execute. This option is only used on Gen 9 systems.",
            default=None,
        )
