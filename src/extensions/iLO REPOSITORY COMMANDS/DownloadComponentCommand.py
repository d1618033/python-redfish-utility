# ##
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
# ##

# -*- coding: utf-8 -*-
""" Download Component Command for rdmc """

import os
import sys
import time
import ctypes

from ctypes import c_char_p, c_int
from argparse import ArgumentParser

import redfish.hpilo.risblobstore2 as risblobstore2

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group, login_select_validation, \
                                logout_routine
from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, \
                        InvalidCommandLineError, DownloadError, \
                        InvalidFileInputError, IncompatibleiLOVersionError, Encryption

def human_readable_time(seconds):
    """ Returns human readable time

    :param seconds: Amount of seconds to parse.
    :type seconds: string.
    """
    seconds = int(seconds)
    hours = seconds / 3600
    seconds = seconds % 3600
    minutes = seconds / 60
    seconds = seconds % 60

    return str(hours) + " hour(s) " + str(minutes) + " minute(s) " + str(seconds) + " second(s) "

class DownloadComponentCommand(RdmcCommandBase):
    """ Main download component command class """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self, \
            name='downloadcomp', \
            usage='downloadcomp [COMPONENT URI] [OPTIONS]\n\n\tRun to ' \
                'download the file from path\n\texample: downloadcomp ' \
                '/fwrepo/filename.exe --outdir <output location>' \
                'download the file by name\n\texample: downloadcomp ' \
                'filename.exe --outdir <output location>', \
            summary='Downloads components/binaries from the iLO Repository.', \
            aliases=['Downloadcomp'], \
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        #self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """ Wrapper function for download command main function

        :param line: command line input
        :type line: string.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        repo = ['fwrepo']
        urilist = args[0].split('/')
        if repo[0] not in urilist:
            repo = ['/fwrepo/']
            repo[0] += args[0]
            args[0] = repo[0]

        self.downloadcomponentvalidation(options)

        if self.typepath.defs.isgen9:
            raise IncompatibleiLOVersionError('iLO Repository commands are ' \
                                                    'only available on iLO 5.')

        if len(args) > 1:
            raise InvalidCommandLineError("Download component only takes 1 " \
                                                "component path argument.\n")
        elif not args:
            raise InvalidCommandLineError("Download component missing component path.\n")

        start_time = time.time()
        ret = ReturnCodes.FAILED_TO_DOWNLOAD_COMPONENT

        sys.stdout.write("Downloading component, this may take a while...\n")

        if 'blobstore' in self._rdmc.app.current_client.base_url:
            ret = self.downloadlocally(args[0], options)
        else:
            ret = self.downloadfunction(args[0], options)

        sys.stdout.write("%s\n" % human_readable_time(time.time() - start_time))

        logout_routine(self, options)
        #Return code
        return ret

    def downloadfunction(self, filepath, options=None):
        """ Main download command worker function

        :param filepath: Path of the file to download.
        :type filepath: string.
        :param options: command options
        :type options: options.
        """
        filename = filepath.rsplit('/', 1)[-1]

        if not options.outdir:
            destination = os.path.join(os.getcwd(), filename)
        else:
            destination = os.path.join(options.outdir, filename)

        if not os.path.exists(os.path.join(os.path.split(destination)[0])):
            raise InvalidFileInputError("Invalid output file location.")
        if not os.access(os.path.join(os.path.split(destination)[0]), os.W_OK):
            raise InvalidFileInputError("File location is not writable.")
        if os.access(destination, os.F_OK) and not os.access(destination, os.W_OK):
            raise InvalidFileInputError("Existing File cannot be overwritten.")

        if filepath[0] != '/':
            filepath = '/' + filepath

        results = self._rdmc.app.get_handler(filepath, uncache=True)

        with open(destination, "wb") as local_file:
            local_file.write(results.ori)

        sys.stdout.write("Download complete\n")

        return ReturnCodes.SUCCESS

    def downloadlocally(self, filepath, options=None):
        """ Used to download a component from the iLO Repo locally

        :param filepath: Path to the file to download.
        :type filepath: string.
        """
        try:
            dll = self._rdmc.app.current_client.connection._conn.channel.dll
            dll.downloadComponent.argtypes = [c_char_p, c_char_p]
            dll.downloadComponent.restype = c_int

            filename = filepath.rsplit('/', 1)[-1]
            if not options.outdir:
                destination = os.path.join(os.getcwd(), filename)
            else:
                destination = os.path.join(options.outdir, filename)

            if not os.path.exists(os.path.join(os.path.split(destination)[0])):
                raise InvalidFileInputError("Invalid output file location.")
            if not os.access(os.path.join(os.path.split(destination)[0]), os.W_OK):
                raise InvalidFileInputError("File location is not writable.")
            if os.access(destination, os.F_OK) and not os.access(destination, \
                                                                 os.W_OK):
                raise InvalidFileInputError("Existing File cannot be overwritten.")

            ret = dll.downloadComponent(ctypes.create_string_buffer(\
                                filename.encode('utf-8')), ctypes.create_string_buffer(\
                                                            destination.encode('utf-8')))

            if ret != 0:
                sys.stdout.write("Component " + filename + " download failed\n")
                return ReturnCodes.FAILED_TO_DOWNLOAD_COMPONENT
            else:
                sys.stdout.write("Component " + filename + " downloaded successfully\n")

        except Exception as excep:
            raise DownloadError(str(excep))

        return ReturnCodes.SUCCESS

    def downloadcomponentvalidation(self, options):
        """ Download command method validation function

        :param options: command options
        :type options: options.
        """
        login_select_validation(self, options)

    def definearguments(self, customparser):
        """ Wrapper function for download command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        add_login_arguments_group(customparser)
        '''
        customparser.add_argument(
            '--logout',
            dest='logout',
            action="store_true",
            help="Optionally include the logout flag to log out of the"\
            " server after this command is completed. Using this flag when"\
            " not logged in will have no effect.",
            default=None,
        )
        '''
        customparser.add_argument(
            '--outdir',
            dest='outdir',
            help="""Output directory for saving the file.""",
            default="",
        )
