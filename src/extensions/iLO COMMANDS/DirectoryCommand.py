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
""" Directory Command for rdmc """

import re
import sys
import getpass

from optparse import OptionParser, OptionValueError, SUPPRESS_HELP

from redfish.ris.rmc_helper import IloResponseError

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, IncompatibleiLOVersionError,\
                    InvalidCommandLineErrorOPTS, NoContentsFoundForOperationError, UI,\
                    ResourceExists, Encryption

def directory_parse(option, opt_str, value, parser):
    """ Helper for parsing options """
    if opt_str.endswith('disable'):
        parser.values.enable = False
    elif opt_str.endswith('enable'):
        parser.values.enable = True
    elif opt_str.endswith('enablelocalauth'):
        parser.values.localauth = False
    elif opt_str.endswith('disablelocalauth'):
        parser.values.localauth = True
    elif opt_str == '--removerolemap':
        setattr(parser.values, option.dest, {'remove': []})
        for role in value.split(','):
            role = role.replace('"', '')
            if role:
                parser.values.roles['remove'].append(role)
    elif opt_str == '--addrolemap':
        setattr(parser.values, option.dest, {'add': []})
        for role in value.split(','):
            role = role.replace('"', '')
            if role and re.match('.*:.*', role):
                parser.values.roles['add'].append(role)
            else:
                raise OptionValueError("Supply roles to add in form <local role>:<remote group>")
    elif opt_str == '--addsearch':
        setattr(parser.values, option.dest, {'add': []})
        for search in value.split(','):
            if search:
                parser.values.search['add'].append(search)
    elif opt_str == '--removesearch':
        setattr(parser.values, option.dest, {'remove': []})
        for search in value.split(','):
            if search:
                parser.values.search['remove'].append(search)

