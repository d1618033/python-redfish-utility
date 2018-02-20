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

import sys
import json

from optparse import OptionParser
from random import randint

from rdmc_base_classes import RdmcCommandBase

from rdmc_helper import IncompatibleiLOVersionError, ReturnCodes,\
                        InvalidCommandLineErrorOPTS, InvalidCommandLineError,\
                        NoContentsFoundForOperationError

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
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commandsDict["LoginCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commandsDict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """ Main update task queue worker function

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
            self.createtask(args[1:])
        else:
            raise InvalidCommandLineError('Invalid command entered.')

        return ReturnCodes.SUCCESS

    def resetqueue(self):
        """ Deletes everything in the update task queue"""
        tasks = self._rdmc.app.getcollectionmembers(\
                                '/redfish/v1/UpdateService/UpdateTaskQueue/')
        if not tasks:
            sys.stdout.write('No tasks found.\n')

        sys.stdout.write('Deleting all update tasks...\n')

        for task in tasks:
            sys.stdout.write('Deleting: %s\n'% task['Name'])
            self._rdmc.app.delete_handler(task['@odata.id'])

    def cleanqueue(self):
        """ Deletes all finished or errored tasks in the update task queue"""
        tasks = self._rdmc.app.getcollectionmembers('/redfish/v1/UpdateService/'\
                                                    'UpdateTaskQueue/')
        if not tasks:
            sys.stdout.write('No tasks found.\n')

        sys.stdout.write('Cleaning update task queue...\n')

        for task in tasks:
            if task['State'] == 'Complete' or task['State'] == 'Exception':
                sys.stdout.write('Deleting %s...\n'% task['Name'])
                self._rdmc.app.delete_handler(task['@odata.id'])

    def createtask(self, tasks):
        """ Creates a task in the update task queue

        :param tasks: arguments for creating tasks
        :type tasks: list.
        """
        path = '/redfish/v1/UpdateService/UpdateTaskQueue/'
        comps = self._rdmc.app.getcollectionmembers('/redfish/v1/UpdateService/'\
                                                    'ComponentRepository/')
        for task in tasks:
            usedcomp = None
            newtask = None

            try:
                usedcomp = int(task)
                newtask = {'Name': 'Wait-%s %s seconds' % (str(randint(0, \
                           1000000)), str(usedcomp)), 'Command': 'Wait', \
                           'WaitTimeSeconds':usedcomp, 'UpdatableBy':[\
                                                  'RuntimeAgent', 'Uefi']}
            except:
                pass

            if task.lower() == 'reboot':
                newtask = {'Name': 'Reboot-%s' % str(randint(0, 1000000)), \
                          'Command': 'ResetServer', 'UpdatableBy': \
                          ['RuntimeAgent']}
            elif not newtask:
                try:
                    for comp in comps:
                        if comp['Filename'] == task:
                            usedcomp = comp
                            break
                except:
                    pass

                if not usedcomp:
                    raise NoContentsFoundForOperationError('Component ' \
                           'referenced is not present on iLO Drive: %s' % task)

                newtask = {'Name': 'Update-%s %s' % (str(randint(0, 1000000)), \
                        usedcomp['Name']), 'Command': 'ApplyUpdate',\
                      'Filename': usedcomp['Filename'], 'UpdatableBy': usedcomp\
                      ['UpdatableBy'], 'TPMOverride': True}

            sys.stdout.write('Creating task: "%s"\n' % newtask['Name'])

            self._rdmc.app.post_handler(path, newtask)

    def printqueue(self, options):
        """ Prints the update task queue"""
        tasks = self._rdmc.app.getcollectionmembers(\
                                '/redfish/v1/UpdateService/UpdateTaskQueue/')
        if not tasks:
            sys.stdout.write('No tasks found.\n')
            return

        if not options.json:
            sys.stdout.write('\nCurrent Update Task Queue:\n\n')

        if not options.json:
            for task in tasks:
                sys.stdout.write('Task %s:\n'%task['Name'])
    
                if 'Filename' in task.keys():
                    sys.stdout.write('\tCommand: %s\n\tFilename: %s\n\t'\
                        'State:%s\n'% (task['Command'], task['Filename'], \
                                                            task['State']))
                elif 'WaitTimeSeconds' in task.keys():
                    sys.stdout.write('\tCommand: %s %s seconds\n\tState:%s\n'%(\
                                task['Command'], str(task['WaitTimeSeconds']),
                                    task['State']))
                else:
                    sys.stdout.write('\tCommand:%s\n\ttate: %s\n'%(task\
                                                    ['Command'],task['State']))
    
                sys.stdout.write('\n')
        elif options.json:
            outjson = dict()
            for task in tasks:
                outjson[task['Name']] = task
            sys.stdout.write(str(json.dumps(outjson, indent=2))+'\n')

    def updatetaskqueuevalidation(self, options):
        """ taskqueue validation function

        :param options: command line options
        :type options: list.
        """
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

            if not len(inputline):
                sys.stdout.write(u'Local login initiated...\n')
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
            '-r',
            '--resetqueue',
            action='store_true',
            dest='resetqueue',
            help="""Remove all update tasks in the queue.""",
            default=False,
        )
        customparser.add_option(
            '-c',
            '--cleanqueue',
            action='store_true',
            dest='cleanqueue',
            help="""Clean up all finished or errored tasks - leave pending.""",
            default=False,
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
