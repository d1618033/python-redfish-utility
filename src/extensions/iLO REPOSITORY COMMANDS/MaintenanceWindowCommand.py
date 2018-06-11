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
""" Update Task Queue Command for rdmc """

import re
import sys
import json

from optparse import OptionParser
from random import randint

from redfish.ris.rmc_helper import ValidationError

from rdmc_base_classes import RdmcCommandBase

from rdmc_helper import IncompatibleiLOVersionError, ReturnCodes,\
                        InvalidCommandLineErrorOPTS, InvalidCommandLineError,\
                        NoContentsFoundForOperationError

class MaintenanceWindowCommand(RdmcCommandBase):
    """ Main maintenancewindow command class """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self, \
            name='maintenancewindow', \
            usage='maintenancewindow [OPTIONS] \n\n\t'\
            'Run to add, remove, or delete maintenance windows from the iLO ' \
              'repository.\n\n\tPrint maintenance windows on the system.'\
              '\n\texample: maintenancewindow\n\n\tCreate new maintenance window '\
               'with startup time 1998-11-21T00:00:00 and user defined expire time,'\
               ' name, and description.\n\texample: maintenancewindow add '\
               '1998-11-21T00:00:00 --expire=1998-11-22T00:00:00 --name='\
               'MyMaintenanceWindow --description "My maintenance window description."'\
               '\n\n\tDelete a maintenance window by name:\n\texample: '\
               'maintenancewindow delete MyMaintenanceWindow\n\t'\
               'Note: You can delete maintenance windows by Id or Name.',\
            summary='Manages the maintenance windows for iLO.',\
            aliases=['Maintenancewindow'], \
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """ Main update maintenance window worker function

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

        self.maintenancewindowvalidation(options)

        if self.typepath.defs.isgen9:
            raise IncompatibleiLOVersionError(\
                      'iLO Repository commands are only available on iLO 5.')

        windows = self._rdmc.app.getcollectionmembers(\
                                '/redfish/v1/UpdateService/MaintenanceWindows/')
        if not args:
            self.listmainenancewindows(options, windows)
        elif args[0].lower() == 'add':
            if not len(args) == 2:
                raise InvalidCommandLineError("Adding a maintenance window only "\
                                              "requires one argument.")
            else:
                self.addmaintenancewindow(options, windows, args[1])
        elif args[0].lower() == 'delete':
            if not len(args) == 2:
                raise InvalidCommandLineError("Deleting a maintenance window only"\
                                              " requires one argument.")
            else:
                self.deletemaintenancewindow(windows, args[1])
        else:
            raise InvalidCommandLineError('Invalid command entered.')

        return ReturnCodes.SUCCESS

    def addmaintenancewindow(self, options, windows, startafter):
        """ Add a maintenance window

        :param options: command line options
        :type options: list.
        :param windows: list of maintenance windows on the system
        :type windows: list.
        :param startafter: redfish date-time string to start the maintenance window
        :type startafter: str.
        """
        adddata = {}
        adddata['StartAfter'] = startafter

        if options.name:
            adddata['Name'] = options.name
        else:
            adddata['Name'] = 'MW-%s' % str(randint(0, 1000000))

        if options.description:
            if options.description.startswith('"') and \
                                            options.description.endswith('"'):
                options.description = options.description[1:-1]
            adddata['Description'] = options.description

        if options.expire:
            adddata['Expire'] = options.expire

        errors = self.validatewindow(adddata, windows)

        if not errors:
            path = '/redfish/v1/UpdateService/MaintenanceWindows/'
            self._rdmc.app.post_handler(path, adddata)
        else:
            sys.stderr.write("Invalid Maintenance Window:\n")
            for error in errors:
                sys.stderr.write('\t'+error+'\n')
            raise ValidationError('')

    def deletemaintenancewindow(self, windows, nameid):
        """ Delete a maintenance window by Id or Name

        :param windows: list of maintenance windows on the system
        :type windows: list.
        :param nameid: id or name string to remove
        :type nameid: str.
        """

        deleted = False
        for window in windows:
            if window['Name'] == nameid or window['Id'] == nameid:
                path = window['@odata.id']
                sys.stdout.write("Deleting %s\n" % nameid)
                self._rdmc.app.delete_handler(path)
                deleted = True
                break

        if not deleted:
            raise NoContentsFoundForOperationError("No maintenance window found with that Name/Id.")

    def listmainenancewindows(self, options, windows):
        """ Lists the maintenance windows

        :param options: command line options
        :type options: list.
        :param windows: list of maintenance windows on the system
        :type windows: list.
        """

        outstring = ''
        jsonwindows = []

        if windows:
            for window in windows:
                if options.json:
                    jsonwindows.append(dict((key, val) for key, val in window.iteritems() \
                                                            if not '@odata.'in key))
                else:
                    outstring += '%s:' % window['Name']
                    if 'Description' in window.keys() and window['Description']:
                        outstring += '\n\tDescription: %s' % window['Description']
                    else:
                        outstring += '\n\tDescription: %s' % 'No description.'
                    outstring += '\n\tStart After: %s' % window['StartAfter']
                    if 'Expire' in window.keys():
                        outstring += '\n\tExpires at: %s' % window['Expire']
                    else:
                        outstring += '\n\tExpires at: %s' % 'No expire time set.'
                    outstring += '\n'
            if jsonwindows:
                sys.stdout.write(str(json.dumps(jsonwindows, indent=2))+'\n')
            else:
                sys.stdout.write(outstring)
        else:
            sys.stdout.write("No maintenance windows found on system.\n")

    def validatewindow(self, cmw, windows):
        """ Validate the maintenance window before adding

        :param cmw: a maintenance window candidate
        :type cmw: dict.
        :param windows: list of maintenance windows on the system
        :type windows: list.
        :returns: returns a list of errors or a empty list if no errors
        """
        errorlist = []
        rfdtregex = '\\d\\d\\d\\d-\\d\\d-\\d\\dT\\d\\d:\\d\\d:\\d\\dZ?'

        for window in windows:
            if cmw['Name'] == window['Name']:
                errorlist.append('Maintenance window with Name: %s already exists.'\
                                 % cmw['Name'])

        if 'Name' in cmw.keys():
            if len(cmw['Name']) > 64:
                errorlist.append('Name must be 64 characters or less.')
        if 'Description' in cmw.keys():
            if len(cmw['Description']) > 64:
                errorlist.append('Description must be 64 characters or less.')
        if 'Expire' in cmw.keys():
            if not re.match(rfdtregex, cmw['Expire']):
                errorlist.append('Invalid redfish date-time format in Expire. '\
                    'Accepted formats: YYYY-MM-DDThh:mm:ss, YYYY-MM-DDThh:mm:ssZ')
        if not re.match(rfdtregex, cmw['StartAfter']):
            errorlist.append('Invalid redfish date-time format in StartAfter. '\
                    'Accepted formats YYYY-MM-DDThh:mm:ss, YYYY-MM-DDThh:mm:ssZ')

        return errorlist

    def maintenancewindowvalidation(self, options):
        """ maintenencewindow validation function

        :param options: command line options
        :type options: list.
        """
        inputline = list()
        client = None

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

        if not inputline and not client:
            sys.stdout.write(u'Local login initiated...\n')
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
            '--description',
            dest='description',
            help="Optionally include this flag if you would like to add a "\
            "description to the maintenance window you create",
            default=None
        )
        customparser.add_option(
            '-n',
            '--name',
            dest='name',
            help="Optionally include this flag if you would like to add a "\
            "name to the maintenance window you create. If you do not specify one"\
            " a unique name will be added.",
            default=None
        )
        customparser.add_option(
            '-e',
            '--expire',
            dest='expire',
            help="Optionally include this flag if you would like to add a "\
            "time the maintenance window expires.",
            default=None
        )
