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
"""This is the helper module for RDMC"""

#---------Imports---------

import os
import sys
import glob
import shlex

from argparse import ArgumentParser, Action, _ArgumentGroup, SUPPRESS, RawDescriptionHelpFormatter

import six

from redfish.ris import NothingSelectedError

import cliutils
import versioning
import rdmc_helper

#---------End of imports---------

#Using hard coded list until better solution is found
HARDCODEDLIST = ["name", "modified", "type", "description",
                 "attributeregistry", "links", "settingsresult",
                 "actions", "availableactions", "id", "extref"]

#class _SilentAction(Action):
#    def __init__(self, option_strings, dest, nargs, **kwargs):
#        super(_SilentAction, self).__init__(option_strings, dest, nargs, **kwargs)
#    def __call__(self, parser, namespace, values, option_strings):
#        """ Silent action helper"""
#
#        pass


def add_login_arguments_group(parser):
    """Adds login arguments to the passed parser

    :param parser: The parser to add the login option group to
    :type parser: ArgumentParser
    """
    group = parser.add_argument_group('LOGIN OPTIONS', 'Options for logging in to a system '\
                                      'before the command is run.')
    group.add_argument(
        '--url',
        dest='url',
        help="Use the provided iLO URL to login.",
        default=None)
    group.add_argument(
        '-u',
        '--user',
        dest='user',
        help="If you are not logged in yet, including this flag along"\
        " with the password and URL flags can be used to login to a"\
        " server in the same command.",
        default=None)
    group.add_argument(
        '-p',
        '--password',
        dest='password',
        help="""Use the provided iLO password to log in.""",
        default=None)
    group.add_argument(
        '--https',
        dest='https_cert',
        help="Use the provided CA bundle or SSL certificate with your login to connect "\
            "securely to the system in remote mode. This flag has no effect in local mode.",
        default=None)
    group.add_argument(
        '-e',
        '--enc',
        dest='encode',
        action='store_true',
        help=SUPPRESS,
        default=False)
    group.add_argument(
        '--includelogs',
        dest='includelogs',
        action="store_true",
        help="Optionally include logs in the data retrieval process.",
        default=False)
    group.add_argument(
        '--path',
        dest='path',
        help="Optionally set a starting point for data collection during login."\
        " If you do not specify a starting point, the default path"\
        " will be /redfish/v1/. Note: The path flag can only be specified"\
        " at the time of login. Warning: Only for advanced users, and generally "\
        "not needed for normal operations.",
        default=None)
    group.add_argument(
        '--logout',
        dest='logout',
        action="store_true",
        help="Logout after the completion of the command.",
        default=None)

def login_select_validation(command_obj, options, skipbuild=False):
    """ Combined validation function to login and select with other commands. Not for use with
    login or select commands themselves. Make sure your command imports options from
    add_login_arguments_group or there will be errors.

    :param command_obj: the command object instance
    :type command_obj: list.
    :param options: command line options
    :type options: list.
    :param skipbuild: flag to only login and skip monolith build
    :type skipbuild: bool.
    """

    logobj = command_obj._rdmc.commands_dict["LoginCommand"](command_obj._rdmc)
    selobj = command_obj._rdmc.commands_dict["SelectCommand"](command_obj._rdmc)

    inputline = list()
    client = None
    loggedin = False

    if hasattr(options, 'json') and command_obj._rdmc.config.format.lower() == 'json':
        options.json = True

    try:
        client = command_obj._rdmc.app.current_client
    except:
        if options.user or options.password or options.url:
            if options.url:
                inputline.extend([options.url])
            if options.user:
                if options.encode:
                    options.user = rdmc_helper.Encryption.decode_credentials(options.user)
                inputline.extend(["-u", options.user])
            if options.password:
                if options.encode:
                    options.password = rdmc_helper.Encryption.decode_credentials(options.password)
                inputline.extend(["-p", options.password])
            if options.https_cert:
                inputline.extend(["--https", options.https_cert])
        else:
            if command_obj._rdmc.config.url:
                inputline.extend([command_obj._rdmc.config.url])
            if command_obj._rdmc.config.username:
                inputline.extend(["-u", command_obj._rdmc.config.username])
            if command_obj._rdmc.config.password:
                inputline.extend(["-p", command_obj._rdmc.config.password])
            if command_obj._rdmc.config.ssl_cert:
                inputline.extend(["--https", command_obj._rdmc.config.ssl_cert])

        if options.includelogs:
            inputline.extend(["--includelogs"])
        if options.path:
            inputline.extend(["--path", options.path])

    if hasattr(options, 'biospassword') and options.biospassword:
        inputline.extend(["--biospassword", options.biospassword])

    if hasattr(options, 'selector') and options.selector:
        if inputline:
            inputline.extend(["--selector", options.selector])
            logobj.loginfunction(inputline)
            loggedin = True
        else:
            if hasattr(options, 'ref') and options.ref:
                inputline.extend(["--refresh"])

            inputline.extend([options.selector])
            selobj.selectfunction(inputline)
            loggedin = True
    elif hasattr(options, 'selector'):
        try:
            inputline = list()
            selector = command_obj._rdmc.app.selector

            if hasattr(options, 'ref') and options.ref:
                inputline.extend(["--refresh"])

            inputline.extend([selector])
            selobj.selectfunction(inputline)
            loggedin = True
        except NothingSelectedError:
            raise NothingSelectedError
    if not loggedin and not client and not options.url and not command_obj._rdmc.config.url:
        try:
            if command_obj._rdmc.opts.verbose:
                sys.stdout.write("Local login initiated...\n")
            else:
                raise Exception
        except Exception:
            rdmc_helper.LOGGER.info("Local login initiated...\n")
    if not loggedin and not client:
        logobj.loginfunction(inputline, skipbuild=skipbuild)

