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
""" Add Account Command for rdmc """

import sys
import getpass

from optparse import OptionParser
from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, AccountExists, \
                InvalidCommandLineErrorOPTS, NoContentsFoundForOperationError

class IloAccountsCommand(RdmcCommandBase):
    """ command to manipulate/add ilo user accounts """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='iloaccounts',\
            usage='iloaccounts [COMMAND] [OPTIONS]\n\n\t'\
            'Add an iLO user account the current logged in server.\n\t' \
            'iloaccounts add [USERNAME LOGINNAME PASSWORD] \n\t'\
            'example: iloaccounts add USERNAME ACCOUNTNAME PASSWORD' \
            '\n\n\tChange the password of an account.\n\t'\
            'iloaccounts changepass [LOGINNAMEorID# PASSWORD]\n\t'\
            'example: iloaccounts changepass 2 newpassword\n\n\t'\
            'Get Id and LoginName info of iLO user accounts.\n\t'\
            'example: iloaccounts\n\n\tDelete an iLO account.\n\t'\
            'iloaccounts delete [LOGINNAMEorID#]\n\t'\
            'example: iloaccounts delete accountLoginName\n\n'
            '\tDESCRIPTIONS:\n\tLOGINNAME:  The account name, not used ' \
            'to login.\n\tUSERNAME: The account username name, used' \
            ' to login. \n\tPASSWORD:  The account password, used to login.'
            '\n\tId: The number associated with an iLO user account.'\
            '\n\n\tNOTE: please make sure the order of arguments is ' \
            'correct. The\n\tparameters are extracted based on their ' \
            'position in the arguments list.\n\tOnly privileges available to' \
            ' the logged in account can be set to the new account.',\
            summary='Adds / deletes an iLO account on the currently logged ' \
                                                                'in server.',\
            aliases=None,\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commandsDict["LoginCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commandsDict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """ Main iloaccounts function

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

        if len(args) > 4:
            raise InvalidCommandLineError("Invalid number of parameters for "\
                                                                "this command.")

        self.iloaccountsvalidation(options)

        redfish = self._rdmc.app.current_client.monolith.is_redfish
        results = self._rdmc.app.get_handler(self.typepath.defs.accountspath,\
          service=False, silent=True).dict[self.typepath.defs.collectionstring]
        path = None

        if 'Id' not in results[0].keys():
            newresults = []

            for acct in results:
                acct = self._rdmc.app.get_handler(acct[self.typepath.defs.\
                                hrefstring], service=True, silent=True).dict
                newresults.append(acct)

            results = newresults

        if not results:
            raise NoContentsFoundForOperationError("")

        if len(args) == 0:
            sys.stdout.write("iLO Account info: \n[Id]LoginName: "\
                                "\nPrivileges\n-----------------\n")
            for acct in sorted(results, key=lambda k: int(k['Id'])):
                privstr = ""
                privs = acct['Oem'][self.typepath.defs.\
                                            oemhp]['Privileges']
                for priv in privs:
                    privstr += priv + '=' + str(privs[priv]) + '\n'

                sys.stdout.write("[%s] %s:\n%s\n" % (acct['Id'], \
                                acct['Oem'][self.typepath.defs.\
                                            oemhp]['LoginName'], privstr))
        elif args[0].lower() == 'changepass':
            if len(args) == 2:
                sys.stdout.write('Please input the new password.\n')
                tempinput = getpass.getpass()

                if tempinput and tempinput != '\r':
                    tempinput = tempinput
                    args.extend([tempinput])
                else:
                    raise InvalidCommandLineError("Empty or invalid password" \
                                                                    " was entered.")
            if len(args) == 3:
                account = args[1]

                for acct in results:
                    if acct['Id'] == account or acct['Oem'][self.typepath.\
                                                            defs.oemhp]\
                                                    ['LoginName'] == account:
                        if redfish:
                            path = acct['@odata.id']
                            break
                        else:
                            path = acct['links']['self']['href']
                            break

                body = {'Password': args[2]}

                if path and body:
                    self._rdmc.app.patch_handler(path, body, service=True)
                else:
                    raise NoContentsFoundForOperationError('Unable to find '\
                                                'the specified account.')
            else:
                raise InvalidCommandLineError('Invalid number of parameters.')

        elif args[0].lower() == 'add':
            args.remove('add')
            if len(args) == 2:
                sys.stdout.write('Please input the account password.\n')
                tempinput = getpass.getpass()

                if tempinput and tempinput != '\r':
                    tempinput = tempinput
                    args.extend([tempinput])
                else:
                    raise InvalidCommandLineError("Empty or invalid password" \
                                                                    " was entered.")
            if not len(args) == 3:
                raise InvalidCommandLineError('Invalid number of parameters.')

            privs = self.getprivs(options)
            path = self.typepath.defs.accountspath

            body = {"UserName": args[0], "Password": args[2], "Oem": {self.\
                                        typepath.defs.oemhp: {"Privileges": \
                                              privs, "LoginName": args[1]}}}

            self.addvalidation(args[0], args[1], args[2], results)

            if path and body:
                self._rdmc.app.post_handler(path, body)

        elif args[0].lower() == 'delete':
            args.remove('delete')

            try:
                account = args[0]
            except:
                raise InvalidCommandLineError('No item entered to delete.')

            for acct in results:
                if acct['Id'] == account or acct['Oem'][self.typepath.\
                                                    defs.oemhp]\
                                            ['LoginName'] == account:
                    if redfish:
                        path = acct['@odata.id']
                        break
                    else:
                        path = acct['links']['self']['href']
                        break

            if path:
                self._rdmc.app.delete_handler(path)
            else:
                raise NoContentsFoundForOperationError('Unable to find '\
                                            'the specified account.')
        else:
            raise InvalidCommandLineError('Invalid command.')

        return ReturnCodes.SUCCESS

    def getprivs(self, options):
        """ find and return the current available session privileges """
        if self._rdmc.app.current_client:
            sespath = self._rdmc.app.current_client._rest_client.\
                                            _RestClientBase__session_location
            sespath = self._rdmc.app.current_client.\
                                _rest_client.default_prefix + \
                                sespath.split(self._rdmc.app.current_client.\
                                              _rest_client.default_prefix)[-1]

            ses = self._rdmc.app.get_handler(sespath, service=False, \
                                                                    silent=True)

            sesprivs = ses.dict['Oem'][self.typepath.defs.oemhp]['Privileges']

            templist = []
            for key in sesprivs:
                if not sesprivs[key]:
                    templist.append(key)

            if templist:
                for item in templist:
                    del sesprivs[item]

            if options.optprivs:
                for priv in options.optprivs:
                    if priv.keys()[0] in sesprivs.keys():
                        sesprivs.update(priv)

        return sesprivs

    def addvalidation(self, username, loginname, password, accounts):
        """ add validation function

        :param username: username to be added
        :type username: str.
        :param loginname: loginname to be added
        :type loginname: str.
        :param password: password to be added
        :type password: str.
        :param accounts: list of federation accounts
        :type accounts: list.
        """
        for acct in accounts:
            if acct['UserName'] == username or acct['Oem']\
                                    [self.typepath.defs.oemhp]['LoginName']\
                                     == loginname:
                raise AccountExists('Username or login name is already in use.')

        if len(username) >= 60:
            raise InvalidCommandLineError('Username exceeds maximum length.')

        if len(loginname) >= 60:
            raise InvalidCommandLineError('Login name exceeds maximum length.')

        if len(password) >= 40 or len(password) < 8:
            raise InvalidCommandLineError('Password length is invalid.')

    def iloaccountsvalidation(self, options):
        """ add account validation function

        :param options: command line options
        :type options: list.
        """
        inputline = list()

        try:
            self._rdmc.app.get_current_client()
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

            if not len(inputline):
                sys.stdout.write(u'Local login initiated...\n')
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
            '--noremoteconsolepriv',
            dest='optprivs',
            action="append_const",
            const={"RemoteConsolePriv": False},
            help="Optionally include this flag if you wish to set the "\
            "remote console privileges to false."
        )
        customparser.add_option(
            '--noiloconfigpriv',
            dest='optprivs',
            action="append_const",
            const={"iLOConfigPriv": False},
            help="Optionally include this flag if you wish to set the "\
            "ilo config privileges to false."
        )
        customparser.add_option(
            '--novirtualmediapriv',
            dest='optprivs',
            action="append_const",
            const={"VirtualMediaPriv": False},
            help="Optionally include this flag if you wish to set the "\
            "virtual media privileges to false.",
        )
        customparser.add_option(
            '--nouserconfigpriv',
            dest='optprivs',
            action="append_const",
            const={"UserConfigPriv": False},
            help="Optionally include this flag if you wish to set the "\
            "userconfig privileges to false.",
        )
        customparser.add_option(
            '--novirtualprpriv',
            dest='optprivs',
            action="append_const",
            const={"VirtualPowerAndResetPriv": False},
            help="Optionally include this flag if you wish to set the "\
            "virtual power and reset privileges to false.",
        )
        customparser.add_option(
            '--nologinpriv',
            dest='optprivs',
            action="append_const",
            const={"LoginPriv": False},
            help="Optionally include this flag if you wish to set the "\
            "login privileges to false."
        )
        customparser.add_option(
            '--nobiosconfigpriv',
            dest='optprivs',
            action="append_const",
            const={"HostBIOSConfigPriv": False},
            help="Optionally include this flag if you wish to set the "\
            "host BIOS config privileges to false. Only available on gen10"\
            " servers."
        )
        customparser.add_option(
            '--nonicconfigpriv',
            dest='optprivs',
            action="append_const",
            const={"HostNICConfigPriv": False},
            help="Optionally include this flag if you wish to set the "\
            "host NIC config privileges to false. Only available on gen10"\
            " servers."
        )
        customparser.add_option(
            '--nohoststorageconfigpriv',
            dest='optprivs',
            action="append_const",
            const={"HostStorageConfigPriv": False},
            help="Optionally include this flag if you wish to set the "\
            "host storage config privileges to false. Only available on gen10"\
            " servers."
        )
        customparser.add_option(
            '--nosysrecoveryconfigpriv',
            dest='optprivs',
            action="append_const",
            const={"SystemRecoveryConfigPriv": False},
            help="Optionally include this flag if you wish to set the "\
            "system recovery config privileges to false. Only available on gen10"\
            " servers."
        )
