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
""" Get Command for RDMC """

from optparse import OptionParser, SUPPRESS_HELP
from collections import (OrderedDict)

import six

import redfish.ris

from rdmc_base_classes import RdmcCommandBase, HARDCODEDLIST
from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, UI, Encryption, \
                    NoContentsFoundForOperationError, InvalidCommandLineError

class GetCommand(RdmcCommandBase):
    """ Constructor """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='get',\
            usage='get [PROPERTY] [OPTIONS]\n\n\tTo retrieve all' \
                    ' the properties run without arguments\n\texample: get' \
                    '\n\n\tTo retrieve multiple properties use the following' \
                    ' example\n\texample: get <property> <property> ' \
                    '<property>\n\n\tTo change output style format provide'\
                    ' the json flag\n\texample: get --json',\
            summary='Displays the current value(s) of a' \
                    ' property(ies) within a selected type.',\
            aliases=[],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """ Main get worker function

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

        self.getvalidation(options)

        filtr = (None, None)

        if options.filter:
            try:
                if (str(options.filter)[0] == str(options.filter)[-1])\
                        and str(options.filter).startswith(("'", '"')):
                    options.filter = options.filter[1:-1]

                (sel, val) = options.filter.split('=')
                filtr = (sel.strip(), val.strip())

            except:
                raise InvalidCommandLineError("Invalid filter" \
                  " parameter format [filter_attribute]=[filter_value]")

        self.getworkerfunction(args, options, results=None, uselist=True, filtervals=filtr,\
                               readonly=options.noreadonly)

        #Return code
        return ReturnCodes.SUCCESS

    def getworkerfunction(self, args, options, readonly=False, filtervals=(None, None),\
                                results=None, uselist=False):
        """ main get worker function

        :param args: command line arguments
        :type args: list.
        :param options: command line options
        :type options: list.
        :param line: command line input
        :type line: string.
        :param readonly: remove readonly properties
        :type readonly: bool
        :param filtervals: filter key value pair (Key,Val)
        :type filtervals: tuple
        :param results: current results collected
        :type results: string.
        :param uselist: use reserved properties list to filter results
        :type uselist: boolean.
        """
        content = []
        nocontent = set()
        instances = None

        #For rest redfish compatibility of bios.
        args = [args] if args and isinstance(args, six.string_types) else args
        args = ["Attributes/"+arg if self._rdmc.app.get_selector().lower().\
                startswith('bios.') and 'attributes' not in arg.lower() else arg \
                                                for arg in args] if args else args
        if filtervals[0]:
            instances = self._rdmc.app.select(selector=self._rdmc.app.get_selector(), \
                                                                    fltrvals=filtervals)

        try:
            contents = self._rdmc.app.getprops(props=args, remread=readonly, nocontent=nocontent, \
                                                                                insts=instances)
            uselist = False if readonly else uselist
        except redfish.ris.rmc_helper.EmptyRaiseForEAFP:
            contents = self._rdmc.app.getprops(props=args, nocontent=nocontent)
        for ind, content in enumerate(contents):
            if 'bios.' in self._rdmc.app.get_selector().lower() and \
                    'Attributes' in list(content.keys()):
                content.update(content['Attributes'])
                del content['Attributes']
            contents[ind] = OrderedDict(sorted(list(content.items()), key=lambda x: x[0]))
        if uselist:
            map(lambda x: self.removereserved(x), contents)
        if results:
            return contents

        contents = contents[0] if len(contents) == 1 else contents
        if options and options.json and contents:
            UI().print_out_json(contents)
        elif contents:
            UI().print_out_human_readable(contents)

        if nocontent:
            strtoprint = ', '.join(str(val) for val in nocontent)
            raise NoContentsFoundForOperationError('No ' \
                               'contents found for entry: %s' % strtoprint)
        if options.logout:
            self.logoutobj.run("")

    def removereserved(self, entry):
        """ function to remove reserved properties

        :param entry: dictionary to remove reserved properties from
        :type entry: dict.
        """

        for key, val in list(entry.items()):
            if key.lower() in HARDCODEDLIST or '@odata' in key.lower():
                del entry[key]
            elif isinstance(val, list):
                for item in entry[key]:
                    if isinstance(item, dict):
                        self.removereserved(item)
                        if all([True if not test else False for test in entry[key]]):
                            del entry[key]
            elif isinstance(val, dict):
                self.removereserved(val)
                if all([True if not test else False for test in entry[key]]):
                    del entry[key]

    def getvalidation(self, options):
        """ get method validation function

        :param options: command line options
        :type options: list.
        """
        inputline = list()

        if self._rdmc.app.config._ac__format.lower() == 'json':
            options.json = True

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
                    inputline.extend(["-u", \
                                  self._rdmc.app.config.get_username()])
                if self._rdmc.app.config.get_password():
                    inputline.extend(["-p", \
                                  self._rdmc.app.config.get_password()])

        if inputline and options.selector:
            if options.includelogs:
                inputline.extend(["--includelogs"])
            if options.path:
                inputline.extend(["--path", options.path])

            inputline.extend(["--selector", options.selector])
            self.lobobj.loginfunction(inputline)
        elif options.selector:
            if options.includelogs:
                inputline.extend(["--includelogs"])
            if options.path:
                inputline.extend(["--path", options.path])
            if options.ref:
                inputline.extend(["--refresh"])

            inputline.extend([options.selector])
            self.selobj.selectfunction(inputline)
        else:
            try:
                inputline = list()
                selector = self._rdmc.app.get_selector()
                if options.includelogs:
                    inputline.extend(["--includelogs"])
                if options.path:
                    inputline.extend(["--path", options.path])
                if options.ref:
                    inputline.extend(["--refresh"])

                inputline.extend([selector])
                self.selobj.selectfunction(inputline)
            except InvalidCommandLineErrorOPTS:
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
            '--path',
            dest='path',
            help="Optionally set a starting point for data collection during login."\
            " If you do not specify a starting point, the default path"\
            " will be /redfish/v1/. Note: The path flag can only be specified"\
            " at the time of login. Warning: Only for advanced users, and generally "\
            "not needed for normal operations.",
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
            '--noreadonly',
            dest='noreadonly',
            action="store_true",
            help="Optionally include this flag if you wish to only show"\
            " properties that are not read-only. This is useful to see what "\
            "is configurable with the selected type(s).",
            default=False
        )
        customparser.add_option(
            '--refresh',
            dest='ref',
            action="store_true",
            help="Optionally reload the data of selected type and clear \
                                            patches from current selection.",
            default=False,
        )
        customparser.add_option(
            '-e',
            '--enc',
            dest='encode',
            action='store_true',
            help=SUPPRESS_HELP,
            default=False,
        )
