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
""" Delete Component Command for rdmc """

import sys

from optparse import OptionParser, SUPPRESS_HELP

from rdmc_base_classes import RdmcCommandBase

from rdmc_helper import IncompatibleiLOVersionError, ReturnCodes, Encryption, \
                        InvalidCommandLineErrorOPTS, InvalidCommandLineError

class DeleteComponentCommand(RdmcCommandBase):
    """ Main download command class """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self, \
            name='deletecomp', \
            usage='deletecomp [COMPONENT URI/ID] [OPTIONS] \n\n\tRun to ' \
              'delete component(s) of the currently logged in system.\n\n\t'\
              'Delete a single component by name.\n\texample: deletecomp ' \
              'CP327.zip\n\n\tDelete multiple components by ' \
              'id.\n\texample: deletecomp 377fg6c4 327cf4c7\n\n\tDelete '
              'multiple components by filename.\n\texample: deletecomp '
              'CP327.exe CP99.exe',\
            summary='Deletes components/binaries from the iLO Repository.', \
            aliases=['Deletecomp'], \
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """ Main deletecomp worker function

        :param line: string of arguments passed in
        :type line: str.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.deletecomponentvalidation(options)

        if self.typepath.defs.isgen9:
            raise IncompatibleiLOVersionError('iLO Repository commands are ' \
                                              'only available on iLO 5.')

        comps = self._rdmc.app.getcollectionmembers(\
                            '/redfish/v1/UpdateService/ComponentRepository/')

        if not comps:
            sys.stdout.write('No components found to delete\n')

        elif options.deleteall:
            delopts = []

            for comp in comps:
                try:
                    if comp['Locked']:
                        sys.stderr.write("Unable to delete %s. It is in use by "\
                                         "an install set or update task.\n" % comp['Filename'])
                        continue
                except KeyError:
                    pass
                delopts.append(comp['@odata.id'])

            self.deletecomponents(comps, delopts)
        elif args:
            self.deletecomponents(comps, args)
        else:
            InvalidCommandLineError("Please include the component(s) you wish to delete")

        return ReturnCodes.SUCCESS

    def deletecomponents(self, comps, delopts):
        """ component validation function

        :param comps: component list
        :type comps: list.
        :param delopts: delete items list
        :type delopts: list.
        """
        if ',' in delopts:
            delopts = delopts.split(',')
        elif not isinstance(delopts, list):
            delopts = [delopts]

        for opt in delopts:
            deleted = False

            if '/' in opt:
                self._rdmc.app.delete_handler(opt)
                deleted = True
            else:
                for comp in comps:
                    if opt == comp['Id'] or opt == comp['Filename']:
                        try:
                            if comp['Locked']:
                                sys.stdout.write("Unable to delete %s. It is in use by "\
                                         "an install set or update task.\n" % comp['Filename'])
                                continue
                        except KeyError:
                            pass

                        self._rdmc.app.delete_handler(comp['@odata.id'])
                        deleted = True

                if deleted:
                    sys.stdout.write('Deleted %s\n' % opt)
                else:
                    raise InvalidCommandLineError('Cannot find or unable to delete component %s' \
                                                                                            % opt)

    def deletecomponentvalidation(self, options):
        """ component validation function

        :param options: command line options
        :type options: list.
        """
        inputline = list()
        client = None

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

        if not inputline and not client:
            sys.stdout.write('Local login initiated...\n')
        if not client or inputline:
            self.lobobj.loginfunction(inputline)

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
            '-a',
            '--all',
            dest='deleteall',
            action="store_true",
            help="""Delete all components.""",
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
