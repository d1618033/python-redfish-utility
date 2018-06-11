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
""" Set Command for RDMC """

import sys

from optparse import OptionParser

import redfish.ris

from rdmc_base_classes import RdmcCommandBase
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
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj

        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)
        self.comobj = rdmcObj.commands_dict["CommitCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)

        #remove reboot option if there is no reboot command
        try:
            self.rebootobj = rdmcObj.commands_dict["RebootCommand"](rdmcObj)
        except:
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
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        if not self._rdmc.interactive and \
                                        not self._rdmc.app.config.get_cache():
            raise InvalidCommandLineError("The 'set' command is not useful in "\
                                      "non-interactive and non-cache modes.")

        self.setvalidation(options)

        if args:
            if any([s.lower().startswith('adminpassword=') for s in args]) \
                    and not any([s.lower().startswith('oldadminpassword=') \
                                                                for s in args]):
                raise InvalidCommandLineError("'OldAdminPassword' must also " \
                            "be set with the current password \nwhen " \
                            "changing 'AdminPassword' for security reasons.")

            for arg in args:
                if arg[0] == '"' and arg[-1] == '"':
                    arg = arg[1:-1]

                if self._rdmc.app.get_selector().lower().startswith('bios.'):
                    if 'attributes' not in arg.lower():
                        arg = "Attributes/" + arg

                try:
                    (sel, val) = arg.split('=')
                    sel = sel.strip().lower()
                    val = val.strip()
                    if val[0] in ("'", '"') and val[-1] in ("'", '"'):
                        val = val[1:-1]

                    if val.lower() == "true" or val.lower() == "false":
                        val = val.lower() in ("yes", "true", "t", "1")
                except:
                    raise InvalidCommandLineError("Invalid set parameter " \
                                                  "format. [Key]=[Value]")

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
                                        latestschema=options.latestschema,\
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
                            if self._rdmc.opts.verbose:
                                sys.stdout.write("Added the following" \
                                                                    " patch:\n")
                                UI().print_out_json(content)

                except redfish.ris.ValidationError, excp:
                    errs = excp.get_errors()

                    for err in errs:
                        if err.sel.lower() == 'adminpassword':
                            types = self._rdmc.app.current_client.monolith.types

                            for item in types:
                                for instance in types[item]["Instances"]:
                                    if 'hpbios.' in instance.type.lower():
                                        _ = [instance.patches.remove(patch) for \
                                         patch in instance.patches if \
                                         patch.patch[0]['path'] == \
                                         '/OldAdminPassword']

                        if isinstance(err, redfish.ris.RegistryValidationError):
                            sys.stderr.write(err.message)
                            sys.stderr.write(u'\n')

                            if err.reg and not skipprint:
                                err.reg.print_help(sel)
                                sys.stderr.write(u'\n')

                    raise redfish.ris.ValidationError(excp)

            if options.commit:
                self.comobj.commitfunction(options)

            if options.reboot and not options.commit:
                self.rebootobj.run(options.reboot)

            if options.logout:
                self.logoutobj.run("")

        else:
            raise InvalidCommandLineError("Missing parameters "\
                    "for 'set' command.\n")

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
        inputline = list()

        if self._rdmc.opts.latestschema:
            options.latestschema = True
        if self._rdmc.app.config._ac__commit.lower() == 'true':
            options.commit = True

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
            if options.filter:
                inputline.extend(["--filter", options.filter])
            if options.includelogs:
                inputline.extend(["--includelogs"])
            if options.path:
                inputline.extend(["--path", options.path])
            if options.biospassword:
                inputline.extend(["--biospassword", options.biospassword])

            inputline.extend(["--selector", options.selector])
            self.lobobj.loginfunction(inputline)
        elif options.selector:
            if options.filter:
                inputline.extend(["--filter", options.filter])
            if options.includelogs:
                inputline.extend(["--includelogs"])
            if options.path:
                inputline.extend(["--path", options.path])
            if options.biospassword:
                inputline.extend(["--biospassword", options.biospassword])

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
                if options.biospassword:
                    inputline.extend(["--biospassword", options.biospassword])

                inputline.extend([selector])
                self.selobj.selectfunction(inputline)
            except:
                raise redfish.ris.NothingSelectedSetError

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
            '--commit',
            dest='commit',
            action="store_true",
            help="Use this flag when you are ready to commit all the"\
            " changes for the current selection. Including the commit"\
            " flag will log you out of the server after the command is"\
            " run. Note that some changes made in this way will be updated"\
            " instantly, while others will be reflected the next time the"\
            " server is started.",
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
            '--path',
            dest='path',
            help="Optionally set a starting point for data collection."\
            " If you do not specify a starting point, the default path"\
            " will be /redfish/v1/. Note: The path flag can only be specified"\
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
            '--reboot',
            dest='reboot',
            help="Use this flag to perform a reboot command function after"\
            " completion of operations.  For help with parameters and"\
            " descriptions regarding the reboot flag, run help reboot.",
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
        customparser.add_option(
            '--uniqueitemoverride',
            dest='uniqueoverride',
            action='store_true',
            help="Override the measures stopping the tool from writing "\
            "over items that are system unique.",
            default=None
        )
