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
""" Add Federation Command for rdmc """

import sys
import getpass

from argparse import ArgumentParser, Action # OptionValueError

from redfish.ris.ris import SessionExpired
from redfish.ris.rmc_helper import IdTokenError

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group
from rdmc_helper import ReturnCodes, InvalidCommandLineError, ResourceExists,\
                InvalidCommandLineErrorOPTS, NoContentsFoundForOperationError,\
                IncompatibleiLOVersionError, Encryption

class _FederationParse(Action):
    def __init__(self, option_strings, dest, nargs, **kwargs):
        super(_FederationParse, self).__init__(option_strings, dest, nargs, **kwargs)
    def __call__(self, parser, namespace, values, option_strings):
        """ Federation privileges option helper"""

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
                                           "match an available privlege." % priv)
                except:
                    raise InvalidCommandLineErrorOPTS("")

    #federation_parse.counter = 0

class IloFederationCommand(RdmcCommandBase):
    """ Add a new ilo federation to the server """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='ilofederation',\
            usage='ilofederation [COMMAND] [ARGUMENTS] [OPTIONS]\n\n\t'\
            'Add an iLO federation group to the current logged in server.'\
            '\n\tilofederation add [FEDERATIONNAME KEY]'\
            '\n\texample: ilofederation add newfedname thisfedkey\n\n\t'\
            'Add an iLO Federation Group to the current server with the following privileges:'\
            '\n\tLogin, iLO Config, Host BIOS Config.\n\t'\
            'ilofederation add [FEDERATIONNAME KEY] --addprivs <list of numbered '\
            'privileges>\n\texample: ilofederation add FEDERATIONNAME FEDKEY'\
            ' --addprivs 1,4,7\n\n\t'\
            'Modify the privileges on an existing federation group.\n\t'\
            'ilofederation modify [FEDNAME] --addprivs <list of numbered privileges>'\
            '--removeprivs <list of numbered privileges>\n\t'\
            'example: ilofederation modify FEDERATIONNAME --addprivs 1,2,3 --removeprivs 4,5,6'\
            '\n\n\tChange the key of an iLO federation group.\n\t'\
            'ilofederation changekey [FEDERATIONNAME NEWKEY]\n\t'\
            'example: ilofederation changekey newfedname newfedkey\n\n\t'\
            'Delete an iLO federation group.\n\t'\
            'ilofederation delete [FEDERATIONNAME]\n\t'\
            'example: ilofederation delete newfedname\n\n\t'\
            'See a list of federations on the system.\n\t'\
            'DESCRIPTIONS:\n\t\n\tFEDERATION: The federation name, used' \
            ' to login. \n\tFEDERATIONKEY:  The federation password, used to login.'
            '\n\tId: The number associated with an iLO Federation.'\
            '\n\n\tPRIVILEGES:\n\t1: Login\n\t2: Remote Console\n\t3: User Config\n\t4: iLO Config'\
            '\n\t5: Virtual Media\n\t6: Virtual Power and Reset\n\n\tiLO 5 added privileges:\n\t7:'\
            ' Host NIC Config\n\t8: Host Bios Config\n\t9: Host Storage Config\n\t10: '\
            'System Recovery Config\n\n\tNOTE: please make sure the order of arguments is ' \
            'correct. The\n\tparameters are extracted based on their ' \
            'position in the arguments list.\n\tBy default only login privilege is added to ' \
            'the newly created federation with role "ReadOnly"\n\tin iLO 5 and no privileges in'\
            ' iLO 4.\n\tTo modify these privileges you can remove properties that would be set by '\
            'using --removeprivs\n\tor you can directly set which privileges are given using'\
            ' --addprivs.\n\n\tNote: federation credentials are case-sensitive.',\
            summary='Adds / deletes an iLO federation group on the currently logged in server.',\
            aliases=['ilofederation'],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)

    def run(self, line):
        """ Main addfederation function

        :param line: string of arguments passed in
        :type line: str.
        """
        mod_fed = None
        valid_args = ['add', 'delete', 'modify', 'changekey']
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
            raise InvalidCommandLineError("Invalid command.")

        self.addfederationvalidation(options)

        redfish = self._rdmc.app.monolith.is_redfish
        path = self.typepath.defs.federationpath
        results = self._rdmc.app.get_handler(path, service=True, silent=True).dict

        newresults = []

        if redfish:
            results = results['Members']
        else:
            results = results['links']['Member']

        for fed in results:
            fed = self._rdmc.app.get_handler(fed[self.typepath.defs.hrefstring], \
                                         service=True, silent=True).dict
            if fed['Name'] in args or fed['Id'] in args:
                mod_fed = fed
                if redfish:
                    path = fed['@odata.id']
                else:
                    path = fed['links']['self']['href']
            newresults.append(fed)
            results = newresults

        fed = mod_fed
        if not results:
            raise NoContentsFoundForOperationError("")

        if not args:
            sys.stdout.write("iLO Federation Id list with Privileges:\n")

            for fed in sorted(results, key=lambda k: k['Name']):
                privstr = ""
                privs = fed['Privileges']

                for priv in privs:
                    privstr += priv + '=' + str(privs[priv]) + '\n'

                sys.stdout.write("\nName=%s:\n%s" % (fed['Name'], privstr))

        elif args[0].lower() == 'add':
            args.remove('add')
            if len(args) == 1:
                sys.stdout.write("Please input the federation key.\n")
                tempinput = getpass.getpass()

                args.extend([tempinput])

            privs = self.getprivs(options)
            path = self.typepath.defs.federationpath

            body = {"Name": args[0], "Key": args[1]}
            if privs:
                body.update({"Privileges": privs})
            self.addvalidation(args[0], args[1], results)

            if path and body:
                resp = self._rdmc.app.post_handler(path, body, response=True)

            if resp and resp.dict:
                if 'resourcealreadyexist' in str(resp.dict).lower():
                    raise ResourceExists('')

        elif args[0].lower() == 'changekey':
            args.remove('changekey')

            try:
                name = args[0]
                newkey = args[1]
            except:
                raise InvalidCommandLineError('Invalid number of parameters.')

            for fed in results:
                if fed['Name'] == name:
                    if redfish:
                        path = fed['@odata.id']
                        break
                    else:
                        path = fed['links']['self']['href']
                        break

            body = {'Key': newkey}

            if path and body:
                self._rdmc.app.patch_handler(path, body, service=True)
            else:
                raise NoContentsFoundForOperationError('Unable to find '\
                                            'the specified federation.')
        elif args[0].lower() == 'modify':
            if not mod_fed:
                raise InvalidCommandLineError("Unable to find the specified federation.")
            body = {}
            args.remove('modify')

            if not len(args) == 1:
                raise InvalidCommandLineError("Invalid number of parameters.")

            if options.optprivs:
                body.update({'Privileges': {}})
                if any(priv for priv in options.optprivs if 'SystemRecoveryConfigPriv' in priv) \
                                                        and 'SystemRecoveryConfigPriv' not in \
                                                        self.getsesprivs().keys():
                    raise IdTokenError("The currently logged in federation must have The System "\
                                       "Recovery Config privilege to add the System Recovery "\
                                       "Config privilege.")
                privs = self.getprivs(options)
                body['Privileges'] = privs

            self._rdmc.app.patch_handler(path, body)

        elif args[0].lower() == 'delete':
            if not mod_fed:
                raise InvalidCommandLineError("Unable to find the specified Federation.")
            args.remove('delete')

            try:
                name = str(args[0])
            except:
                raise InvalidCommandLineError("No Name entered to delete.")

            for fed in results:
                if fed['Name'] == name:
                    if redfish:
                        path = fed['@odata.id']
                        break
                    else:
                        path = fed['links']['self']['href']
                        break

            if not path == self.typepath.defs.federationpath:
                self._rdmc.app.delete_handler(path)
            else:
                raise NoContentsFoundForOperationError('Unable to find the specified federation.')
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
                raise IdTokenError("The currently logged in federation does not have the Config"\
                                   "Privilege and cannot add or modify federations.")

        if options.optprivs:
            for priv in options.optprivs:
                priv = next(iter(priv.keys()))
                if priv not in availableprivs:
                    raise IncompatibleiLOVersionError("Privilege %s is not available on this iLO version."\
                                           % priv)

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
        """Finds and returns the current session's privileges

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

    def addvalidation(self, username, key, feds):
        """ add validation function

        :param username: username to be added
        :type username: str.
        :param key: key to be added
        :type key: str.
        :param feds: list of federation accounts
        :type feds: list.
        """
        for fed in feds:
            if fed['Name'] == username:
                raise ResourceExists('Federation name is already in use.')

        if len(username) >= 32:
            raise InvalidCommandLineError('User name exceeds maximum length.')
        elif len(key) >= 32 or len(key) <= 7:
            raise InvalidCommandLineError('Password is invalid length.')

    def addfederationvalidation(self, options):
        """ addfederation validation function

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
            '--addprivs',
            dest='optprivs',
            nargs='*',
            action=_FederationParse,
            type=str,
            help="Optionally include this flag if you wish to specify "\
            "which privileges you want added to the iLO federation. This overrides the default of "\
            "duplicating privileges of the currently logged in federation on the new federation. "\
            "Pick privileges from the privilege list in the above help text. EX: --addprivs=1,2,4",
            default=None
        )
        customparser.add_argument(
            '--removeprivs',
            dest='optprivs',
            nargs='*',
            action=_FederationParse,
            type=str,
            help="Optionally include this flag if you wish to specify "\
            "which privileges you want removed from the iLO federation. This overrides the default"\
            " of duplicating privileges of the currently logged in federation on the new "\
            "federation. Pick privileges from the privilege list in the above help text. "\
            "EX: --removeprivs=1,2,4",
            default=None
        )