def logout_routine(command_obj, options):

    """ Routine to logout of a server automatically at the completion of a command.

    :param command_obj: the command object instance
    :type command_obj: list.
    :param options: command line options
    :type options: list.
    """

    logoutobj = command_obj._rdmc.commands_dict["LogoutCommand"](command_obj._rdmc)

    if options.logout:
        logoutobj.run("")

class CommandBase(object):
    """Abstract base class for all Command objects.

    This class is used to build complex command line programs
    """
    def __init__(self, name, usage, summary, aliases=None, argparser=None, **kwargs):
        self.name = name
        self.summary = summary
        self.aliases = aliases
        self.config_required = True # does the command access config data

        if argparser is None:
            self.parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,\
                                         prog=versioning.__shortname__ + " " + name, **kwargs)
        else:
            self.parser = argparser

        self.parser.usage = usage
        #TODO: See if we can remove this or stop it from opening a subprocess all the time
        #self._cli = cliutils.CLI()

    def run(self, line):
        """Called to actually perform the work.

        Override this method in your derived class.  This is where your program
        actually does work.
        """
        pass

    def ismatch(self, cmdname):
        """Compare cmdname against possible aliases.

        Commands can have aliases for syntactic sugar.  This method searches
        aliases for a match.

        :param cmdname: name or alias to search for
        :type cmdname: str.
        :returns: boolean -- True if it matches, otherwise False
        """
        if not cmdname:
            return False

        cmdname_lower = cmdname.lower()
        if self.name.lower() == cmdname_lower:
            return True

        if self.aliases:
            for alias in self.aliases:
                if alias.lower() == cmdname_lower:
                    return True

        return False

    def print_help(self):
        """Automated help printer.
        """
        self.parser.print_help()

    def print_summary(self):
        """Automated summary printer.
        """
        maxsum = 45
        smry = self.summary

        if not smry:
            smry = ''

        sumwords = smry.split(' ')
        lines = []
        line = []
        linelength = 0

        for sword in sumwords:
            if linelength + len(sword) > maxsum:
                lines.append(' '.join(line))
                line = []
                linelength = 0

            line.append(sword)
            linelength += len(sword) + 1

        lines.append(' '.join(line))

        sep = '\n' + (' ' * 34)
        print("  %-28s - %s" % (self.name, sep.join(lines)))

    def _parse_arglist(self, line=None, default=False):
        """
        parses line into arguments taking special consideration
        of quote characters
        :param line: string of arguments passed in
        :type line: str.
        :param default: Flag to determine if the parsed command requires the default workaround for
                        argparse in Python 2. Argparse incorrectly assumes a sub-command is always
                        required, so we have to include a default sub-command for no arguments.
        :type default: bool
        :returns: args list
        """

        def checkargs(argopts):
            """Check for optional args"""
            (_, args) = argopts
            for arg in args:
                if arg.startswith('-') or arg.startswith('--'):
                    try:
                        self.parser.error("The option %s is not available for %s" % \
                                                                    (arg, self.name))
                    except SystemExit:
                        raise rdmc_helper.InvalidCommandLineErrorOPTS("")
            return argopts

        if line is None:
            return checkargs(self.parser.parse_known_args(line))

        arglist = []
        if isinstance(line, six.string_types):
            arglist = shlex.split(line, posix=False)

            for ind, val in enumerate(arglist):
                arglist[ind] = val.strip('"\'')
        elif isinstance(line, list):
            arglist = line

        exarglist = []
        if os.name == 'nt':
            # need to glob for windows
            for arg in arglist:
                try:
                    gob = glob.glob(arg)

                    if gob and len(gob) > 0:
                        exarglist.extend(gob)
                    else:
                        exarglist.append(arg)
                except:
                    if not arg:
                        continue
                    else:
                        exarglist.append(arg)
        else:
            for arg in arglist:
                if arg:
                    exarglist.append(arg)
        # insert the 'default' positional argument when the first argument is an optional
        #chicken and egg problem. Would be nice to figure out if a help option has been
        #referenced; however, I may not be able to parse the exarglist (line in array form)
        #in the event it is empty (appears there is no way to test parse and subsequently catch
        #the error for flow control)
        if len(exarglist) > 1:
            if default and (exarglist[0].startswith('-') or exarglist[1].startswith('-')):
                #find help otherwise we assume if 0th or 1st positions contain an optional argument
                #the user is targetting a default command
                found_help = False
                for _opt in exarglist:
                    if _opt in ['-h', '--h', '-help', '--help']:
                        found_help=True
                        break
                if not found_help:
                    exarglist.insert(0, 'default')
        elif default: #and not exarglist:
            #empty command so I assume the target subcommand is 'default'
            exarglist.insert(0, 'default')#append('default')
        return checkargs(self.parser.parse_known_args(exarglist))

