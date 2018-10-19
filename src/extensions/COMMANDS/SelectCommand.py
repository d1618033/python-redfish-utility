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
""" Select Command for RDMC """

import sys

from optparse import OptionParser, SUPPRESS_HELP

import redfish.ris

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, Encryption, \
                                                    InvalidCommandLineErrorOPTS

class SelectCommand(RdmcCommandBase):
    """ Constructor """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='select',\
            usage='select [TYPE] [OPTIONS]\n\n\tRun without a type to display' \
            ' currently selected type\n\texample: select\n\n\tIn order to ' \
            'remove the need of including the version\n\twhile selecting you' \
            ' can simply enter the type name\n\tuntil the first period\n\t' \
            'example: select HpBios.',\
            summary='Selects the object type to be used.',\
            aliases=['sel'],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)

    def selectfunction(self, line):
        """ Main select worker function

        :param line: command line input
        :type line: string.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        if options.encode and options.user and options.password:
            options.user = Encryption.decode_credentials(options.user)
            options.password = Encryption.decode_credentials(options.password)

        self.selectvalidation(options)

        try:
            if args:
                sel = None
                val = None

                if options.filter:
                    try:
                        if (str(options.filter)[0] == str(options.filter)[-1])\
                                and str(options.filter).startswith(("'", '"')):
                            options.filter = options.filter[1:-1]

                        (sel, val) = options.filter.split('=')
                        sel = sel.strip()
                        val = val.strip()

                        if val.lower() == "true" or val.lower() == "false":
                            val = val.lower() in ("yes", "true", "t", "1")
                    except:
                        raise InvalidCommandLineError("Invalid filter" \
                          " parameter format [filter_attribute]=[filter_value]")
                else:
                    self._rdmc.app.erase_filter_settings()

                selections = self._rdmc.app.select(query=args, sel=sel, val=val)

                if self._rdmc.opts.verbose and selections:
                    templist = list()
                    sys.stdout.write("Selected option(s): ")

                    for item in selections:
                        if item.type not in templist:
                            templist.append(item.type)

                    sys.stdout.write('%s' % ', '.join(map(str, templist)))
                    sys.stdout.write('\n')
            else:
                selector = self._rdmc.app.get_selector()

                if selector:
                    sys.stdout.write("Current selection: '%s'" % selector)
                    sys.stdout.write('\n')
                else:
                    raise InvalidCommandLineError("No type currently selected."\
                                " Please use the 'types' command to\nget a" \
                                " list of types, or pass your type by using" \
                                " the '--selector' flag.")

        except redfish.ris.InstanceNotFoundError, infe:
            raise redfish.ris.InstanceNotFoundError(infe)

    def selectvalidation(self, options):
        """ Select data validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        runlogin = False
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

        if not inputline and not client:
            sys.stdout.write(u'Local login initiated...\n')
        if inputline:
            runlogin = True
        if options.includelogs:
            inputline.extend(["--includelogs"])
        if options.path:
            inputline.extend(["--path", options.path])
        if not client or runlogin:
            self.lobobj.loginfunction(inputline)

    def run(self, line):
        """ Wrapper function for main select function

        :param line: entered command line
        :type line: list.
        """
        self.selectfunction(line)

        #Return code
        return ReturnCodes.SUCCESS

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
            '--includelogs',
            dest='includelogs',
            action="store_true",
            help="Optionally include logs in the data retrieval process.",
            default=False,
        )
        customparser.add_option(
            '--filter',
            dest='filter',
            help="Optionally set a filter value for a filter attribute."\
            " This uses the provided filter for the currently selected"\
            " type. Note: Use this flag to narrow down your results. For"\
            " example, selecting a common type might return multiple"\
            " objects that are all of that type. If you want to modify"\
            " the properties of only one of those objects, use the filter"\
            " flag to narrow down results based on properties."\
            "\t\t\t\t\t Usage: --filter [ATTRIBUTE]=[VALUE]",
            default=None,
        )
        customparser.add_option(
            '--path',
            dest='path',
            help="Optionally set a starting point for data collection."\
            " If you do not specify a starting point, the default path"\
            " will be /rest/v1. Note: The path flag can only be specified"\
            " at the time of login, so if you are already logged into the"\
            " server, the path flag will not change the path. If you are"\
            " entering a command that isn't the login command, but include"\
            " your login information, you can still specify the path flag"\
            " there.  ",
            default=None,
        )
        customparser.add_option(
            '--biospassword',
            dest='biospassword',
            help="Select this flag to input a BIOS password. Include this"\
            " flag if second-level BIOS authentication is needed for the"\
            " command to execute.",
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
