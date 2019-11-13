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
""" BiosDefaultsCommand for rdmc """

import sys

from argparse import ArgumentParser

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group
from rdmc_helper import ReturnCodes, InvalidCommandLineError, InvalidCommandLineErrorOPTS, \
                        Encryption

class BiosDefaultsCommand(RdmcCommandBase):
    """ Set BIOS settings back to default for the server that is currently
        logged in """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='biosdefaults',\
            usage="biosdefaults [OPTIONS]\n\n\tRun to set the currently" \
                " logged in server's Bios. type settings to defaults\n\texample: "\
                "biosdefaults\n\n\tRun to set the currently logged in server's "\
                "Bios. type settings to user defaults\n\texample: biosdefaults "\
                "--userdefaults\n\n\tRun to set the currently logged in server "\
                "to manufacturing defaults, including boot order and secure boot."
                "\n\texample: biosdefaults --manufacturingdefaults",\
            summary='Set the currently logged in server to default BIOS settings.',\
            aliases=['biosdefaults'],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.setobj = rdmcObj.commands_dict["SetCommand"](rdmcObj)
        self.rebootobj = rdmcObj.commands_dict["RebootCommand"](rdmcObj)

    def run(self, line):
        """ Main BIOS defaults worker function """
        try:
            (options, _) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.defaultsvalidation(options)

        sys.stdout.write('Resetting the currently logged in server\'s BIOS settings to defaults.\n')

        put_path = self.typepath.defs.biospath
        body = None

        if self.typepath.defs.isgen10 and not options.manufdefaults:
            bodydict = self._rdmc.app.get_handler(self.typepath.defs.biospath,\
                                        service=True, silent=True).dict

            for item in bodydict['Actions']:
                if 'ResetBios' in item:
                    action = item.split('#')[-1]
                    path = bodydict['Actions'][item]['target']
                    break

            body = {"Action": action}

            if options.userdefaults:
                body["ResetType"] = "default.user"
            else:
                body["ResetType"] = "default"

            self._rdmc.app.post_handler(path, body)
        else:
            if options.userdefaults:
                body = {'BaseConfig': 'default.user'}
            elif not options.manufdefaults:
                body = {'BaseConfig': 'default'}

            if body:
                self._rdmc.app.put_handler(put_path + '/settings', body=body, \
                                        optionalpassword=options.biospassword)

        if not body and options.manufdefaults:
            setstring = "RestoreManufacturingDefaults=Yes --selector=HpBios. --commit"
            if options.reboot:
                setstring += " --reboot=%s" % options.reboot

            self.setobj.run(setstring)

        elif options.reboot:
            self.rebootobj.run(options.reboot)

        #Return code
        return ReturnCodes.SUCCESS

    def defaultsvalidation(self, options):
        """ BIOS defaults method validation function """
        client = None
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
            '--biospassword',
            dest='biospassword',
            help="Select this flag to input a BIOS password. Include this"\
            " flag if second-level BIOS authentication is needed for the"\
            " command to execute. This option is only used on Gen 9 systems.",
            default=None,
        )
        customparser.add_argument(
            '--reboot',
            dest='reboot',
            help="Use this flag to perform a reboot command function after"\
            " completion of operations.  For help with parameters and"\
            " descriptions regarding the reboot flag, run help reboot.",
            default=None,
        )
        customparser.add_argument(
            '--userdefaults',
            dest='userdefaults',
            action="store_true",
            help="Sets bios to user defaults instead of factory "\
                                                                "defaults.",
            default=False
        )
        customparser.add_argument(
            '--manufacturingdefaults',
            dest='manufdefaults',
            action="store_true",
            help="Reset all configuration settings to manufacturing defaults, "\
                                        "including boot order and secure boot.",
            default=False
        )
