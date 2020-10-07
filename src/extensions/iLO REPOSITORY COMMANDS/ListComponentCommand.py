# ##
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
# ##

# -*- coding: utf-8 -*-
""" List Component Command for rdmc """

import sys
import json

from argparse import ArgumentParser

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group, login_select_validation, \
                                logout_routine

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
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath

    def run(self, line):
        """ Main listcomp worker function

        :param line: string of arguments passed in
        :type line: str.
        """
        try:
            (options, _) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
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

        logout_routine(self, options)
        #Return code
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
            sys.stdout.write(str(json.dumps(jsonout, indent=2, sort_keys=True))+'\n')
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
        login_select_validation(self, options)

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        add_login_arguments_group(customparser)

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
