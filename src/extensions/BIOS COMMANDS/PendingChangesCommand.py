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
""" Results Command for rdmc """

import sys
import copy
import json

from optparse import OptionParser, SUPPRESS_HELP

import jsondiff

from rdmc_base_classes import RdmcCommandBase, HARDCODEDLIST
from rdmc_helper import ReturnCodes, InvalidCommandLineError, Encryption, \
                            InvalidCommandLineErrorOPTS, UI

class PendingChangesCommand(RdmcCommandBase):
    """ PendingChanges class command """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='pending',\
            usage='pending [OPTIONS]\n\n\tRun to show pending committed changes '\
                    'that will be applied after a reboot.\n\texample: pending',\
            summary='Show the pending changes that will be applied on reboot.',\
            aliases=['pending'],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)

    def run(self, line):
        """ Show pending changes of settings objects

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

        if args:
            raise InvalidCommandLineError("Pending command does not take any arguments.")
        self.pendingvalidation(options)

        self.pendingfunction()

        return ReturnCodes.SUCCESS

    def pendingfunction(self):
        """ Main pending command worker function
        """
        settingsuri = []
        ignorekeys = ['@odata.id', '@odata.etag', '@redfish.settings', 'oem']
        ignoreuri = [unicode('hpsut*')]
        ignorekeys.extend(HARDCODEDLIST)

        resourcedir = self._rdmc.app.get_handler(self._rdmc.app.current_client.\
                monolith._resourcedir, verbose=self._rdmc.opts.verbose, service=True, silent=True)

        for resource in resourcedir.dict['Instances']:
            if (resource['@odata.id'].split('/').__len__() - 1) > 4:
                splitstr = resource['@odata.id'].split('/')[5]
            for element in ignoreuri:
                if '/settings' in resource['@odata.id'] and not \
                                                        self.wildcard_str_match(element, splitstr):
                    settingsuri.append(resource['@odata.id'])

        sys.stdout.write('Current Pending Changes:\n')

        for uri in settingsuri:
            diffprint = {}
            baseuri = uri.split('settings')[0]

            base = self._rdmc.app.get_handler(baseuri, \
                    verbose=self._rdmc.opts.verbose, service=True, silent=True)
            settings = self._rdmc.app.get_handler(uri, \
                    verbose=self._rdmc.opts.verbose, service=True, silent=True)

            typestring = self._rdmc.app._rmc_clients._monolith._typestring
            currenttype = '.'.join(base.dict[typestring].split('#')[-1].split('.')[:-1])

            differences = json.loads(jsondiff.diff(base.dict, settings.dict, \
                                                syntax='symmetric', dump=True))

            diffprint = self.recursdict(differences, ignorekeys)

            sys.stdout.write('\n%s:' % currenttype)
            if not diffprint:
                sys.stdout.write('\nNo pending changes found.\n')
            else:
                UI().pretty_human_readable(diffprint)
                sys.stdout.write('\n')

    def wildcard_str_match(self, first, second):
        """
        Recursive function for determining match between two strings. Accounts
        for wildcard characters

        :param first: comparison string (may contain '*' or '?' for wildcards)
        :param type: str (unicode)
        :param second: string value to be compared (must not contain '*' or '?')
        :param type: str (unicode)
        """

        if not first and not second:
            return True
        if len(first) > 1 and first[0] == '*' and not second:
            return False
        if (len(first) > 1 and first[0] == '?') or (first and second and first[0] == second[0]):
            return self.wildcard_str_match(first[1:], second[1:])
        if first and first[0] == '*':
            return self.wildcard_str_match(first[1:], second) or \
                self.wildcard_str_match(first, second[1:])

        return False

    def recursdict(self, diff, ignorekeys):
        """ Recursively get dict ready for printing

        :param diff: diff dict
        :type options: dict.
        """
        diffprint = copy.deepcopy(diff)
        for item in diff:
            if item.lower() in ignorekeys:
                diffprint.pop(item)
            elif item == '$delete':
                for ditem in diff[item]:
                    if isinstance(diff[item], list):
                        continue
                    if isinstance(diff[item][ditem], dict):
                        diffprint[item].pop(ditem)
                        if ditem.lower() in ignorekeys or ditem.isdigit():
                            continue
                        else:
                            diffprint.update({'removed': ditem})
                diffprint.pop(item)
            elif item == '$insert':
                for ditem in diff[item]:
                    del diffprint[item][diffprint[item].index(ditem)]
                    diffprint.update({'changed index position': ditem[1]})
                diffprint.pop(item)
            elif isinstance(diff[item], dict):
                diffprint[item] = self.recursdict(diff[item], ignorekeys)

            elif isinstance(diff[item], list):
                diffprint.update({item: {'Current': diff[item][0], 'Pending': diff[item][1]}})
            else:
                continue

        return diffprint

    def pendingvalidation(self, options):
        """ Pending method validation function

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
            '-e',
            '--enc',
            dest='encode',
            action='store_true',
            help=SUPPRESS_HELP,
            default=False,
        )
