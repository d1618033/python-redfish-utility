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
""" Info Command for RDMC """

import sys

from argparse import ArgumentParser

import redfish.ris

from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, UI, InfoMissingEntriesError,\
                        Encryption

from rdmc_base_classes import RdmcCommandBase, HARDCODEDLIST, add_login_arguments_group

class InfoCommand(RdmcCommandBase):
    """ Constructor """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='info',\
            usage='info [PROPERTY] [OPTIONS]\n\n\tDisplays detailed ' \
                    'information about a property within a selected type' \
                    '\n\texample: info property\n\n\tDisplays detailed ' \
                    'information for several properties\n\twithin a selected ' \
                    'type\n\texample: info property property/sub-property property\n\n\t' \
                    'Run without arguments to display properties \n\tthat ' \
                    'are available for info command\n\texample: info',\
            summary='Displays detailed information about a property within a selected type.',\
            aliases=[],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)

    def run(self, line, autotest=False):
        """ Main info worker function

        :param line: command line input
        :type line: string.
        :param autotest: flag to determine if running automatictesting
        :type autotest: bool.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.infovalidation(options)

        if args:
            for item in args:
                if self._rdmc.app.selector.lower().startswith('bios.') \
                                        and not 'attributes' in item.lower():
                    if not (item.lower() in HARDCODEDLIST or '@odata' in item.lower()):
                        item = "Attributes/" + item

                outdata = self._rdmc.app.info(props=item, dumpjson=options.json, \
                                                latestschema=options.latestschema)

                if autotest:
                    return outdata
                if outdata and options.json:
                    UI().print_out_json(outdata)
                elif outdata:
                    sys.stdout.write(outdata)

                if not outdata:
                    raise InfoMissingEntriesError("There are no valid "\
                            "entries for info in the current instance.")
                else:
                    if len(args) > 1 and not item == args[-1]:
                        sys.stdout.write("\n************************************"\
                                     "**************\n")
        else:
            results = sorted(self._rdmc.app.info(props=None,\
                   ignorelist=HARDCODEDLIST, latestschema=options.latestschema))

            if results and autotest:
                return results
            elif results:
                sys.stdout.write("Info options:\n")
                for item in results:
                    sys.stdout.write("%s\n" % item)
            else:
                raise InfoMissingEntriesError('No info items '\
                        'available for this selected type. Try running with the '\
                        '--latestschema flag.')

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

            inputline.extend([options.selector])
            self.selobj.selectfunction(inputline)
        else:
            try:
                inputline = list()
                selector = self._rdmc.app.selector
                if options.includelogs:
                    inputline.extend(["--includelogs"])
                if options.path:
                    inputline.extend(["--path", options.path])

                inputline.extend([selector])
                self.selobj.selectfunction(inputline)
            except redfish.ris.NothingSelectedError:
                raise redfish.ris.NothingSelectedError

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        add_login_arguments_group(customparser, full=True)

        customparser.add_argument(
            '--selector',
            dest='selector',
            help="Optionally include this flag to select a type to run"\
             " the current command on. Use this flag when you wish to"\
             " select a type without entering another command, or if you"\
              " wish to work with a type that is different from the one"\
              " you currently have selected.",
            default=None,
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
            '--logout',
            dest='logout',
            action="store_true",
            help="Optionally include the logout flag to log out of the"\
            " server after this command is completed. Using this flag when"\
            " not logged in will have no effect",
            default=None,
        )
        customparser.add_argument(
            '--latestschema',
            dest='latestschema',
            action='store_true',
            help="Optionally use the latest schema instead of the one "\
            "requested by the file. Note: May cause errors in some data "\
            "retrieval due to difference in schema versions.",
            default=None
        )
