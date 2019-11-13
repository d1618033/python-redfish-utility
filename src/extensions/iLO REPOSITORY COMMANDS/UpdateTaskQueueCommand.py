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
""" Update Task Queue Command for rdmc """

import sys
import json

from random import randint
from argparse import ArgumentParser

from redfish.ris.rmc_helper import IdTokenError

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group
from rdmc_helper import IncompatibleiLOVersionError, ReturnCodes, NoContentsFoundForOperationError,\
                        InvalidCommandLineErrorOPTS, InvalidCommandLineError, Encryption, \
                        TaskQueueError

class UpdateTaskQueueCommand(RdmcCommandBase):
    """ Main download command class """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self, \
            name='taskqueue', \
            usage='taskqueue [OPTIONS] \n\n\tRun to add or remove tasks from the' \
              ' task queue. Added tasks are appended to the end of the queue.'\
              '\n\n\tPrint update task queue.\n\texample: taskqueue'\
              '\n\n\tCreate new wait task for 30 secs.\n\texample: '\
              'taskqueue create 30\n\n\tCreate new reboot task.\n\t'\
              'example: taskqueue create reboot\n\n\tCreate new '\
              'component task.\n\texample: taskqueue create compname.exe\n\n\tCreate multiple'\
              ' tasks at once.\n\texample: taskqueue create 30 compname.exe compname2.exe '\
              'reboot\n\n\tDelete all tasks from update task queue.\n\texample: taskqueue '\
              '--resetqueue\n\n\tRemove all finished or errored tasks, leaving '\
              'pending.\n\texample: taskqueue --cleanqueue',\
            summary='Manages the update task queue for iLO.',\
            aliases=['Taskqueue'], \
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """ Main update task queue worker function

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

        self.updatetaskqueuevalidation(options)

        if self.typepath.defs.isgen9:
            raise IncompatibleiLOVersionError(\
                      'iLO Repository commands are only available on iLO 5.')

        if options.resetqueue:
            self.resetqueue()
        elif options.cleanqueue:
            self.cleanqueue()
        elif not args:
            self.printqueue(options)
        elif args[0].lower() == 'create':
            self.createtask(args[1:], options)
        else:
            raise InvalidCommandLineError('Invalid command entered.')

        return ReturnCodes.SUCCESS

    def resetqueue(self):
        """ Deletes everything in the update task queue"""
        tasks = self._rdmc.app.getcollectionmembers('/redfish/v1/UpdateService/UpdateTaskQueue/')
        if not tasks:
            sys.stdout.write('No tasks found.\n')

        sys.stdout.write('Deleting all update tasks...\n')

        for task in tasks:
            sys.stdout.write('Deleting: %s\n'% task['Name'].encode("ascii", "ignore"))
            self._rdmc.app.delete_handler(task['@odata.id'])

    def cleanqueue(self):
        """ Deletes all finished or errored tasks in the update task queue"""
        tasks = self._rdmc.app.getcollectionmembers('/redfish/v1/UpdateService/UpdateTaskQueue/')
        if not tasks:
            sys.stdout.write('No tasks found.\n')

        sys.stdout.write('Cleaning update task queue...\n')

        for task in tasks:
            if task['State'] == 'Complete' or task['State'] == 'Exception':
                sys.stdout.write('Deleting %s...\n'% task['Name'].encode("ascii", "ignore"))
                self._rdmc.app.delete_handler(task['@odata.id'])

    def createtask(self, tasks, options):
        """ Creates a task in the update task queue

        :param tasks: arguments for creating tasks
        :type tasks: list.
        :param options: command line options
        :type options: list.
        """

        tpmflag = None

        path = '/redfish/v1/UpdateService/UpdateTaskQueue/'
        comps = self._rdmc.app.getcollectionmembers('/redfish/v1/UpdateService/'\
                                                    'ComponentRepository/')
        curr_tasks = self._rdmc.app.getcollectionmembers(\
                                                    '/redfish/v1/UpdateService/UpdateTaskQueue/')
        for task in tasks:
            usedcomp = None
            newtask = None

            try:
                usedcomp = int(task)
                newtask = {'Name': 'Wait-%s %s seconds' % (str(randint(0, \
                           1000000)), str(usedcomp)), 'Command': 'Wait', \
                           'WaitTimeSeconds':usedcomp, 'UpdatableBy':[\
                            'Bmc']}
            except ValueError:
                pass

            if task.lower() == 'reboot':
                newtask = {'Name': 'Reboot-%s' % str(randint(0, 1000000)), \
                          'Command': 'ResetServer', 'UpdatableBy': \
                          ['RuntimeAgent']}
            elif not newtask:
                if tpmflag is None:
                    if options.tover:
                        tpmflag = True
                    else:
                        tpmflag = False
                    #TODO: Update to monolith check
                    results = self._rdmc.app.get_handler(self.typepath.defs.biospath, silent=True)
                    if results.status == 200:
                        contents = results.dict if self.typepath.defs.isgen9 else \
                                                                        results.dict["Attributes"]
                        tpmstate = contents["TpmState"]
                        if "Enabled" in tpmstate and not tpmflag:
                            raise IdTokenError('')

                for curr_task in curr_tasks:
                    if 'Filename' in curr_task and curr_task['Filename'] == task \
                            and curr_task['State'].lower() is not 'exception':
                        raise TaskQueueError("This file already has a task queue for flashing "\
                                                 "associated with it. Reset the taskqueue and "\
                                                 "retry if you need to add this task again.")
                for comp in comps:
                    if comp['Filename'] == task:
                        usedcomp = comp
                        break

                if not usedcomp:
                    raise NoContentsFoundForOperationError('Component ' \
                           'referenced is not present on iLO Drive: %s' % task)

                newtask = {'Name': 'Update-%s %s' % (str(randint(0, 1000000)), \
                        usedcomp['Name'].encode("ascii", "ignore")), 'Command': 'ApplyUpdate',\
                      'Filename': usedcomp['Filename'], 'UpdatableBy': usedcomp\
                      ['UpdatableBy'], 'TPMOverride': tpmflag}

            sys.stdout.write('Creating task: "%s"\n' % newtask['Name'].encode("ascii", "ignore"))

            self._rdmc.app.post_handler(path, newtask)

    def printqueue(self, options):
        """ Prints the update task queue

        :param options: command line options
        :type options: list.
        """
        tasks = self._rdmc.app.getcollectionmembers(\
                                '/redfish/v1/UpdateService/UpdateTaskQueue/')
        if not tasks:
            sys.stdout.write('No tasks found.\n')
            return

        if not options.json:
            sys.stdout.write('\nCurrent Update Task Queue:\n\n')

        if not options.json:
            for task in tasks:
                sys.stdout.write('Task %s:\n'%task['Name'].encode("ascii", "ignore"))

                if 'Filename' in list(task.keys()):
                    sys.stdout.write('\tCommand: %s\n\tFilename: %s\n\t'\
                        'State:%s\n'% (task['Command'], task['Filename'], task['State']))
                elif 'WaitTimeSeconds' in list(task.keys()):
                    sys.stdout.write('\tCommand: %s %s seconds\n\tState:%s\n'%(\
                                task['Command'], str(task['WaitTimeSeconds']), task['State']))
                else:
                    sys.stdout.write('\tCommand:%s\n\tState: %s\n'%(task['Command'], task['State']))

                sys.stdout.write('\n')
        elif options.json:
            outjson = dict()
            for task in tasks:
                outjson[task['Name']] = task
            sys.stdout.write(str(json.dumps(outjson, indent=2, sort_keys=True))+'\n')

    def updatetaskqueuevalidation(self, options):
        """ taskqueue validation function

        :param options: command line options
        :type options: list.
        """
        inputline = list()
        client = None

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

        add_login_arguments_group(customparser)

        customparser.add_argument(
            '-r',
            '--resetqueue',
            action='store_true',
            dest='resetqueue',
            help="""Remove all update tasks in the queue.""",
            default=False,
        )
        customparser.add_argument(
            '-c',
            '--cleanqueue',
            action='store_true',
            dest='cleanqueue',
            help="""Clean up all finished or errored tasks - leave pending.""",
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
            '--tpmover',
            dest='tover',
            action="store_true",
            help="If set then the TPMOverrideFlag is passed in on the "\
            "associated flash operations",
            default=False
        )
