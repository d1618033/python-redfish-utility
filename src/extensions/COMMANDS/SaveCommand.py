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
""" Save Command for RDMC """

import sys
import json

from optparse import OptionParser, SUPPRESS_HELP
from collections import OrderedDict

import redfish.ris

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, \
                            InvalidCommandLineError, InvalidFileFormattingError, Encryption

#default file name
__filename__ = 'ilorest.json'

class SaveCommand(RdmcCommandBase):
    """ Constructor """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='save',\
            usage='save [OPTIONS]\n\n\tRun to save a selected type to a file' \
            '\n\texample: save --selector HpBios.\n\n\tChange the default ' \
            'output filename\n\texample: save --selector HpBios. -f ' \
            'output.json',\
            summary="Saves the selected type's settings to a file.",\
            aliases=[],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self.filename = None
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """ Main save worker function

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

        self.savevalidation(options)

        if args:
            raise InvalidCommandLineError('Save command takes no arguments.')

        sys.stdout.write("Saving configuration...\n")
        if options.filter:
            try:
                if (str(options.filter)[0] == str(options.filter)[-1])\
                        and str(options.filter).startswith(("'", '"')):
                    options.filter = options.filter[1:-1]

                (sel, val) = options.filter.split('=')
                sel = sel.strip()
                val = val.strip()
            except:
                raise InvalidCommandLineError("Invalid filter" \
                  " parameter format [filter_attribute]=[filter_value]")

            instances = self._rdmc.app.select(selector=self._rdmc.app.get_selector(), \
                                                                                fltrvals=(sel, val))
            contents = self.saveworkerfunction(instances=instances)
        else:
            contents = self.saveworkerfunction()

        if options.multisave:
            for select in options.multisave:
                self.selobj.run(select)
                contents += self.saveworkerfunction()

        if not contents:
            raise redfish.ris.NothingSelectedError
        else:
            contents = self.add_save_file_header(contents)

        if options.encryption:
            outfile = open(self.filename, 'wb')
            outfile.write(Encryption().encrypt_file(json.dumps(contents, \
                                indent=2, cls=redfish.ris.JSONEncoder), options.encryption))
        else:
            outfile = open(self.filename, 'w')
            outfile.write(json.dumps(contents, indent=2, cls=redfish.ris.JSONEncoder))
        outfile.close()
        sys.stdout.write("Configuration saved to: %s\n" % self.filename)

        if options.logout:
            self.logoutobj.run("")

        #Return code
        return ReturnCodes.SUCCESS

    def saveworkerfunction(self, instances=None):
        """ Returns the currently selected type for saving

        :param instances: list of instances from select to save
        :type instances: list.
        """

        content = self._rdmc.app.getprops(insts=instances)
        try:
            contents = [{val[self.typepath.defs.hrefstring]:val} for val in content]
        except KeyError:
            contents = [{val['links']['self'][self.typepath.defs.hrefstring]:val} for val in \
                                                                                content]
        type_string = self._rdmc.app.current_client.monolith._typestring

        templist = list()

        for content in contents:
            typeselector = None
            pathselector = None

            for path, values in content.items():
                values = self.nested_sort(values)

                for dictentry in list(values.keys()):
                    if dictentry == type_string:
                        typeselector = values[dictentry]
                        pathselector = path
                        del values[dictentry]

                if values:
                    tempcontents = dict()

                    if typeselector and pathselector:
                        tempcontents[typeselector] = {pathselector: values}
                    else:
                        raise InvalidFileFormattingError("Missing path or selector in input file.")

                templist.append(tempcontents)

        return templist

    def nested_sort(self, data):
        """ Helper function to sort all dictionary key:value pairs

        :param data: dictionary to sort
        :type data: dict.
        """

        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = self.nested_sort(value)

        data = OrderedDict(sorted(list(data.items()), key=lambda x: x[0]))

        return data

    def savevalidation(self, options):
        """ Save method validation function

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
                    inputline.extend(["-u", self._rdmc.app.config.get_username()])
                if self._rdmc.app.config.get_password():
                    inputline.extend(["-p", self._rdmc.app.config.get_password()])

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
        elif options.multisave:
            options.multisave = options.multisave.replace('"', '').replace("'", '')
            options.multisave = options.multisave.replace(' ', '').split(',')
            if not len(options.multisave) >= 1:
                raise InvalidCommandLineError("Invalid number of types in multisave option.")
            if inputline:
                inputline.extend(['--selector', options.multisave[0]])
                self.lobobj.loginfunction(inputline)
            else:
                inputline.extend([options.multisave[0]])
                self.selobj.selectfunction(inputline)
            options.multisave = options.multisave[1:]
        else:
            try:
                inputline = list()
                selector = self._rdmc.app.get_selector()
                if options.includelogs:
                    inputline.extend(["--includelogs"])
                if options.path:
                    inputline.extend(["--path", options.path])

                inputline.extend([selector])
                self.selobj.selectfunction(inputline)
            except InvalidCommandLineErrorOPTS:
                raise redfish.ris.NothingSelectedError

        #filename validations and checks
        self.filename = None

        if options.filename and len(options.filename) > 1:
            raise InvalidCommandLineError("Save command doesn't support multiple filenames.")
        elif options.filename:
            self.filename = options.filename[0]
        elif self._rdmc.app.config:
            if self._rdmc.app.config._ac__savefile:
                self.filename = self._rdmc.app.config._ac__savefile

        if not self.filename:
            self.filename = __filename__

    def add_save_file_header(self, contents):
        """ Helper function to retrieve the comments for save file

        :param contents: current save contents
        :type contents: list.
        """
        templist = list()

        headers = self._rdmc.app.create_save_header()
        templist.append(headers)

        for content in contents:
            templist.append(content)

        return templist

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
            '--logout',
            dest='logout',
            action="store_true",
            help="Optionally include the logout flag to log out of the"\
            " server after this command is completed. Using this flag when"\
            " not logged in will have no effect",
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
            '-f',
            '--filename',
            dest='filename',
            help="Use this flag if you wish to use a different"\
            " filename than the default one. The default filename is" \
            " %s." % __filename__,
            action="append",
            default=None,
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
            '--multisave',
            dest='multisave',
            help="Optionally include this flag to save multiple types to a "\
            "single file. Overrides the currently selected type."\
            "\t\t\t\t\t Usage: --multisave type1.,type2.,type3.",
            default='',
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
            '--encryption',
            dest='encryption',
            help="Optionally include this flag to encrypt/decrypt a file "\
            "using the key provided.",
            default=None
        )
        customparser.add_option(
            '-e',
            '--enc',
            dest='encode',
            action='store_true',
            help=SUPPRESS_HELP,
            default=False,
        )
