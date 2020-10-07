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
""" Add Federation Command for rdmc """

import sys
import getpass

from argparse import ArgumentParser, Action, RawDescriptionHelpFormatter

from redfish.ris.ris import SessionExpired
from redfish.ris.rmc_helper import IdTokenError

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group, login_select_validation, \
                                logout_routine
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

class IloFederationCommand(RdmcCommandBase):
    """ Add a new ilo federation to the server """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='ilofederation',\
            usage=None,\
            description='View, Add, Remove and Modify iLO Federation accoutns based on the '\
            'sub-command used.\nTo view help on specific sub-commands run: ilofederation '\
            '<sub-command> -h\n\nExample: ilofederation add -h\n'\
            'NOTE 1: By default only the login privilege is added to the newly created\n\t\t'\
            'federation group with role "ReadOnly" in iLO 5 and no privileges in iLO 4.\n\t'\
            'NOTE 2: Federation credentials are case-sensitive.',
            summary='Adds / deletes an iLO federation group on the currently logged in server.',\
            aliases=['ilofederation'])
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath

    def run(self, line):
        """ Main addfederation function

        :param line: string of arguments passed in
        :type line: str.
        """
        mod_fed = None
        body = dict()
        try:
            (options, _) = self._parse_arglist(line, default=True)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.addfederationvalidation(options)

        redfish = self._rdmc.app.monolith.is_redfish
        path = self.typepath.defs.federationpath
        results = self._rdmc.app.get_handler(path, service=True, silent=False).dict

        newresults = []

        if redfish:
            results = results['Members']
        else:
            results = results['links']['Member']

        for fed in results:
            fed = self._rdmc.app.get_handler(fed[self.typepath.defs.hrefstring], \
                                         service=True, silent=True).dict
            if hasattr(options, 'fedname') or hasattr(options, 'fedkey'):
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

        if options.command.lower() == 'add':
            privs = self.getprivs(options)
            path = self.typepath.defs.federationpath

            body = {"Name": options.fedname, "Key": options.fedkey}
            if privs:
                body.update({"Privileges": privs})
            self.addvalidation(options.fedname, options.fedkey, results)

            if path and body:
                resp = self._rdmc.app.post_handler(path, body)

            if resp and resp.dict:
                if 'resourcealreadyexist' in str(resp.dict).lower():
                    raise ResourceExists('')

        elif options.command.lower() == 'changekey':

            try:
                name = options.fedname
                newkey = options.fedkey
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
        elif options.command.lower() == 'modify':
            if not mod_fed:
                raise InvalidCommandLineError("Unable to find the specified federation.")

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

        elif options.command.lower() == 'delete':
            if not mod_fed:
                raise InvalidCommandLineError("Unable to find the specified Federation.")

            name = options.fedname

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
            sys.stdout.write("iLO Federation Id list with Privileges:\n")

            for fed in sorted(results, key=lambda k: k['Name']):
                privstr = ""
                privs = fed['Privileges']

                for priv in privs:
                    privstr += priv + '=' + str(privs[priv]) + '\n'

                sys.stdout.write("\nName=%s:\n%s" % (fed['Name'], privstr))

        logout_routine(self, options)
        #Return code
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
        login_select_validation(self, options)

    @staticmethod
    def options_addprivs_argument_group(parser):
        """ Define optional arguments group

        :param parser: The parser to add the addprivs option group to
        :type parser: ArgumentParser/OptionParser
        """
        group = parser.add_argument_group('GLOBAL OPTION:', 'Option(s) are available for'\
                                          ' all arguments within the scope of this subcommand.')

        parser.add_argument(
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

    @staticmethod
    def options_removeprivs_argument_group(parser):
        """ Additional argument

        :param parser: The parser to add the removeprivs option group to
        :type parser: ArgumentParser/OptionParser
        """

        group = parser.add_argument_group('GLOBAL OPTION:', 'Option(s) are available'\
                                          'for all arguments within the scope of this command.')
        parser.add_argument(
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

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        add_login_arguments_group(customparser)
        subcommand_parser = customparser.add_subparsers(dest='command')
        privilege_help='\n\nPRIVILEGES:\n\t1: Login\n\t2: Remote Console\n\t3: User Config\n\t4:'\
            ' iLO Config\n\t5: Virtual Media\n\t6: Virtual Power and Reset\n\n\tiLO 5 added '\
            'privileges:\n\t7: Host NIC Config\n\t8: Host Bios Config\n\t9: Host Storage Config'\
            '\n\t10: System Recovery Config'
        #default sub-parser
        default_parser = subcommand_parser.add_parser(
            'default',
            help='Running without any sub-command will return all federation group information '\
            ' on the currently logged in server.'
        )
        add_login_arguments_group(default_parser)
        #add sub-parser
        add_help='Adds an iLO federation group to the currently logged in server. Federation '\
                 'group privileges may be specified with\n\"--addprivs\". If a federation key '\
                 'is not '\
                 'provided, the user will be prompted to provide one prior to account creation.'
        add_parser = subcommand_parser.add_parser(
            'add',
            help=add_help,
            description=add_help+'\n\tilofederation add [FEDERATIONNAME] [FEDERATIONKEY] ' +\
            privilege_help+ '\n\tilofederation add newilofedname thisfedkey --addprivs 1,3,4',
            formatter_class=RawDescriptionHelpFormatter
        )
        add_parser.add_argument(
            'fedname',
            help= 'Federation name of the federation group to add.',
            type= str,
            metavar='FEDERATION KEY',
        )
        add_parser.add_argument(
            'fedkey',
            help= 'Federation key of the federation group to add.',
            type= str,
            metavar='FEDERATION KEY',
        )
        self.options_addprivs_argument_group(add_parser)
        add_login_arguments_group(add_parser)

        modify_help='Modify the privileges on an existing federation group.'
        modify_parser = subcommand_parser.add_parser(
            'modify',
            help=modify_help,
            description=modify_help+"\n\nTo add privileges:\n\tilofederation modify "\
            "[FEDNAME] --addprivs <list of numbered privileges>\n\nTo remove privileges:\n\t"\
            "ilofederation modify [FEDNAME] --removeprivs <list of numbered privileges>\n\n"\
            +privilege_help,
            formatter_class=RawDescriptionHelpFormatter
        )
        modify_parser.add_argument(
            'fedname',
            help='The federation name of the iLO account to modify.',
            metavar='FEDERATION NAME',
            type= str,
        )
        self.options_addprivs_argument_group(modify_parser)
        self.options_removeprivs_argument_group(modify_parser)
        add_login_arguments_group(modify_parser)

        #changepass sub-parser
        changekey_help='Change the key of an iLO federation group on the currently logged in '\
                       'server.'
        changekey_parser = subcommand_parser.add_parser(
            'changekey',
            help=changekey_help,
            description=changekey_help+'\n\nexample:ilofederation changekey [FEDNAME] [NEWFEDKEY]',
            formatter_class=RawDescriptionHelpFormatter
        )
        changekey_parser.add_argument(
            'fedname',
            help='The iLO federation account to be updated with a new federation key (password).',
            metavar='FEDERATION NAME',
            type= str,
        )
        changekey_parser.add_argument(
            'fedkey',
            help='The federation key (password) to be altered for the selected iLO federation '\
            ' account. If you do not include a federation key, you will be prompted to enter one.',
            metavar='FEDERATION KEY',
            type= str,
            nargs='?',
            default=''
        )
        add_login_arguments_group(changekey_parser)

        #delete sub-parser
        delete_help='Deletes the provided iLO user account on the currently logged in server.'
        delete_parser = subcommand_parser.add_parser(
            'delete',
            help=delete_help,
            description=delete_help+'\n\nexample: ilofederation delete fedname',
            formatter_class=RawDescriptionHelpFormatter
        )
        delete_parser.add_argument(
            'fedname',
            help='The iLO federation account to delete.',
            metavar='FEDERATION NAME',
            type= str,
        )
        add_login_arguments_group(delete_parser)
