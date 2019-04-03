# ##
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
# ##

# -*- coding: utf-8 -*-
""" List Component Command for rdmc """

import sys
import json

from optparse import OptionParser, SUPPRESS_HELP

from rdmc_base_classes import RdmcCommandBase

from rdmc_helper import IncompatibleiLOVersionError, ReturnCodes, InvalidCommandLineErrorOPTS, \
                        Encryption

class ListComponentCommand(RdmcCommandBase):
    """ Main download command class """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self, \
            name='listcomp', \
            usage='listcomp [OPTIONS] \n\n\tRun to list the components of' \
              'the currently logged in system.\n\texample: listcomp',\
            summary='Lists components/binaries from the iLO Repository.', \
            aliases=['Listcomp'], \
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """ Main listcomp worker function

        :param line: string of arguments passed in
        :type line: str.
        """
        try:
            (options, _) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.listcomponentvalidation(options)

        if self.typepath.defs.isgen9:
            raise IncompatibleiLOVersionError('iLO Repository commands are ' \
                                                    'only available on iLO 5.')

        comps = self._rdmc.app.getcollectionmembers(\
                            '/redfish/v1/UpdateService/ComponentRepository/')

        if comps:
            self.printcomponents(comps, options)
        else:
            sys.stdout.write('No components found.\n')

        return ReturnCodes.SUCCESS

    def printcomponents(self, comps, options):
        """ Print components function

        :param comps: list of components
        :type comps: list.
        """
        if options.json:
            jsonout = dict()
            for comp in comps:
                jsonout[comp['Id']] = comp
            sys.stdout.write(str(json.dumps(jsonout, indent=2))+'\n')
        else:
            for comp in comps:
                sys.stdout.write('Id: %s\nName: %s\nVersion: %s\nLocked:%s\nComponent '\
                                'Uri:%s\nFile Path: %s\nSizeBytes: %s\n\n' % \
                             (comp['Id'], comp['Name'].encode("ascii", "ignore"), comp['Version'], \
                              'Yes' if comp['Locked'] else 'No', comp['ComponentUri'], \
                              comp['Filepath'], str(comp['SizeBytes'])))

    def listcomponentvalidation(self, options):
        """ listcomp validation function

        :param options: command line options
        :type options: list.
        """
        inputline = list()
        client = None

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

        if not inputline and not client:
            sys.stdout.write('Local login initiated...\n')
        if not client or inputline:
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