class RdmcCommandBase(CommandBase):
    """Base class for rdmc commands which includes some common helper
       methods.
    """

    def __init__(self, name, usage, summary, aliases, argparser=None, **kwargs):
        """ Constructor """
        CommandBase.__init__(self,\
            name=name,\
            usage=usage,\
            summary=summary,\
            aliases=aliases,\
            argparser=argparser,\
            **kwargs)
        self.json = False
        self.cache = False
        self.nologo = False

    def is_enabled(self):
        """ If reachable return true for command """
        return True

    def enablement_hint(self):
        """
        Override to define a error message displayed to the user
        when command is not enabled.
        """
        return ""

class RdmcOptionParser(ArgumentParser):
    """ Constructor """
    def __init__(self):
        super(RdmcOptionParser, self).__init__(usage="%s [GLOBAL OPTIONS] [COMMAND] " \
                                "[COMMAND ARGUMENTS] [COMMAND OPTIONS]" % versioning.__shortname__,
                                description="iLOrest is a command-line interface that allows you "\
                                "to manage Hewlett Packard Enterprise products that take advantage"\
                                " of RESTful APIs.\n\nIn order to view or manage a system you must"\
                                " first login. You can login using the login command or during "\
                                "execution of any other command.\nFrom here you can run any other "\
                                "commands. To learn more about specific commands, run iLOrest "\
                                "COMMAND -h.\nA list of commands with descriptions is available at"\
                                " the end of this help.",
                                epilog="Examples:\n\nThe following is the standard flow of command"\
                                "s to view system data.\n\tThe first example is each command "\
                                "run individually: \n\n\tilorest login\n\tilorest select Bios.\n\t"\
                                "ilorest get\n\n\tThe second is the list of all of the commands "\
                                "run at once. First locally, then remotely.\n\tilorest get "\
                                "--select Bios.\n\tilorest get --select Bios. --url <iLO IP> -u"\
                                " <iLO Username> -p <iLO Password>",\
                                formatter_class=RawDescriptionHelpFormatter)
        globalgroup = _ArgumentGroup(self, "GLOBAL OPTIONS")

        self.add_argument('-c',
                          '--config',
                          dest='config',
                          help="Use the provided configuration file instead of the default one.",
                          metavar='FILE')

        config_dir_default = os.path.join(cliutils.get_user_config_dir(),\
                                            '.%s' % versioning.__shortname__)
        self.add_argument(
            '--cache-dir',
            dest='config_dir',
            default=config_dir_default,
            help="Use the provided directory as the location to cache data"\
            " (default location: %s)" % config_dir_default,
            metavar='PATH')
        self.add_argument(
            '-v',
            '--verbose',
            dest='verbose',
            action="count",
            help="""Display verbose information (with increasing level).\n\t\'-v\': Level 1""" \
                 """\n\t\'-vv\': Level 2""")
        self.add_argument(
            '-d',
            '--debug',
            dest='debug',
            action="store_true",
            help="""Display debug information.""",
            default=False)
        self.add_argument(
            '--logdir',
            dest='logdir',
            default=None,
            help="""Use the provided directory as the location for log file.""",
            metavar='PATH')
        self.add_argument(
            '--nocache',
            dest='nocache',
            action="store_true",
            help="During execution the application will temporarily store data only in memory.",
            default=False)
        self.add_argument(
            '--nologo',
            dest='nologo',
            action="store_true",
            help="""Include to block copyright and logo.""",
            default=False)
        self.add_argument(
            '--redfish',
            dest='is_redfish',
            action='store_true',
            help="Use this flag if you wish to to enable "\
                "Redfish only compliance. It is enabled by default "\
                "in systems with iLO5 and above.",
            default=False)
        self.add_argument(
            '--latestschema',
            dest='latestschema',
            action='store_true',
            help="Optionally use the latest schema instead of the one "\
            "requested by the file. Note: May cause errors in some data "\
            "retrieval due to difference in schema versions.",
            default=False)
        self.add_argument(
            '--proxy',
            dest='proxy',
            default=None,
            help="""Use the provided proxy for communication.""",
            metavar='URL')
        self.add_argument(
            '--quiet',
            '--silent',
            dest='silent',
            help="Optionally include this flag to redirect console print statements.",
            #action=_SilentAction,
            #type=str,
            nargs='?',
            default=None,
            const=True,
            metavar='Silent'
        )
        self.add_argument_group(globalgroup)
