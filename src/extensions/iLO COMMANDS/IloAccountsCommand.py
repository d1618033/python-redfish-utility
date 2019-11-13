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
""" Add Account Command for rdmc """

import os
import sys
import json
import getpass

from argparse import ArgumentParser, Action

from redfish.ris.ris import SessionExpired
from redfish.ris.rmc_helper import IdTokenError

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group
from rdmc_helper import ReturnCodes, InvalidCommandLineError, ResourceExists, \
                InvalidCommandLineErrorOPTS, NoContentsFoundForOperationError, \
                IncompatibleiLOVersionError, Encryption, InvalidFileInputError

class _AccountParse(Action):
    def __init__(self, option_strings, dest, nargs, **kwargs):
        super(_AccountParse, self).__init__(option_strings, dest, nargs, **kwargs)
    def __call__(self, parser, namespace, values, option_strings):
        """ Account privileges option helper"""

        privkey = {1: 'LoginPriv', 2: 'RemoteConsolePriv', 3:'UserConfigPriv', 4:'iLOConfigPriv', \
         5: 'VirtualMediaPriv', 6: 'VirtualPowerAndResetPriv', 7: 'HostNICConfigPriv', \
         8: 'HostBIOSConfigPriv', 9: 'HostStorageConfigPriv', 10: 'SystemRecoveryConfigPriv'}

        for priv in next(iter(values)).split(','):
            try:
                priv = int(priv)
            except ValueError:
                try:
                    parser.error("Invalid privilege entered: %s. Privileges must " \
                                           "be numbers." % priv)
                except:
                    raise InvalidCommandLineErrorOPTS("")
            try:
                if not isinstance(namespace.optprivs, list):
                    namespace.optprivs = list()
                if option_strings.startswith('--add'):
                    namespace.optprivs.append({privkey[priv]: True})
                elif option_strings.startswith('--remove'):
                    namespace.optprivs.append({privkey[priv]: False})
            except KeyError:
                try:
                    parser.error("Invalid privilege entered: %s. Number does not " \
                                           "match an available privilege." % priv)
                except:
                    raise InvalidCommandLineErrorOPTS("")
    #account_parse.counter = 0

