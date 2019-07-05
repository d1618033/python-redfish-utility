###
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
###

# -*- coding: utf-8 -*-
""" Factory Reset Controller Command for rdmc """

import sys
from collections import OrderedDict

from optparse import OptionParser, SUPPRESS_HELP
from six.moves import input

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, InvalidCommandLineErrorOPTS, \
                        Encryption

def controller_parse(option, opt_str, value, parser):
    """ Controller Option Parsing

        :param option: command line option
        :type option: attributes
        :param opt_str: parsed option string
        :type opt_str: string
        :param value: parsed option value
        :type value: attribute
        :param parser: OptionParser instance
        :type parser: object
    """
    setattr(parser.values, option.dest, [])
    use_slot = False
    use_indx = False
    for _opt in value.split(','):
        if _opt.isdigit() and not use_slot:
            use_indx = True
            parser.values.controller.append(int(_opt))
        elif "slot" in _opt.lower() and not use_indx:
            use_slot = True
            parser.values.controller.append((_opt.replace('\"', '')).strip())
        else:
            raise InvalidCommandLineErrorOPTS("An invalid option or combination of options were " \
                                              "used to specify a smart array controller.")
    if use_indx:
        parser.values.controller.sort()

class FactoryResetControllerCommand(RdmcCommandBase):
    """ Factory reset controller command """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='factoryresetcontroller',\
            usage='factoryresetcontroller [OPTIONS]\n\n\tTo factory reset a controller ' \
                'by index.\n\texample: factoryresetcontroller --controller=2' \
                '\n\tor by slot position.' \
                '\n\texample: factoryresetcontroller --controller "Slot1" ' \
                '\n\n\tTo factory reset all available smart array controllers' \
                '\n\texample: factoryresetcontroller --all', \
            summary='Factory resets a controller by index or location.',\
            aliases=['factoryresetcontroller'],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)

    def run(self, line):
        """ Main disk inventory worker function

        :param line: command line input
        :type line: string.
        """
        try:
            (options, _) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.frcontrollervalidation(options)

        self.selobj.selectfunction("SmartStorageConfig.")
        content = OrderedDict()
        for controller in self._rdmc.app.getprops():
            try:
                content[int(controller.get('Location', None).split(' ')[-1])] = controller
            except (AttributeError, KeyError):
                pass

        controldict = {}
        use_slot = False
        use_indx = False

        for _opt in options.controller:
            found = False
            for pos, control in enumerate(content):
                if isinstance(_opt, int) and not use_slot:
                    if pos == (_opt - 1):
                        controldict[_opt] = content[control]
                        found = True
                        use_indx = True
                elif _opt.lower() == content[control]["Location"].lower() and not use_indx:
                    controldict[int(content[control]["Location"].split(' ')[-1])] = \
                                                                                content[control]
                    found = True
                    use_slot = True
                if found:
                    break

            if not found:
                sys.stderr.write("\nController \'%s\' not found in the current inventory " \
                                 "list.\n" % _opt)

        if options.all:
            controldict.update(content)

        if not options.force:
            while True:
                if options.all:
                    ans = input("Are you sure you would like to factory reset all available " \
                                "smart array controllers? (y/n)\n")
                else:
                    ans = input("Are you sure you would like to factory reset controller(s): " \
                                "\'%s\' ? (y/n)\n" % controldict.keys())
                if ans.lower() == 'y':
                    break
                elif ans.lower() == 'n':
                    sys.stdout.write("Aborting factory reset of controllers.\n")
                    return None

        for indx, controller in enumerate(controldict):
            self._rdmc.app.patch_handler(controldict[controller]["@odata.id"], \
                                         {"Actions": [{"Action": "FactoryReset"}], \
                                          "DataGuard": "Disabled"})

            sys.stdout.write("[%d]: %s - has been reset to factory defaults.\n" % (indx + 1, \
                                                              controldict[controller]["Location"]))

        #Return code
        return ReturnCodes.SUCCESS

    def frcontrollervalidation(self, options):
        """ Factory reset controller validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        inputline = list()
        runlogin = False

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
                    inputline.extend(["-u", self._rdmc.app.config.get_username()])
                if self._rdmc.app.config.get_password():
                    inputline.extend(["-p", self._rdmc.app.config.get_password()])

        if inputline or not client:
            runlogin = True
            if not inputline:
                sys.stdout.write('Local login initiated...\n')

        if runlogin:
            self.lobobj.loginfunction(inputline)

        if not options.all and not options.controller:
            raise InvalidCommandLineErrorOPTS("Please specify a controller or use \'--all\'.")

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
            '--controller',
            dest='controller',
            action='callback',
            callback=controller_parse,
            help="""Use this flag to select the corresponding controller "\
                 "using either the slot number or index.""",
            type="string",
            default=[],
        )
        customparser.add_option(
            '--all',
            dest='all',
            help="""Use this flag to reset all available smart array controllers to factory """ \
                 """defaults """,
            action="store_true",
            default=False,
        )
        customparser.add_option(
            '--force',
            dest='force',
            help="""Use this flag to override the "are you sure?" text when """ \
                 """clearing controller configuration.""",
            action="store_true",
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
