###
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
###

# -*- coding: utf-8 -*-
""" Status Command for RDMC """

import sys
import json

from argparse import ArgumentParser, SUPPRESS

from redfish.ris.utils import merge_dict

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, Encryption, \
                                                    NoCurrentSessionEstablished

class StatusCommand(RdmcCommandBase):
    """ Constructor """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='status',\
            usage='status\n\n\tRun to display all pending changes within'\
                    ' the currently\n\tselected type that need to be' \
                    ' committed\n\texample: status',\
            summary='Displays all pending changes within a selected type'\
                    ' that need to be committed.',\
            aliases=[],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)

    def run(self, line):
        """ Main status worker function

        :param line: command line input
        :type line: string.
        """
        try:
            (options, _) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.statusvalidation(options)
        contents = self._rdmc.app.status()
        selector = self._rdmc.app.selector

        if contents and options.json:
            self.jsonout(contents)
        elif contents:
            self.outputpatches(contents, selector)
        else:
            sys.stdout.write("No changes found\n")

        #Return code
        return ReturnCodes.SUCCESS

    def jsonout(self, contents):
        """ Helper function to print json output of patches

        :param contents: contents for the selection
        :type contents: string.
        """
        sys.stdout.write("Current changes found:\n")
        createdict = lambda y, x: {x:y}
        totdict = {}
        for item in contents:
            for keypath, value in item.items():
                path = keypath.split('(')[1].strip('()')
                cont = {}
                totdict[path] = cont
                for content in value:
                    val = ["List Manipulation"] if content['op'] == 'move' else \
                        [content["value"].strip('"\'')] if len(content["value"]) else [""]
                    cont = reduce(createdict, reversed([path]+content['path'].strip('/').\
                                  split('/')+val))
                    merge_dict(totdict, cont)
        sys.stdout.write(json.dumps(totdict, indent=2, sort_keys=True))#, cls=JSONEncoder)
        sys.stdout.write('\n')

    def outputpatches(self, contents, selector):
        """ Helper function for status for use in patches

        :param contents: contents for the selection
        :type contents: string.
        :param selector: type selected
        :type selector: string.
        """
        sys.stdout.write("Current changes found:\n")
        for item in contents:
            moveoperation = ""
            for key, value in item.items():
                if selector and key.lower().startswith(selector.lower()):
                    sys.stdout.write("%s (Currently selected)\n" % key)
                else:
                    sys.stdout.write("%s\n" % key)

                for content in value:
                    try:
                        if content['op'] == 'move':
                            moveoperation = '/'.join(content['path'].split('/')[1:-1])
                            continue
                    except:
                        if content[0]['op'] == 'move':
                            moveoperation = '/'.join(content[0]['path'].split('/')[1:-1])
                            continue
                    try:
                        if isinstance(content[0]["value"], int):
                            sys.stdout.write('\t%s=%s' % \
                                 (content[0]["path"][1:], content[0]["value"]))
                        elif not isinstance(content[0]["value"], bool) and \
                                            not len(content[0]["value"]) == 0:
                            if content[0]["value"][0] == '"' and \
                                                content[0]["value"][-1] == '"':
                                sys.stdout.write('\t%s=%s' % (content[0]["path"][1:], \
                                                    content[0]["value"][1:-1]))
                            else:
                                sys.stdout.write('\t%s=%s' % (content[0]["path"][1:], \
                                                     content[0]["value"]))
                        else:
                            output = content[0]["value"]

                            if not isinstance(output, bool):
                                if len(output) == 0:
                                    output = '""'

                            sys.stdout.write('\t%s=%s' % \
                                             (content[0]["path"][1:], output))
                    except:
                        if isinstance(content["value"], int):
                            sys.stdout.write('\t%s=%s' % \
                                 (content["path"][1:], content["value"]))
                        elif not isinstance(content["value"], bool) and \
                                                not len(content["value"]) == 0:
                            if content["value"][0] == '"' and \
                                                    content["value"][-1] == '"':
                                sys.stdout.write('\t%s=%s' % (content["path"][1:], \
                                                        content["value"]))
                            else:
                                sys.stdout.write('\t%s=%s' % (content["path"][1:], \
                                                        content["value"]))
                        else:
                            output = content["value"]

                            if not isinstance(output, bool):
                                if len(output) == 0:
                                    output = '""'

                            sys.stdout.write('\t%s=%s' % (content["path"][1:], output))
                    sys.stdout.write('\n')
            if moveoperation:
                sys.stdout.write("\t%s=List Manipulation\n" % moveoperation)

    def statusvalidation(self, options):
        """ Status method validation function """

        if options.encode and options.user and options.password:
            options.user = Encryption.decode_credentials(options.user)
            options.password = Encryption.decode_credentials(options.password)

        try:
            _ = self._rdmc.app.current_client
        except:
            raise NoCurrentSessionEstablished("Please login and make setting" \
                                      " changes before using status command.")

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return
        customparser.add_argument(
            '-u',
            '--user',
            dest='user',
            help="Pass this flag along with the password flag if you are"\
            "running in local higher security modes.""",
            default=None
        )
        customparser.add_argument(
            '-p',
            '--password',
            dest='password',
            help="Pass this flag along with the username flag if you are"\
            "running in local higher security modes.""",
            default=None
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
            '-e',
            '--enc',
            dest='encode',
            action='store_true',
            help=SUPPRESS,
            default=False
        )
