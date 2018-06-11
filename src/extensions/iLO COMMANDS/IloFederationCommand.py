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
""" Add Federation Command for rdmc """

import sys
import getpass

from optparse import OptionParser
from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, AccountExists,\
                InvalidCommandLineErrorOPTS, NoContentsFoundForOperationError

class IloFederationCommand(RdmcCommandBase):
    """ Add a new ilo account to the server """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='ilofederation',\
            usage='ilofederation [COMMAND] [OPTIONS]\n\n\t'\
                'Adds an iLO federation group to the current logged in server.'\
                '\n\tilofederation add [FEDERATIONNAME KEY]'\
                '\n\texample: ilofederation add newfedname thisfedkey\n\n\t'\
                'Change the key of an iLO federation group.\n\t'\
                'ilofederation changekey [FEDERATIONNAME NEWKEY]\n\t'\
                'example: ilofederation changekey newfedname newfedkey\n\n\t'\
                'Delete an iLO federation group.\n\t'\
                'ilofederation delete [FEDERATIONNAME]\n\t'\
                'example: ilofederation delete newfedname\n\n\t'\
                'See a list of federations on the system.\n\t'\
                'example: ilofederation\n\n\tDESCRIPTIONS:\n\tFEDERATIONNAME:' \
                ' The name of the federation group. \n\tKEY:  The key ' \
                'required to join the federation.\n\n\tNOTE: please make sure' \
                ' the order of arguments is correct. The\n\tparameters are ' \
                'extracted based on their position in the arguments list.\n\t' \
                'Federation key must be 8 characters or greater.',\
            summary='Adds / deletes an iLO federaion group on the currently ' \
                'logged in server.',\
            aliases=None,\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)

    def run(self, line):
        """ Main addfederation function

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

        self.addfederationvalidation(options)

        if len(args) == 2 and args[0] in ['add', 'changekey']:
            sys.stdout.write('Please input the federation key.\n')
            tempnewkey = getpass.getpass()

            if tempnewkey and tempnewkey != '\r':
                tempnewkey = tempnewkey
            else:
                raise InvalidCommandLineError("Empty or invalid key" \
                                                                " was entered.")
            args.extend([tempnewkey])

        elif not len(args) <= 3:
            raise InvalidCommandLineError("invalid number of parameters.")

        redfish = self._rdmc.app.current_client.monolith.is_redfish
        path = self.typepath.defs.federationpath
        results = self._rdmc.app.get_handler(path, service=True, \
                                                            silent=True).dict

        newresults = []

        if redfish:
            results = results['Members']
        else:
            results = results['links']['Member']

        for fed in results:
            fed = self._rdmc.app.get_handler(\
                                         fed[self.typepath.defs.hrefstring], \
                                         service=True, silent=True).dict

            newresults.append(fed)
            results = newresults

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

            if not len(args) == 2:
                raise InvalidCommandLineError("Invalid number of parameters.")

            body = {"Name": args[0], "Key": args[1], \
                    "Privileges": {"RemoteConsolePriv": options.remoteconsole, \
                    "iLOConfigPriv": options.iloconfig,\
                    "VirtualMediaPriv": options.virtualmedia,\
                    "UserConfigPriv": options.userconfig,\
                    "VirtualPowerAndResetPriv": options.virtualpr,\
                    "LoginPriv": options.loginpriv}}

            if self.typepath.flagiften:
                body["Privileges"].update({\
                    "HostBIOSConfigPriv": options.biosconfigpriv,\
                    "HostNICConfigPriv": options.nicconfigpriv,\
                    "HostStorageConfigPriv": options.hoststoragepriv,\
                    "SystemRecoveryConfigPriv": options.sysrecoveryconfigpriv})

            self.addvalidation(args[0], args[1], results)

            if path and body:
                resp = self._rdmc.app.post_handler(path, body, response=True)

            if resp and resp.dict:
                if 'resourcealreadyexist' in str(resp.dict).lower():
                    raise AccountExists('')

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
        elif args[0].lower() == 'delete':
            args.remove('delete')

            try:
                name = unicode(args[0])
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
                raise NoContentsFoundForOperationError('Unable to find the specified'\
                                                                    ' account.')
        else:
            raise InvalidCommandLineError('Invalid command.')

        return ReturnCodes.SUCCESS

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
                raise AccountExists('Federation name is already in use.')

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
            '--noremoteconsolepriv',
            dest='remoteconsole',
            action="store_false",
            help="Optionally include this flag if you wish to set the "\
            "remote console privileges to false.",
            default=True
        )
        customparser.add_option(
            '--noiloconfigpriv',
            dest='iloconfig',
            action="store_false",
            help="Optionally include this flag if you wish to set the "\
            "ilo config privileges to false.",
            default=True
        )
        customparser.add_option(
            '--novirtualmediapriv',
            dest='virtualmedia',
            action="store_false",
            help="Optionally include this flag if you wish to set the "\
            "virtual media privileges to false.",
            default=True
        )
        customparser.add_option(
            '--nouserconfigpriv',
            dest='userconfig',
            action="store_false",
            help="Optionally include this flag if you wish to set the "\
            "userconfig privileges to false.",
            default=True
        )
        customparser.add_option(
            '--novirtualprpriv',
            dest='virtualpr',
            action="store_false",
            help="Optionally include this flag if you wish to set the "\
            "virtual power and reset privileges to false.",
            default=True
        )
        customparser.add_option(
            '--nologinpriv',
            dest='loginpriv',
            action="store_false",
            help="Optionally include this flag if you wish to set the "\
            "login privileges to false.",
            default=True
        )
        customparser.add_option(
            '--nobiosconfigpriv',
            dest='biosconfigpriv',
            action="store_false",
            help="Optionally include this flag if you wish to set the "\
            "host BIOS config privileges to false. Only available on gen10"\
            " servers.",
            default=True
        )
        customparser.add_option(
            '--nonicconfigpriv',
            dest='nicconfigpriv',
            action="store_false",
            help="Optionally include this flag if you wish to set the "\
            "host NIC config privileges to false. Only available on gen10"\
            " servers.",
            default=True
        )
        customparser.add_option(
            '--nohoststorageconfigpriv',
            dest='hoststoragepriv',
            action="store_false",
            help="Optionally include this flag if you wish to set the "\
            "host storage config privileges to false. Only available on gen10"\
            " servers.",
            default=True
        )
        customparser.add_option(
            '--nosysrecoveryconfigpriv',
            dest='sysrecoveryconfigpriv',
            action="store_false",
            help="Optionally include this flag if you wish to set the "\
            "system recovery config privileges to false. Only available on gen10"\
            " servers.",
            default=True
        )
