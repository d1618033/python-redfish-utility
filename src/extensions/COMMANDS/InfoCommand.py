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
""" Info Command for RDMC """

import sys

from optparse import OptionParser

import redfish.ris

from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, \
                                                    InfoMissingEntriesError

from rdmc_base_classes import RdmcCommandBase, HARDCODEDLIST

class InfoCommand(RdmcCommandBase):
    """ Constructor """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='info',\
            usage='info [PROPERTY] [OPTIONS]\n\n\tDisplays detailed ' \
                    'information about a property within a selected type' \
                    '\n\texample: info property\n\n\tDisplays detailed ' \
                    'information for several properties\n\twithin a selected ' \
                    'type\n\texample: info property property property\n\n\t' \
                    'Run without arguments to display properties \n\tthat ' \
                    'are available for info command\n\texample: info',\
            summary='Displays detailed information about a property' \
                    ' within a selected type.',\
            aliases=[],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commandsDict["LoginCommand"](rdmcObj)
        self.selobj = rdmcObj.commandsDict["SelectCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commandsDict["LogoutCommand"](rdmcObj)

    def run(self, line, autotest=False):
        """ Main info worker function

        :param line: command line input
        :type line: string.
        :param autotest: flag to determine if running automatictesting
        :type autotest: bool.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.infovalidation(options)

        if len(args) > 0:
            # TODO need to move the print from rdmc.app.info()
            # to here so we don't write from inside the lib
            inforesp = ''

            for item in args:
                newargs = list()
                if self._rdmc.app.get_selector().lower().startswith('bios.') \
                                        and not 'attributes' in item.lower():
                    item = "Attributes/" + item

                if "/" in item:
                    newargs = item.split("/")
                    item = newargs[0]

                contents = self._rdmc.app.info(selector=item, \
                    dumpjson=options.json, autotest=autotest, newarg=newargs, \
                                            latestschema=options.latestschema)

                if isinstance(contents, list) and not autotest:
                    if 'none' in contents and inforesp != 'success':
                        inforesp = 'none'
                    elif 'Success' in contents:
                        inforesp = 'success'

                try:
                    if not contents or inforesp == 'none':
                        raise InfoMissingEntriesError("There are no valid "\
                            "entries for info in the current instance.")
                except Exception, excp:
                    raise excp

                if len(args) > 1 and not item == args[-1]:
                    sys.stdout.write("\n************************************"\
                                     "**************\n")
        else:
            results = sorted(self._rdmc.app.info(selector=None,\
                   ignorelist=HARDCODEDLIST, latestschema=options.latestschema))

            if results:
                sys.stdout.write("Info options:\n")
                for item in results:
                    sys.stdout.write("%s\n" % item)
            else:
                raise InfoMissingEntriesError('No info items '\
                        'available in this selected type.')

        if options.logout:
            self.logoutobj.run("")

        #Return code
        return ReturnCodes.SUCCESS

    def infovalidation(self, options):
        """ Info method validation function

        :param options: command line options
        :type options: list.
        """
        inputline = list()

        if self._rdmc.opts.latestschema:
            options.latestschema = True

        if self._rdmc.app.config._ac__format.lower() == 'json':
            options.json = True

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

        if len(inputline) and options.selector:
            if options.filter:
                inputline.extend(["--filter", options.filter])
            if options.includelogs:
                inputline.extend(["--includelogs"])
            if options.path:
                inputline.extend(["--path", options.path])

            inputline.extend(["--selector", options.selector])
            self.lobobj.loginfunction(inputline)
        elif options.selector:
            if options.filter:
                inputline.extend(["--filter", options.filter])
            if options.includelogs:
                inputline.extend(["--includelogs"])
            if options.path:
                inputline.extend(["--path", options.path])

            inputline.extend([options.selector])
            self.selobj.selectfunction(inputline)
        else:
            try:
                inputline = list()
                selector = self._rdmc.app.get_selector()
                if options.filter:
                    inputline.extend(["--filter", options.filter])
                if options.includelogs:
                    inputline.extend(["--includelogs"])
                if options.path:
                    inputline.extend(["--path", options.path])

                inputline.extend([selector])
                self.selobj.selectfunction(inputline)
            except:
                raise redfish.ris.NothingSelectedError

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
            '--selector',
            dest='selector',
            help="Optionally include this flag to select a type to run"\
             " the current command on. Use this flag when you wish to"\
             " select a type without entering another command, or if you"\
              " wish to work with a type that is different from the one"\
              " you currently have selected.",
            default=None,
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
            '--logout',
            dest='logout',
            action="store_true",
            help="Optionally include the logout flag to log out of the"\
            " server after this command is completed. Using this flag when"\
            " not logged in will have no effect",
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
            '--latestschema',
            dest='latestschema',
            action='store_true',
            help="Optionally use the latest schema instead of the one "\
            "requested by the file. Note: May cause errors in some data "\
            "retrieval due to difference in schema versions.",
            default=None
        )
