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
"""This is the helper module for RDMC"""

#---------Imports---------

import os
import glob
import shlex

from argparse import ArgumentParser, _ArgumentGroup, SUPPRESS

import six

import cliutils
import versioning
import rdmc_helper

#---------End of imports---------

#Using hard coded list until better solution is found
HARDCODEDLIST = ["name", "modified", "type", "description",
                 "attributeregistry", "links", "settingsresult",
                 "actions", "availableactions", "id", "extref"]

def add_login_arguments_group(parser, full=False):
    """Adds login arguments to the passed parser

    :param parser: The parser to add the login option group to
    :type parser: ArgumentParser.
    :param full: Flag to include seldom used options
    :type full: bool
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
    if full:
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

class CommandBase(object):
    """Abstract base class for all Command objects.

    This class is used to build complex command line programs
    """
    def __init__(self, name, usage, summary, aliases=None, argparser=None):
        self.name = name
        self.summary = summary
        self.aliases = aliases
        self.config_required = True # does the command access config data

        if argparser is None:
            self.parser = ArgumentParser()
        else:
            self.parser = argparser

        self.parser.usage = usage


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

    def _parse_arglist(self, line=None):
        """
        parses line into arguments taking special consideration
        of quote characters
        :param line: string of arguments passed in
        :type line: str.
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

        return checkargs(self.parser.parse_known_args(exarglist))

class RdmcCommandBase(CommandBase):
    """Base class for rdmc commands which includes some common helper
       methods.
    """

    def __init__(self, name, usage, summary, aliases, argparser=None):
        """ Constructor """
        CommandBase.__init__(self,\
            name=name,\
            usage=usage,\
            summary=summary,\
            aliases=aliases,\
            argparser=argparser)
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
        super(RdmcOptionParser, self).__init__("Usage: %s [GLOBAL OPTIONS] [COMMAND] [ARGUMENTS]" \
                                                "[COMMAND OPTIONS]" % versioning.__shortname__)

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
            action="store_true",
            help="""Display verbose information.""",
            default=False)
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
        self.add_argument_group(globalgroup)
