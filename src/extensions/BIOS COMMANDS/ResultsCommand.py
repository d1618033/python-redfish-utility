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

from optparse import OptionParser
from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
                                                    InvalidCommandLineErrorOPTS

class ResultsCommand(RdmcCommandBase):
    """ Monolith class command """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='results',\
            usage='results [OPTIONS]\n\n\tRun to show the results of the last' \
                    ' BIOS change after a server reboot.\n\texample: results',\
            summary='Show the results of a BIOS change after a server reboot.',\
            aliases=['results'],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commandsDict["LoginCommand"](rdmcObj)
        self.selobj = rdmcObj.commandsDict["SelectCommand"](rdmcObj)

    def run(self, line):
        """ Gather results of latest BIOS change

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

        if not len(args) == 0:
            raise InvalidCommandLineError("Results command does not take any " \
                                                                "arguments.")
        self.resultsvalidation(options)
        results = {}
        if self.typepath.defs.biospath[-1] == '/':
            iscsipath = self.typepath.defs.biospath + 'iScsi/'
            bootpath = self.typepath.defs.biospath + 'Boot/'
        else:
            iscsipath = self.typepath.defs.biospath + '/iScsi'
            bootpath = self.typepath.defs.biospath + '/Boot'

        try:
            self.selobj.selectfunction("SmartStorageConfig")
            smartarray = self._rdmc.app.get_save()
            sapaths = [path['@odata.id'].split('settings')[0] for path in smartarray]
        except:
            sapaths = None

        biosresults = self._rdmc.app.get_handler(self.typepath.defs.biospath, \
                    verbose=self._rdmc.opts.verbose, service=True, silent=True)
        iscsiresults = self._rdmc.app.get_handler(iscsipath, \
                    verbose=self._rdmc.opts.verbose, service=True, silent=True)
        bootsresults = self._rdmc.app.get_handler(bootpath, \
                    verbose=self._rdmc.opts.verbose, service=True, silent=True)
        if sapaths:
            saresults = [self._rdmc.app.get_handler(path, \
                            verbose=self._rdmc.opts.verbose, service=True, \
                            silent=True) for path in sapaths]
        try:
            results.update({'Bios:': biosresults.dict[self.typepath.defs.\
                                            biossettingsstring][u'Messages']})
        except:
            results.update({'Bios:': None})

        try:
            results.update({'Iscsi:': iscsiresults.dict[self.typepath.defs.\
                                           biossettingsstring][u'Messages']})
        except:
            results.update({'Iscsi:': None})

        try:
            results.update({'Boot:': bootsresults.dict[self.typepath.defs.\
                                             biossettingsstring][u'Messages']})
        except:
            results.update({'Boot:': None})
        try:
            for result in saresults:
                loc = 'SmartArray'
                if saresults.index(result) > 0:
                    loc += ' %d:' % saresults.index(result)
                else:
                    loc += ':'
                results.update({loc: result.dict[self.typepath.defs.\
                                             biossettingsstring][u'Messages']})
        except:
            results.update({'SmartArray:': None})

        messagelist = list()

        errmessages = self._rdmc.app.get_error_messages()

        for result in results:
            if results[result]:
                messagelist.append((result, (results[result])))
            else:
                sys.stderr.write(u"No messages found for %s.\n" % result[:-1])

        sys.stdout.write(u"Results of the previous reboot changes:\n\n")

        for loc, messages  in messagelist:

            sys.stdout.write(u"%s\n" % loc)

            for message in messages:
                if self.typepath.flagiften:
                    message_type = message['MessageId'].split('.')
                    message_name = message_type
                else:
                    try:
                        message_type = message['MessageID'].split('.')
                        message_name = message['MessageID'].split(':')
                    except:
                        message_type = message['MessageId'].split('.')
                        message_name = message['MessageId'].split(':')

                output = ''

                if message_type[0] in errmessages:
                    try:
                        if errmessages[message_type[0]][message_name[-1]]\
                                                        ["NumberOfArgs"] == 0:
                            output = errmessages[message_type[0]]\
                                                [message_name[-1]]["Message"]
                        else:
                            output = errmessages[message_type[0]]\
                                            [message_name[-1]]["Description"]

                        sys.stdout.write(u"%s\n" % output)
                        continue
                    except:
                        pass

                if not output:
                    sys.stderr.write(u"Unable to find error message for: %s\n" \
                                                                % message_name)

        return ReturnCodes.SUCCESS

    def resultsvalidation(self, options):
        """ Results method validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        inputline = list()

        try:
            client = self._rdmc.app.get_current_client()
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

        if len(inputline):
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
