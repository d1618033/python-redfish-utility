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
""" SetPassword Command for rdmc """

import sys
import getpass

from argparse import ArgumentParser

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group
from rdmc_helper import ReturnCodes, InvalidCommandLineError, InvalidCommandLineErrorOPTS, \
                        Encryption, UnableToDecodeError

class SetPasswordCommand(RdmcCommandBase):
    """ Set password class command """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='setpassword',\
            usage='setpassword [NEW_PASSWORD] [OLD_PASSWORD] [OPTIONS]\n\n\t'\
                'Setting the admin password with no previous password set.' \
                '\n\texample: setpassword newpassword ""\n\n\tSetting the admin '\
                'password back to nothing.\n\texample: setpassword "" oldpassword'\
                '\n\n\tSetting the power on password.\n\texample: setpassword'\
                ' newpassword oldpassword --poweron\n\n\tNOTE: please make sure' \
                ' the order of passwords is maintained.\n\tThe passwords are' \
                ' extracted base on their position in the arguments list.', \
            summary='Sets the admin password and power-on password',\
            aliases=None,\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.setobj = rdmcObj.commands_dict["SetCommand"](rdmcObj)
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)
        self.commitobj = rdmcObj.commands_dict["CommitCommand"](rdmcObj)
        self.rebootobj = rdmcObj.commands_dict["RebootCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """ Main set password worker function

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

        self.setpasswordvalidation(options)

        if not args:
            sys.stdout.write('Please input the current password.\n')
            tempoldpass = getpass.getpass()

            if tempoldpass and tempoldpass != '\r':
                tempoldpass = tempoldpass
            else:
                tempoldpass = '""'

            sys.stdout.write('Please input the new password.\n')
            tempnewpass = getpass.getpass()

            if tempnewpass and tempnewpass != '\r':
                tempnewpass = tempnewpass
            else:
                tempnewpass = '""'
            args.extend([tempnewpass, tempoldpass])

        if len(args) < 2:
            raise InvalidCommandLineError("Please pass both new password and old password.")

        count = 0
        for arg in args:
            if arg:
                if '"' in arg[0] and '"' in arg[-1] and len(arg) > 2:
                    args[count] = arg[1:-1]
                elif len(arg) == 2 and arg[0] == '"' and arg[1] == '"' or \
                                arg[0] == '"' and arg[1] == '"':
                    args[count] = ''

            count += 1

        if options.encode:
            _args = []
            for arg in args:
                try:
                    _args.append(Encryption.decode_credentials(arg))
                except UnableToDecodeError:
                    _args.append(arg)
            args = _args
        if self.typepath.defs.isgen10:
            bodydict = self._rdmc.app.get_handler(self.typepath.defs.biospath,\
                service=True, silent=True).dict

            for item in bodydict['Actions']:
                if 'ChangePassword' in item:
                    path = bodydict['Actions'][item]['target']
                    break

            if options.poweron:
                body = {"PasswordName": "User", "OldPassword": args[1], "NewPassword": args[0]}
            else:
                body = {"PasswordName": "Administrator", "OldPassword": args[1],\
                        "NewPassword": args[0]}

            self._rdmc.app.post_handler(path, body)
        else:
            if options.poweron:
                self.selobj.run("HpBios.")
                self.setobj.run("PowerOnPassword=%s OldPowerOnPassword=%s" % (args[0], args[1]))
                self.commitobj.run("")
            else:
                self.selobj.run("HpBios.")
                self.setobj.run("AdminPassword=%s OldAdminPassword=%s" % (args[0], args[1]))
                self.commitobj.run("")
                sys.stdout.write('\nThe session will now be terminated.\nPlease'\
                    ' login again with the updated credentials to continue.\n')
                self.logoutobj.run("")

        if options:
            if options.reboot:
                self.rebootobj.run(options.reboot)

        return ReturnCodes.SUCCESS

    def setpasswordvalidation(self, options):
        """ Results method validation function

        :param options: command line options
        :type options: list.
        """
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
            '--reboot',
            dest='reboot',
            help="Use this flag to perform a reboot command function after "\
                "completion of operations. 'REBOOT' is a replaceable parameter "\
                "that can have multiple values. For help with parameters and "\
                "descriptions regarding the reboot flag, run help reboot.",
            default=None,
        )
        customparser.add_argument(
            '--poweron',
            dest='poweron',
            action="store_true",
            help="""Use this flag to set power on password instead""",
            default=None,
        )
