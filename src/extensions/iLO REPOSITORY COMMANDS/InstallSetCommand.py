# ##
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
# ##

# -*- coding: utf-8 -*-
""" Install Set Command for rdmc """

import re
import sys
import json
import datetime

from argparse import ArgumentParser

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group

from rdmc_helper import IncompatibleiLOVersionError, ReturnCodes, Encryption,\
                        InvalidCommandLineErrorOPTS, InvalidCommandLineError,\
                        NoContentsFoundForOperationError, InvalidFileInputError

class InstallSetCommand(RdmcCommandBase):
    """ Main download command class """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self, \
            name='installset', \
            usage='installset [OPTIONS] \n\n\tRun to perform operations on ' \
            'install sets.\n\n\tList install sets.\n\texample: installset\n\n' \
            '\tAdd install set.\n\texample: installset add installsetfile.json'\
            ' --name=newinstallsetname\n\n\tDelete install set.\n\texample: ' \
            'installset delete --name=installsetname\n\n\tInvoke install ' \
            'set.\n\texample: installset invoke --name=installsetname\n\n\t' \
            'Remove all install sets.\n\texample: installset --removeall\n' \
            '\n\tExample install set json file:\n\t[\n\t\t{\n\t\t\t"Name": ' \
            '"Wait",\n\t\t\t"UpdatableBy": ["RuntimeAgent"],\n\t\t\t'\
            '"Command": "Wait",\n\t\t\t"WaitTimeSeconds": 60\n\t\t},\n\t\t{' \
            '\n\t\t\t"Name": "uniqueName",\n\t\t\t"UpdatableBy": ' \
            '["RuntimeAgent"],\n\t\t\t"Command": "ApplyUpdate",\n\t\t\t"' \
            'Filename": "filename.exe"\n\t\t},\n\t\t{\n\t\t\t"Name": ' \
            '"Reboot",\n\t\t\t"UpdatableBy": ["RuntimeAgent"],\n\t\t\t' \
            '"Command": "ResetServer"\n\t\t}\n\t]',\
            summary='Manages install sets for iLO.',\
            aliases=['Installset'], \
            argparser=ArgumentParser())
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
            (options, args) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.installsetvalidation(options)

        if self.typepath.defs.isgen9:
            raise IncompatibleiLOVersionError('iLO Repository commands are ' \
                                                    'only available on iLO 5.')

        if args and args[0] in ['delete', 'invoke'] and not options.name:
            raise InvalidCommandLineError('Name option is required for ' \
                                          'delete and invoke commands.')
        if options.name:
            if options.name.startswith('"') and options.name.endswith('"'):
                options.name = options.name[1:-1]
        if options.removeall:
            self.removeinstallsets()
        elif not args:
            self.printinstallsets(options)
        elif args[0].lower() == 'add':
            if not len(args) == 2:
                raise InvalidCommandLineError('add command requires an install set file.')
            else:
                self.addinstallset(args[1], options.name)
        elif args[0].lower() == 'delete':
            self.deleteinstallset(options.name)
        elif args[0].lower() == 'invoke':
            self.invokeinstallset(options)
        else:
            raise InvalidCommandLineError('%s is not a valid command.' % args[0])

        return ReturnCodes.SUCCESS

    def addinstallset(self, setfile, name):
        """Adds an install set
        :param setfile: filename of install set
        :type setfile: str.
        :param name: string of the install set name to add
        :type name: str.
        """
        path = '/redfish/v1/UpdateService/InstallSets/'
        comps = self._rdmc.app.getcollectionmembers(\
                            '/redfish/v1/UpdateService/ComponentRepository/')

        sets = self._rdmc.app.getcollectionmembers(path)

        if not name:
            name = str(datetime.datetime.now())
            name = name.replace(':', '')
            name = name.replace(' ', 'T')
        try:
            inputfile = open(setfile, 'r')
            sequences = json.loads(inputfile.read())
        except Exception as excp:
            raise InvalidFileInputError("%s" % excp)

        listtype = self.validatefile(sequences)

        if listtype:
            body = {"Name": name, "Sequence": sequences}
        else:
            body = sequences
            if "Sequence" in body:
                sequences = body['Sequence']
            else:
                raise InvalidFileInputError("Invalid install set file.")
            sequences = body["Sequence"]

        filenamelist = [x['Filename'] for x in comps]

        for sequence in sequences:
            if sequence['Command'] == 'ApplyUpdate':
                if 'Filename' in list(sequence.keys()):
                    if not sequence['Filename'] in filenamelist:
                        raise NoContentsFoundForOperationError('Component' \
                            ' referenced in install set is not present on' \
                            ' iLO Drive: %s' % sequence['Filename'])
            elif sequence['Command'] == 'WaitTimeSeconds':
                sequence['WaitTimeSeconds'] = int(sequence['WaitTimeSeconds'])
        for setvar in sets:
            if setvar['Name'] == body['Name']:
                raise InvalidCommandLineError('Install set name is already in use.')

        self._rdmc.app.post_handler(path, body)

    def invokeinstallset(self, options):
        """Deletes the named set
        :param name: string of the install set name to delete
        :type name: str.
        """
        path = None
        name = options.name
        sets = self._rdmc.app.getcollectionmembers(\
                                       '/redfish/v1/UpdateService/InstallSets/')

        for setvar in sets:
            if setvar['Name'] == name:
                path = setvar['Actions']['#HpeComponentInstallSet.Invoke']['target']

        if not path:
            raise NoContentsFoundForOperationError('No install set with the' \
                                            ' provided name could be found.')

        sys.stdout.write('Invoking install set:%s\n' % name)

        payload = self.checkpayloadoptions(options)
        self._rdmc.app.post_handler(path, payload)

    def deleteinstallset(self, name):
        """Deletes the named set

        :param name: string of the install set name to delete
        :type name: str.
        """
        path = None
        sets = self._rdmc.app.getcollectionmembers('/redfish/v1/UpdateService/InstallSets/')

        for setvar in sets:
            if setvar['Name'] == name:
                path = setvar['@odata.id']

        if path:
            sys.stdout.write('Deleting install set: %s...\n'% name)
            self._rdmc.app.delete_handler(path)
        else:
            raise NoContentsFoundForOperationError('Unable to find the specified install set.')

    def removeinstallsets(self):
        """Removes all install sets """
        sets = self._rdmc.app.getcollectionmembers('/redfish/v1/UpdateService/InstallSets/')

        if not sets:
            sys.stdout.write('No install sets found.\n')

        sys.stdout.write('Deleting all install sets...\n')

        for setvar in sets:
            if setvar['IsRecovery']:
                sys.stdout.write('Skipping delete of recovery set: %s\n' %setvar['Name'])
            else:
                sys.stdout.write('Deleting install set: %s\n' % setvar['Name'])
                self._rdmc.app.delete_handler(setvar['@odata.id'])

    def printinstallsets(self, options):
        """Prints install sets """
        sets = self._rdmc.app.getcollectionmembers('/redfish/v1/UpdateService/InstallSets/')
        if not options.json:
            sys.stdout.write('Install Sets:\n')

        if not sets:
            sys.stdout.write('No install sets found.\n')
        elif not options.json:
            for setvar in sets:
                if setvar['IsRecovery']:
                    recovery = "[Recovery Set]"
                else:
                    recovery = ""
                sys.stdout.write('\n%s: %s\n' % (setvar['Name'], recovery))

                if 'Sequence' not in list(setvar.keys()):
                    sys.stdout.write('\tNo Sequences in set.\n')
                    continue

                for item in setvar['Sequence']:
                    if 'Filename' in list(item.keys()):
                        sys.stdout.write('\t%s: %s %s\n' % (item['Name'].encode("ascii", "ignore"),\
                                            item['Command'], item['Filename']))
                    elif 'WaitTimeSeconds' in list(item.keys()):
                        sys.stdout.write('\t%s: %s %s seconds\n' % \
                                             (item['Name'], item['Command'], \
                                              str(item['WaitTimeSeconds'])))
                    else:
                        sys.stdout.write('\t%s: %s\n' % (item['Name'], \
                                                            item['Command']))
        elif options.json:
            outjson = dict()
            for setvar in sets:
                outjson[setvar['Name']] = setvar
            sys.stdout.write(str(json.dumps(outjson, indent=2, sort_keys=True))+'\n')

    def validatefile(self, installsetfile):
        """ validates json file

        :param file: json file to validate
        :type file: string.
        """
        listtype = True
        keylist = ['Name', 'UpdatableBy', 'Command', 'WaitTimeSeconds', 'Filename']

        if isinstance(installsetfile, list):
            for item in installsetfile:
                for key in item:
                    if key not in keylist:
                        raise InvalidFileInputError('Property %s is invalid ' \
                                                    'for an install set.' % key)
        else:
            listtype = False

        return listtype

    def checkpayloadoptions(self, options):
        """ checks for payload options and adds needed ones to payload

        :param options: command line options
        :type options: list.
        """

        payload = {}
        if options.exafter:
            self.checktime(options.exafter)
            payload["Expire"] = options.exafter
        if options.safter:
            self.checktime(options.safter)
            payload["StartAfter"] = options.safter
        if options.tover:
            payload["TPMOverride"] = True
        if options.uset:
            payload["UpdateRecoverySet"] = True
        if options.ctakeq:
            payload["ClearTaskQueue"] = True

        return payload

    def checktime(self, timestr):
        """ check the time string for valid format

        :param timestr: time string to check
        :type timestr: string.
        """
        rfdtregex = '\\d\\d\\d\\d-\\d\\d-\\d\\dT\\d\\d:\\d\\d:\\d\\dZ?'
        if not re.match(rfdtregex, timestr):
            raise InvalidCommandLineError('Invalid redfish date-time format. '\
                'Accepted formats: YYYY-MM-DDThh:mm:ss, YYYY-MM-DDThh:mm:ssZ')

    def installsetvalidation(self, options):
        """ installset validation function

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
            '-n',
            '--name',
            dest='name',
            help="""Install set name to create, remove, or invoke.""",
            default=None,
        )
        customparser.add_argument(
            '--removeall',
            action='store_true',
            dest='removeall',
            help="""Remove all install sets.""",
            default=False,
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
        customparser.add_argument(
            '--expire',
            dest='exafter',
            help="Optionally include this flag if you wish to set the"\
            " time for installset to expire. ISO 8601 Redfish-style time "\
            "string to be written after which iLO will automatically change "\
            "state to Expired",
            default=None
        )
        customparser.add_argument(
            '--startafter',
            dest='safter',
            help="Optionally include this flag if you wish to set the"\
            " earliest execution time for installset. ISO 8601 Redfish-style "\
            "time string to be used.",
            default=None
        )
        customparser.add_argument(
            '--tpmover',
            dest='tover',
            action="store_true",
            help="If set then the TPMOverrideFlag is passed in on the "\
            "associated flash operations",
            default=False
        )
        customparser.add_argument(
            '--updaterecoveryset',
            dest='uset',
            action="store_true",
            help="If set then the components in the flash operations are used"\
            " to replace matching contents in the Recovery Set.",
            default=False
        )
        customparser.add_argument(
            '--cleartaskqueue',
            dest='ctakeq',
            action="store_true",
            help="This option allows previous items in the task queue to"\
            " be cleared before the Install Set is invoked",
            default=False
        )