class DirectoryCommand(RdmcCommandBase):
    """ Update directory settings on the server """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='directory',\
            usage='directory [kerberos/ldap/test] [OPTIONS]\n\n\t'\
            'Add credentials, service address, two search strings, and enable LDAP directory'\
            ' service.\n\texample: directory ldap --serviceaddress x.x.y.z --addsearch string1,'\
            'string2 --enable username password\n\n\tAdd service address, port, and realm for '\
            'Kerberos.\n\texample: directory kerberos --serviceaddress x.x.y.z --port 8888 '\
            '--realm arealm\n\n\tAdd 2 directory roles.\n\texample:directory ldap --addrolemap '\
            '"LocalRole1:RemoteGroup3,LocalRole2:RemoteGroup4:SID"\n\n\tRemove 2 directory '\
            'roles.\n\texample: directory ldap --removerolemap LocalRole1,LocalRole2\n\n\tStart a '\
            'directory test.\n\texample: directory test start\n\n\tStop a directory test\n\t'\
            'example: directory test stop\n\n\tView results of the last directory test.\n\t'\
            'example: directory test viewresults\n\n\tNOTE: When adding role map SID is optional.',\
            summary='Update directory settings, add/delete directory roles, and test directory '\
                    'settings.',\
            aliases=['ad', 'activedirectory'],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)

    def run(self, line):
        """Main directory Function

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

        self.directoryvalidation(options)
        if self._rdmc.app.getiloversion() < 5.140:
            raise IncompatibleiLOVersionError("Directory settings are only available on "\
                                                                        "iLO 5 1.40 or greater.")
        if len(args) < 1 or len(args) > 3:
            raise InvalidCommandLineError("Invalid number of arguments entered.")
        elif len(args) == 3 and args[0].lower() == 'kerberos':
            raise InvalidCommandLineError("Username and password can only be set for LDAP.")
        elif len(args) == 2 and args[0].lower() in ['ldap']:
            sys.stdout.write('Please input the password for the directory.\n')
            tempinput = getpass.getpass()
            args.extend([tempinput])

        elif len(args) == 2 and args[0].lower() == 'test':
            if not args[1] in ['start', 'stop', 'viewresults']:
                raise InvalidCommandLineError('Please input "start" to start the directory test, '\
                        '"stop" to stop the directory test, or "viewresults" to see the results of'\
                        ' the last directory test.')

        results = None

        if args[0].lower() == 'ldap':
            if options.realm or options.keytab:
                raise InvalidCommandLineError("Keytab and Realm options are not available for "\
                                              "LDAP.")
            try:
                results = self._rdmc.app.select(selector='AccountService.', rel=True)[0].dict
                path = results[self._rdmc.app.typepath.defs.hrefstring]
                oem = results['Oem'][self.typepath.defs.oemhp]
                local_auth = results['LocalAccountAuth']
                results = results['LDAP']
                name = 'LDAP'
            except (KeyError, IndexError):
                raise NoContentsFoundForOperationError("Unable to gather LDAP settings.")

        elif args[0].lower() == 'kerberos':
            if options.authmode or options.search:
                raise InvalidCommandLineError("Authentication and add/remove search options "\
                                              "are not available for Kerberos.")
            try:
                results = self._rdmc.app.select(selector='AccountService.', rel=True)[0].dict
                path = results[self._rdmc.app.typepath.defs.hrefstring]
                oem = results['Oem'][self.typepath.defs.oemhp]
                local_auth = results['LocalAccountAuth']
                results = results['ActiveDirectory']
                name = 'ActiveDirectory'
            except (KeyError, IndexError):
                raise NoContentsFoundForOperationError("Unable to gather Kerberos settings.")

        elif not args[0].lower() == 'test':
            raise InvalidCommandLineError("Please choose LDAP, Kerberos to read or modify "\
                                    "directory settings or test to test directory settings.")

        if results:
            keytab = None
            payload = {}
            if options.keytab:
                keytab = options.keytab
            try:
                directory_settings = self.directory_helper(results, options, args[1], args[2])
            except IndexError:
                directory_settings = self.directory_helper(results, options)

            if directory_settings:
                payload[name] = directory_settings

            if options.authmode:
                payload.update({'Oem':{'Hpe':{'DirectorySettings': \
                                              {'LdapAuthenticationMode': options.authmode}}}})
            
            if not payload and not keytab:
                if options.json:
                    UI().print_out_json({name: results, 'LocalAccountAuth': local_auth, \
                                         "Oem": {"Hpe": oem}})
                else:
                    self.print_settings(results, oem, local_auth, name)

            if payload:
                if options.localauth:
                    payload['LocalAccountAuth'] = 'Enabled' if options.localauth else 'Disabled'
                sys.stdout.write("Changing settings...\n")
                try:
                    self._rdmc.app.patch_handler(path, payload)
                except IloResponseError:
                    if len(args) == 3 and not results['ServiceEnabled']:
                        sys.stderr.write("You must enable this directory service before or during"\
                        " assignment of username and password. Try adding the flag --enable.\n")
                        raise IloResponseError("")
                    else:
                        raise
            if keytab:
                path = oem['Actions'][next(iter(oem['Actions']))]['target']
                sys.stdout.write("Adding keytab...\n")
                self._rdmc.app.post_handler(path, {"ImportUri": keytab})
        else:
            self.test_directory(args[1], json=options.json)

        return ReturnCodes.SUCCESS

    def directory_helper(self, settings, options, username=None, password=None):
        """ Helper function to set the payload based on options and arguments

        :param settings: dictionary to change
        :type settings: dict.
        :param options: list of options
        :type options: list.
        :param username: username to apply
        :type username: str.
        :param password: password to apply
        :type password: str.
        """

        payload = {}
        serviceaddress = None

        if isinstance(options.serviceaddress, str):
            serviceaddress = options.serviceaddress
            if serviceaddress == '""' or serviceaddress == "''":
                serviceaddress = ''
        if isinstance(options.port, str):
            if serviceaddress is None:
                serviceaddress = settings['ServiceAddresses'][0]
            serviceaddress = serviceaddress + ':' + options.port
        if isinstance(options.realm, str):
            if serviceaddress is None:
                serviceaddress = settings['ServiceAddresses'][0]
            if options.realm == '""' or options.realm == "''":
                options.realm = ''
            serviceaddress = serviceaddress + '@' + options.realm
        if not serviceaddress is None:
            payload['ServiceAddresses'] = [serviceaddress]

        if not options.enable is None:
            payload['ServiceEnabled'] = options.enable

        if username and password:
            payload.update({"Authentication":{"Username": username, "Password": password}})

        if options.roles:
            payload['RemoteRoleMapping'] = self.role_helper(options.roles, \
                                                                    settings['RemoteRoleMapping'])

        if options.search:
            payload.update({"LDAPService": {"SearchSettings": self.search_helper(options.search, \
                                                    settings['LDAPService']['SearchSettings'])}})

        return payload

    def test_directory(self, command, json=False):
        """ Function to perform directory testing

        :param command: command to run against directory test. (start/stop/viewresults)
        :type command: str.
        :param json: Bool to print in json format or not.
        :type json: bool.
        """
        results = self._rdmc.app.select(selector='HpeDirectoryTest.', rel=True)[0].dict
        if command.lower() == 'start':
            path = None
            for item in results['Actions']:
                if 'StartTest' in item:
                    path = results['Actions'][item]['target']
                    break
            if not path:
                raise NoContentsFoundForOperationError("Unable to start directory test.")
            sys.stdout.write("Starting the directory test. Monitor results with command: directory"\
                             " viewresults\n")
            self._rdmc.app.post_handler(path, {})
        elif command.lower() == 'stop':
            path = None
            for item in results['Actions']:
                if 'StopTest' in item:
                    path = results['Actions'][item]['target']
                    break
            if not path:
                raise NoContentsFoundForOperationError("Unable to stop directory test.")
            sys.stdout.write("Stopping the directory test.\n")
            self._rdmc.app.post_handler(path, {})
        elif command.lower() == 'viewresults':
            if json:
                UI().print_out_json(results['TestResults'])
            else:
                for test in results['TestResults']:
                    sys.stdout.write('Test: %s\n' % test['TestName'])
                    sys.stdout.write("------------------------\n")
                    sys.stdout.write('Status: %s\n' % test['Status'])
                    sys.stdout.write('Notes: %s\n' % test['Notes'])
                    sys.stdout.write("\n")

    def print_settings(self, settings, oem_settings, local_auth_setting, name):
        """ Pretty print settings of LDAP or Kerberos

        :param settings: settings to print
        :type settings: dict.
        :param oem_settings: oem_settings to print
        :type oem_settings: dict.
        :param local_auth_settings: local authorization setting
        :type local_auth_settings: str.
        :param name: type of setting (activedirectory or ldap)
        :type name: str.
        """
        sys.stdout.write("%s settings:\n" % ('Kerberos' if name == 'ActiveDirectory' else name))
        sys.stdout.write("--------------------------------\n")
        sys.stdout.write("Enabled: %s\n" % str(settings['ServiceEnabled']))

        serviceaddress = settings['ServiceAddresses'][0]

        sys.stdout.write("Service Address: %s\n" % (serviceaddress if serviceaddress else \
                                                                                        "Not Set"))

        sys.stdout.write("Local Account Authorization: %s\n" % local_auth_setting)

        if name.lower() == 'activedirectory':
            address_settings = oem_settings['KerberosSettings']
            sys.stdout.write("Port: %s\n" % address_settings['KDCServerPort'])

            sys.stdout.write("Realm: %s\n" % (address_settings['KerberosRealm'] if \
                                            address_settings['KerberosRealm'] else "Not Set"))
        else:
            address_settings = oem_settings['DirectorySettings']
            sys.stdout.write("Port: %s\n" % address_settings['LdapServerPort'])
            sys.stdout.write("Authentication Mode: %s\n" % \
                                                        address_settings['LdapAuthenticationMode'])

            sys.stdout.write("Search Settings:\n")
            try:
                count = 1
                for search in settings['LDAPService']['SearchSettings']["BaseDistinguishedNames"]:
                    sys.stdout.write("\tSearch %s: %s\n" % (count, search))
                    count += 1
            except KeyError:
                sys.stdout.write("\tNo Search Settings\n")

        sys.stdout.write("Remote Role Mapping(s):\n")
        for role in settings['RemoteRoleMapping']:
            sys.stdout.write("\tLocal Role: %s\n" % role['LocalRole'])
            sys.stdout.write("\tRemote Group: %s\n" % role['RemoteGroup'])

    def role_helper(self, new_roles, curr_roles):
        """ Helper to prepare adding and removing roles for patching

        :param new_roles: dictionary of new roles to add or remove
        :type new_roles: dict.
        :param curr_roles: list of current roles on the system
        :type curr_roles: list.
        """
        final_roles = curr_roles
        if 'add' in new_roles:
            for role in new_roles['add']:
                role = role.split(':', 1)
                if not self.duplicate_group(role[1], curr_roles):
                    final_roles.append({"LocalRole":role[0], "RemoteGroup":role[1]})
                else:
                    raise ResourceExists('Group DN "%s" already exists.' % role[1].split(':')[0])
        if 'remove' in new_roles:
            removed = False
            for role in new_roles['remove']:
                removed = False
                for item in reversed(final_roles):
                    if item['LocalRole'] == role:
                        del final_roles[final_roles.index(item)]
                        removed = True
                        break
                if not removed:
                    raise InvalidCommandLineError("Unable to find local role %s to delete" % role)

        return final_roles

    def duplicate_group(self, group_dn, curr_roles):
        """ Checks if new role is a duplicate

        :param group_dn: group domain name from user
        :type group_dn: str.
        :param curr_roles: list of current roles
        :type curr_roles: list.
        """
        group_dn = group_dn.split(':')[0]
        for item in curr_roles:
            comp_dn = item["RemoteGroup"].split(':')[0]
            if comp_dn == group_dn:
                return True
        return False

    def search_helper(self, new_searches, curr_searches):
        """ Helper to prepare search strings for patching

        :param new_serches: dictionary of new searches to add
        :type new_searches: dict.
        :param curr_searches: list of current searches
        :type curr_searches: dict.
        """
        final_searches = curr_searches

        if 'add' in new_searches:
            if 'BaseDistinguishedNames' in final_searches:
                for search in new_searches['add']:
                    final_searches['BaseDistinguishedNames'].append(search)
            else:
                final_searches['BaseDistinguishedNames'] = new_searches['add']
        elif 'remove' in new_searches:
            to_remove = []
            if 'BaseDistinguishedNames' not in curr_searches:
                raise NoContentsFoundForOperationError("No search strings to remove")
            for search in new_searches['remove']:
                if search in curr_searches['BaseDistinguishedNames']:
                    to_remove.append(search)
                else:
                    raise InvalidCommandLineError("Unable to find search %s to delete" % search)
            for item in to_remove:
                final_searches['BaseDistinguishedNames'].remove(item)

        return final_searches

    def directoryvalidation(self, options):
        """ directory validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        inputline = list()

        if options.encode and options.user and options.password:
            options.user = Encryption.decode_credentials(options.user)
            options.password = Encryption.decode_credentials(options.password)

        try:
            client = self._rdmc.app.get_current_client()
            if options.user and options.password:
                if not client.get_username():
                    client.set_username(options.user)
                if not client.get_password():
                    client.set_password(options.password)
        except Exception:
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
                    inputline.extend(["-u", self._rdmc.app.config.get_username()])
                if self._rdmc.app.config.get_password():
                    inputline.extend(["-p", self._rdmc.app.config.get_password()])

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
            '--enable',
            '--disable',
            dest='enable',
            action='callback',
            callback=directory_parse,
            help="Optionally add this flag to enable or disable LDAP or Kerberos services.",
            default=None,
        )
        customparser.add_option(
            '--serviceaddress',
            dest='serviceaddress',
            help="Optionally include this flag to set the service address of the LDAP or "\
            "Kerberos Services.",
            default=None,
        )
        customparser.add_option(
            '--port',
            dest='port',
            help="Optionally include this flag to set the port of the LDAP or Kerberos services.",
            default=None,
        )
        customparser.add_option(
            '--realm',
            dest='realm',
            help="Optionally include this flag to set the Kerberos realm.",
            default=None,
        )
        customparser.add_option(
            '--keytab',
            dest='keytab',
            help="Optionally include this flag to import a Kerberos Keytab by it's URI location.",
            default="",
        )
        customparser.add_option(
            '--enablelocalauth',
            '--disablelocalauth',
            dest='localauth',
            action="callback",
            callback=directory_parse,
            help="Optionally include this flag if you wish to enable or disable authentication "\
            "for local accounts.",
            default=None
        )
        customparser.add_option(
            '--authentication',
            dest='authmode',
            type='choice',
            choices=['DefaultSchema', 'ExtendedSchema'],
            help="Optionally include this flag if you would like to choose a LDAP authentication "
            "mode Valid choices are: DefaultSchema (Directory Default Schema or Schema-free) or "\
            "ExtendedSchema (HPE Extended Schema).",
            default=None
        )
        customparser.add_option(
            '--addsearch',
            '--removesearch',
            dest='search',
            action='callback',
            callback=directory_parse,
            help="Optionally add this flag to add or remove search strings for "\
            "generic LDAP services. EX: --addsearch search1,search2",
            type="string",
            default={},
        )
        customparser.add_option(
            '--addrolemap',
            '--removerolemap',
            dest='roles',
            action='callback',
            callback=directory_parse,
            help="Optionally add this flag to add or remove Role Mapping(s) for the LDAP and "\
            "Kerberos services. Remove EX: --removerolemap LocalRole1,LocalRole2 "\
            'Add EX: --addrolemap "LocalRole1:RemoteGroup3,LocalRole2:RemoteGroup4"',
            type="string",
            default={},
        )
        customparser.add_option(
            '-j',
            '--json',
            dest='json',
            action="store_true",
            help="Optionally include this flag if you wish to change the"\
            " displayed output to JSON format. Preserving the JSON data"\
            " structure makes the information easier to parse.",
            default=False
        )
        customparser.add_option(
            '-e',
            '--enc',
            dest='encode',
            action='store_true',
            help=SUPPRESS_HELP,
            default=False,
        )
