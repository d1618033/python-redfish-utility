###
# Copyright 2020 Hewlett Packard Enterprise, Inc. All rights reserved.
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
""" Set Command for RDMC """

import sys

from argparse import ArgumentParser

import redfish.ris

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group, \
                                login_select_validation
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
        InvalidCommandLineErrorOPTS, UI, InvalidOrNothingChangedSettingsError

class SetCommand(RdmcCommandBase):
    """ Constructor """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='set',\
            usage='set [PROPERTY=VALUE] [OPTIONS]\n\n\tSetting a ' \
                'single level property example:\n\tset property=value\n\n\t' \
                'Setting multiple single level properties example:\n\tset ' \
                'property=value property=value property=value\n\n\t' \
                'Setting a multi level property example:\n\tset property/' \
                'subproperty=value',\
            summary='Changes the value of a property within the'\
                    ' currently selected type.',\
            aliases=[],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj

        self.comobj = rdmcObj.commands_dict["CommitCommand"](rdmcObj)
        #self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)

        #remove reboot option if there is no reboot command
        try:
            self.rebootobj = rdmcObj.commands_dict["RebootCommand"](rdmcObj)
        except KeyError:
            self.parser.remove_option('--reboot')

    def setfunction(self, line, skipprint=False):
        """ Main set worker function

        :param line: command line input
        :type line: string.
        :param skipprint: boolean to determine output
        :type skipprint: boolean.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        if not self._rdmc.interactive and not self._rdmc.app.cache:
            raise InvalidCommandLineError("The 'set' command is not useful in "\
                                      "non-interactive and non-cache modes.")

        self.setvalidation(options)
        fsel = None
        fval = None
        if args:

            if options.filter:
                try:
                    (fsel, fval) = str(options.filter).strip('\'\" ').split('=')
                    (fsel, fval) = (fsel.strip(), fval.strip())
                except:
                    raise InvalidCommandLineError("Invalid filter" \
                      " parameter format [filter_attribute]=[filter_value]")

            if any([s.lower().startswith('adminpassword=') for s in args]) \
                    and not any([s.lower().startswith('oldadminpassword=') for s in args]):
                raise InvalidCommandLineError("'OldAdminPassword' must also " \
                            "be set with the current password \nwhen " \
                            "changing 'AdminPassword' for security reasons.")

            for arg in args:
                if arg[0] == '"' and arg[-1] == '"':
                    arg = arg[1:-1]

                if self._rdmc.app.selector.lower().startswith('bios.'):
                    if 'attributes' not in arg.lower():
                        arg = "Attributes/" + arg

                try:
                    (sel, val) = arg.split('=')
                    sel = sel.strip().lower()
                    val = val.strip('"\'')

                    if val.lower() == "true" or val.lower() == "false":
                        val = val.lower() in ("yes", "true", "t", "1")
                except:
                    raise InvalidCommandLineError("Invalid set parameter format. [Key]=[Value]")

                newargs = list()

                if "/" in sel and "/" not in str(val):
                    newargs = sel.split("/")
                elif "/" in sel:
                    items = arg.split('=', 1)
                    newargs = items[0].split('/')

                if not isinstance(val, bool):
                    if val:
                        if val[0] == "[" and val[-1] == "]":
                            val = val[1:-1].split(',')

                payload = {newargs[-1]:val} if newargs else {sel:val}
                if newargs:
                    for key in newargs[:-1][::-1]:
                        payload = {key:payload}

                try:
                    contents = self._rdmc.app.loadset(seldict=payload,\
                        latestschema=options.latestschema, fltrvals=(fsel, fval), \
                                        uniqueoverride=options.uniqueoverride)
                    if not contents:
                        if not sel.lower() == 'oldadminpassword':
                            raise InvalidOrNothingChangedSettingsError("Setting " \
                                                "for '%s' is the same as " \
                                                "the current value." % sel)
                    elif contents == "No entries found":
                        raise InvalidOrNothingChangedSettingsError("No " \
                                       "entries found in the current " \
                                       "selection for the setting '%s'." % sel)
                    elif contents == "reverting":
                        sys.stdout.write("Removing previous patch and "\
                                         "returning to the original value.\n")
                    else:
                        for content in contents:
                            try:
                                if self._rdmc.opts.verbose:
                                    sys.stdout.write("Added the following patch:\n")
                                    UI().print_out_json(content)
                            except AttributeError:
                                pass

                except redfish.ris.ValidationError as excp:
                    errs = excp.get_errors()

                    for err in errs:
                        if err.sel and err.sel.lower() == 'adminpassword':
                            types = self._rdmc.app.monolith.types

                            for item in types:
                                for instance in types[item]["Instances"]:
                                    if 'hpbios.' in instance.maj_type.lower():
                                        _ = [instance.patches.remove(patch) for \
                                         patch in instance.patches if \
                                         patch.patch[0]['path'] == '/OldAdminPassword']

                        if isinstance(err, redfish.ris.RegistryValidationError):
                            sys.stderr.write(err.message)
                            sys.stderr.write('\n')

                            if err.reg and not skipprint:
                                err.reg.print_help(sel)
                                sys.stderr.write('\n')

                    raise redfish.ris.ValidationError(excp)

            if options.commit:
                self.comobj.commitfunction(options)

            if options.reboot and not options.commit:
                self.rebootobj.run(options.reboot)

            #if options.logout:
            #    self.logoutobj.run("")

        else:
            raise InvalidCommandLineError("Missing parameters for 'set' command.\n")

    def run(self, line, skipprint=False):
        """ Main set function

        :param line: command line input
        :type line: string.
        :param skipprint: boolean to determine output
        :type skipprint: boolean.
        """
        self.setfunction(line, skipprint=skipprint)

        #Return code
        return ReturnCodes.SUCCESS

    def setvalidation(self, options):
        """ Set data validation function """

        if self._rdmc.opts.latestschema:
            options.latestschema = True
        if self._rdmc.config.commit.lower() == 'true':
            options.commit = True
        try:
            login_select_validation(self, options)
        except redfish.ris.NothingSelectedError:
            raise redfish.ris.NothingSelectedSetError("")

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        add_login_arguments_group(customparser)

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
        customparser.add_argument(
            '--commit',
            dest='commit',
            action="store_true",
            help="Use this flag when you are ready to commit all pending"\
            " changes. Note that some changes made in this way will be updated"\
            " instantly, while others will be reflected the next time the"\
            " server is started.",
            default=None,
        )
        '''
        customparser.add_argument(
            '--logout',
            dest='logout',
            action="store_true",
            help="Optionally include the logout flag to log out of the"\
            " server after this command is completed. Using this flag when"\
            " not logged in will have no effect",
            default=None,
        )
        '''
        customparser.add_argument(
            '--biospassword',
            dest='biospassword',
            help="Select this flag to input a BIOS password. Include this"\
            " flag if second-level BIOS authentication is needed for the"\
            " command to execute. This option is only used on Gen 9 systems.",
            default=None,
        )
        customparser.add_argument(
            '--reboot',
            dest='reboot',
            help="Use this flag to perform a reboot command function after"\
            " completion of operations.  For help with parameters and"\
            " descriptions regarding the reboot flag, run help reboot.",
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
        customparser.add_argument(
            '--uniqueitemoverride',
            dest='uniqueoverride',
            action='store_true',
            help="Override the measures stopping the tool from writing "\
            "over items that are system unique.",
            default=None
        )