class IloAccountsCommand(RdmcCommandBase):

    """ command to manipulate/add ilo user accounts """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='iloaccounts',\
            usage='iloaccounts [COMMAND] [ARGUMENTS] [OPTIONS]\n\n\t'\
            'Add an iLO user account the current logged in server with the following privileges:'\
            '\n\tLogin, iLO Config, Host BIOS Config.\n\t' \
            'iloaccounts add [USERNAME LOGINNAME PASSWORD] --addprivs <list of numbered '\
            'privileges>\n\texample: iloaccounts add USERNAME ACCOUNTNAME PASSWORD' \
            ' --addprivs 1,4,7\n\n\tChange the password of an account.\n\t'\
            'iloaccounts changepass [USERNAMEorID# PASSWORD]\n\t'\
            'example: iloaccounts changepass 2 newpassword\n\n\t'\
            'Get Id, Username, LoginName, and Privileges info of iLO user accounts.\n\t'\
            'example: iloaccounts\n\n\tModify an iLO account\'s privileges:\n\texample: '\
            'iloaccounts modify USERNAMEorID# --addprivs 3,5 --removeprivs 10\n\n\t'\
            'Delete an iLO account.\n\t'\
            'iloaccounts delete [USERNAMEorID#]\n\t'\
            'example: iloaccounts delete accountUserName\n\n\t'\
            'Add a certificate to a user account.\n\t'\
            'iloaccounts addcert [USERNAMEorID#] <path to an x.509 certification string>\n\t'\
            'example: iloaccounts addcert accountUserName C:\Users\user\cert.txt\n\n\t'\
            'Delete a certificate from an iLO account.\n\t'\
            'example: iloaccounts deletecert [USERNAMEorID#]\n\n'\
            '\tDESCRIPTIONS:\n\tNOTE: UserName and LoginName are reversed '\
            'in the GUI for Redfish compatibility.'\
            '\n\tLOGINNAME:  The account name, not used '\
            'to login.\n\tUSERNAME: The account username name, used'\
            ' to login. \n\tPASSWORD:  The account password, used to login.'\
            '\n\tId: The number associated with an iLO user account.'\
            '\n\n\tPRIVILEGES:\n\t1: Login\n\t2: Remote Console\n\t3: User Config\n\t4: iLO Config'\
            '\n\t5: Virtual Media\n\t6: Virtual Power and Reset\n\n\tiLO 5 added privileges:\n\t7:'\
            ' Host NIC Config\n\t8: Host Bios Config\n\t9: Host Storage Config\n\t10: '\
            'System Recovery Config\n\n\tNOTE: please make sure the order of arguments is '\
            'correct. The\n\tparameters are extracted based on their ' \
            'position in the arguments list.\n\tBy default only login privilege is added to '\
            'the newly created account with role "ReadOnly"\n\tin iLO 5 and no privileges in'\
            ' iLO 4.\n\tTo modify these privileges you can remove properties that would be set by '\
            'using --removeprivs\n\tor you can directly set which privileges are given using'\
            ' --addprivs.\n\n\tNote: account credentials are case-sensitive.',\
            summary='Adds / deletes an iLO account on the currently logged in server.',\
            aliases=['iloaccount'],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """ Main iloaccounts function

        :param line: string of arguments passed in
        :type line: str.
        """
        mod_acct = None
        valid_args = ['add', 'delete', 'modify', 'changepass', 'addcert', 'deletecert']
        try:
            (options, args) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        if len(args) > 4:
            raise InvalidCommandLineError("Invalid number of parameters for "\
                                                                "this command.")
        arg_cnt = 0
        for arg in args:
            if arg in valid_args:
                arg_cnt += 1
        if arg_cnt > 1:
            raise InvalidCommandLineError('Invalid command.')

        self.iloaccountsvalidation(options)

        redfish = self._rdmc.app.monolith.is_redfish
        path = self.typepath.defs.accountspath
        results = self._rdmc.app.get_handler(path, service=True, silent=True).dict

        newresults = []

        if redfish:
            results = results['Members']
        else:
            results = results['links']['Member']

        for acct in results:
            acct = self._rdmc.app.get_handler(acct[self.typepath.defs.hrefstring],\
                                                                service=True, silent=True).dict
            if acct['Id'] in args or acct['UserName'] in args:
                mod_acct = acct
                if redfish:
                    path = acct['@odata.id']
                else:
                    path = acct['links']['self']['href']
            newresults.append(acct)
            results = newresults

        acct = mod_acct
        if not results:
            raise NoContentsFoundForOperationError("")

        outdict = dict()
        if not args:
            if not options.json:
                sys.stdout.write("iLO Account info: \n[Id] UserName (LoginName): "\
                                "\nPrivileges\n-----------------\n")
            for acct in sorted(results, key=lambda k: int(k['Id'])):
                privstr = ""
                privs = acct['Oem'][self.typepath.defs.oemhp]['Privileges']

                if 'ServiceAccount' in list(acct['Oem'][self.typepath.defs.oemhp].keys()) and \
                acct['Oem'][self.typepath.defs.oemhp]['ServiceAccount']:
                    service = 'ServiceAccount=True'
                else:
                    service = 'ServiceAccount=False'
                if not options.json:
                    for priv in privs:
                        privstr += priv + '=' + str(privs[priv]) + '\n'
                    sys.stdout.write("[%s] %s (%s):\n%s\n%s\n" % (acct['Id'], acct['UserName'], \
                            acct['Oem'][self.typepath.defs.oemhp]['LoginName'], service, privstr))
                keyval = '['+str(acct['Id'])+'] '+acct['UserName']
                outdict[keyval] = privs
                outdict[keyval]['ServiceAccount'] = service.split('=')[-1].lower()
            if options.json:
                sys.stdout.write(str(json.dumps(outdict, indent=2, sort_keys=True)))
                sys.stdout.write('\n')
        elif args[0].lower() == 'changepass':
            if not mod_acct:
                raise InvalidCommandLineError("Unable to find the specified account.")
            if len(args) == 2:
                sys.stdout.write('Please input the new password.\n')
                tempinput = getpass.getpass()
                self.credentialsvalidation('', '', tempinput, '', True)
                args.extend([tempinput])
            if len(args) == 3:
                account = args[1].lower()
                self.credentialsvalidation('', '', args[2].split('\r')[0], '', True)
                body = {'Password': args[2].split('\r')[0]}

                if path and body:
                    self._rdmc.app.patch_handler(path, body)
                else:
                    raise NoContentsFoundForOperationError('Unable to find the specified account.')
            else:
                raise InvalidCommandLineError('Invalid number of parameters.')

        elif args[0].lower() == 'add':
            args.remove('add')
            if len(args) == 2:
                sys.stdout.write('Please input the account password.\n')
                tempinput = getpass.getpass()

                self.credentialsvalidation('', '', tempinput, '', True)
                args.extend([tempinput])

            if not len(args) == 3:
                raise InvalidCommandLineError('Invalid number of parameters.')

            privs = self.getprivs(options)
            path = self.typepath.defs.accountspath

            body = {"UserName": args[0], "Password": args[2], "Oem": {self.\
                                        typepath.defs.oemhp: {"LoginName": args[1]}}}
            if privs:
                body["Oem"][self.typepath.defs.oemhp].update({"Privileges": privs})
            self.credentialsvalidation(args[0], args[1], args[2], results, True)
            if options.serviceacc:
                body["Oem"][self.typepath.defs.oemhp].update({"ServiceAccount": True})
            if options.role:
                if self._rdmc.app.getiloversion() >= 5.140:
                    body["RoleId"] = options.role
                else:
                    raise IncompatibleiLOVersionError("Roles can only be set in iLO 5"\
                                                                                " 1.40 or greater.")
            if path and body:
                self._rdmc.app.post_handler(path, body)
        elif args[0].lower() == 'modify':
            if not mod_acct:
                raise InvalidCommandLineError("Unable to find the specified account.")
            body = {}
            args.remove('modify')

            if not len(args) == 1:
                raise InvalidCommandLineError("Invalid number of parameters.")

            if options.optprivs:
                body.update({'Oem': {self.typepath.defs.oemhp: {'Privileges': {}}}})
                if any(priv for priv in options.optprivs if 'SystemRecoveryConfigPriv' in priv) \
                                                            and 'SystemRecoveryConfigPriv' not in \
                                                                        self.getsesprivs().keys():
                    raise IdTokenError("The currently logged in account must have The System "\
                                         "Recovery Config privilege to add the System Recovery "\
                                         "Config privilege.")
                privs = self.getprivs(options)
                body['Oem'][self.typepath.defs.oemhp]['Privileges'] = privs

            if options.role and self._rdmc.app.getiloversion >= 5.140:
                body["RoleId"] = options.role

            self._rdmc.app.patch_handler(path, body)

        elif args[0].lower() == 'delete':
            if not mod_acct:
                raise InvalidCommandLineError("Unable to find the specified account.")
            self._rdmc.app.delete_handler(path)

        elif 'cert' in args[0].lower():
            certpath = '/redfish/v1/AccountService/UserCertificateMapping/'
            privs = self.getsesprivs()
            if self.typepath.defs.isgen9:
                IncompatibleiLOVersionError("This operation is only available on gen 10 "\
                                                  "and newer machines.")
            elif privs['UserConfigPriv'] == False:
                raise IdTokenError("The currently logged in account must have The User "\
                                     "Config privilege to manage certificates for users.")
            else:
                if args[0].lower() == 'addcert':
                    if not mod_acct:
                        raise InvalidCommandLineError("Unable to find the specified account.")
                    body = {}
                    args.remove('addcert')
                    username = acct['UserName']
                    account = acct['Id']
                    if not len(args) == 2:
                        raise InvalidCommandLineError("Invalid number of parameters.")
                    fingerprintfile = args[1]
                    if os.path.exists(fingerprintfile):
                        with open(fingerprintfile, 'r') as fingerfile:
                            fingerprint = fingerfile.read()
                    else:
                        raise InvalidFileInputError('%s cannot be read.' % fingerprintfile)
                    body = {"Fingerprint": fingerprint, "UserName": username}
                    self._rdmc.app.post_handler(certpath, body)
                
                elif args[0].lower() == 'deletecert':
                    if not mod_acct:
                        raise InvalidCommandLineError("Unable to find the specified account.")
                    args.remove('deletecert')
                    certpath += acct['Id']
                    self._rdmc.app.delete_handler(certpath)

        else:
            raise InvalidCommandLineError('Invalid command.')

        return ReturnCodes.SUCCESS

    def getprivs(self, options):
        """ find and return the privileges to set

        :param options: command line options
        :type options: list.
        """
        sesprivs = self.getsesprivs()
        setprivs = {}
        availableprivs = self.getsesprivs(availableprivsopts=True)

        if not 'UserConfigPriv' in sesprivs.keys():
                raise IdTokenError("The currently logged in account does not have the User Config "\
                                 "privilege and cannot add or modify user accounts.")

        if options.optprivs:
            for priv in options.optprivs:
                priv = next(iter(priv.keys()))
                if priv not in availableprivs:
                    raise IncompatibleiLOVersionError("Privilege %s is not available on this "\
                                                                            "iLO version." % priv)

            if all(priv.values()[0] for priv in options.optprivs):
                if any(priv for priv in options.optprivs if 'SystemRecoveryConfigPriv' in priv) and\
                                            'SystemRecoveryConfigPriv' not in sesprivs.keys():
                    raise IdTokenError("The currently logged in account must have The System "\
                                     "Recovery Config privilege to add the System Recovery "\
                                     "Config privilege.")
                else:
                    setprivs = {}
            for priv in options.optprivs:
                setprivs.update(priv)

        return setprivs

    def getsesprivs(self, availableprivsopts=False):
        """Finds and returns the curent session's privileges
        
        :param availableprivsopts: return available privileges
        :type availableprivsopts: boolean.
        """
        if self._rdmc.app.current_client:
            sespath = self._rdmc.app.current_client.session_location
            sespath = self._rdmc.app.current_client.default_prefix + \
                                sespath.split(self._rdmc.app.current_client.\
                                              default_prefix)[-1]

            ses = self._rdmc.app.get_handler(sespath, service=False, silent=True)

            if not ses:
                raise SessionExpired("Invalid session. Please logout and "\
                                    "log back in or include credentials.")

            sesprivs = ses.dict['Oem'][self.typepath.defs.oemhp]['Privileges']
            availableprivs = ses.dict['Oem'][self.typepath.defs.oemhp]['Privileges'].keys()
            for priv, val in sesprivs.items():
                if not val:
                    del sesprivs[priv]
        else:
            sesprivs = None
        if availableprivsopts:
            return availableprivs
        else:
            return sesprivs

    def credentialsvalidation(self, username='', loginname='', password='', accounts=[], \
                                                                            check_password=False):
        """ sanity validation of credentials
        :param username: username to be added
        :type username: str.
        :param loginname: loginname to be added
        :type loginname: str.
        :param password: password to be added
        :type password: str.
        :param accounts: list of federation accounts
        :type accounts: list.
        :param check_password: flag to check password
        :type check_password: bool.
        """
        username_max_chars = 39 #60
        loginname_max_chars = 39 #60
        password_max_chars = 39 #PASSWORD MAX CHARS
        password_min_chars = 8  #PASSWORD MIN CHARS

        password_min_chars = next(iter(self._rdmc.app.select(\
                'AccountService.'))).dict['Oem'][self.typepath.defs.oemhp]['MinPasswordLength']

        if username != '' and loginname != '':
            for acct in accounts:
                if acct['UserName'] == username or acct['Oem']\
                                    [self.typepath.defs.oemhp]['LoginName'] == loginname:
                    raise ResourceExists('Username or login name is already in use.')

            if len(username) > username_max_chars:
                raise InvalidCommandLineError('Username exceeds maximum length'\
                    '. Use at most %s characters.' % username_max_chars)

            if len(loginname) > loginname_max_chars:
                raise InvalidCommandLineError('Login name exceeds maximum '\
                    'length. Use at most %s characters.' % loginname_max_chars)

        if check_password:
            if password == '' or password == '/r':
                raise InvalidCommandLineError('An invalid password was entered.')
            else:
                if len(password) > password_max_chars:
                    raise InvalidCommandLineError('Password length is invalid.'\
                            ' Use at most %s characters.' % password_max_chars)
                if len(password) < password_min_chars:
                    raise InvalidCommandLineError('Password length is invalid.'\
                            ' Use at least %s characters.' % password_min_chars)

    def iloaccountsvalidation(self, options):
        """ add account validation function

        :param options: command line options
        :type options: list.
        """
        inputline = list()

        try:
            _ = self._rdmc.app.current_client
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
            '--serviceaccount',
            dest='serviceacc',
            action="store_true",
            help="Optionally include this flag if you wish to created account "\
            "to be a service account.",
            default=False
        )
        customparser.add_argument(
            '--addprivs',
            dest='optprivs',
            nargs='*',
            action=_AccountParse,
            type=str,
            help="Optionally include this flag if you wish to specify "\
            "which privileges you want added to the iLO account. This overrides the default of "\
            "duplicating privileges of the currently logged in account on the new account. Pick "\
            "privileges from the privilege list in the above help text. EX: --addprivs=1,2,4",
            default=None
        )
        customparser.add_argument(
            '--removeprivs',
            dest='optprivs',
            nargs='*',
            action=_AccountParse,
            type=str,
            help="Optionally include this flag if you wish to specify "\
            "which privileges you want removed from the iLO account. This overrides the default of"\
            " duplicating privileges of the currently logged in account on the new account. Pick "\
            "privileges from the privilege list in the above help text. EX: --removeprivs=1,2,4",
            default=None
        )
        customparser.add_argument(
            '--role',
            dest='role',
            choices=['Administrator', 'ReadOnly', 'Operator'],
            help="Optionally include this flag if you would like to specify Privileges by role. "\
                "Valid choices are: Administrator, ReadOnly, Operator",
            default=None
        )
        customparser.add_argument(
            '-j',
            '--json',
            dest='json',
            action="store_true",
            help="Optionally include this flag if you wish to change the"\
            " displayed output to JSON format. Preserving the JSON data"\
            " structure makes the information easier to parse.",
            default=False
        )
