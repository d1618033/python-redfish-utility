# ##
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
# ##

# -*- coding: utf-8 -*-
""" Download Component Command for rdmc """

import os
import sys
import time
import ctypes

from ctypes import c_char_p, c_int
from optparse import OptionParser, SUPPRESS_HELP

import redfish.hpilo.risblobstore2 as risblobstore2

from rdmc_base_classes import RdmcCommandBase
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
                '/fwrepo/filename.exe --outdir <output location>', \
            summary='Downloads components/binaries from the iLO Repository.', \
            aliases=['Downloadcomp'], \
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """ Wrapper function for download command main function

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

        if options.encode and options.user and options.password:
            options.user = Encryption.decode_credentials(options.user)
            options.password = Encryption.decode_credentials(options.password)

        if options.sessionid:
            url = self.sessionvalidation(options)
        else:
            url = None
            self.downloadcomponentvalidation(options)

        if options.sessionid and not url:
            raise InvalidCommandLineError('Url muse be included with ' \
                          'sessionid. Session is not required for local mode.')

        if not options.sessionid and self.typepath.defs.isgen9:
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

        if not url and 'blobstore' in self._rdmc.app.get_current_client()\
                                                ._rest_client.get_base_url():
            ret = self.downloadlocally(args[0], options)
        else:
            ret = self.downloadfunction(args[0], options, url)

        sys.stdout.write("%s\n" % human_readable_time(time.time() - start_time))

        if options.logout:
            self.logoutobj.run("")

        return ret

    def downloadfunction(self, filepath, options=None, url=None):
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

        results = self._rdmc.app.get_handler(filepath, url=url, \
                             uncache=True, sessionid=options.sessionid)

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
            bs2 = risblobstore2.BlobStore2()
            risblobstore2.BlobStore2.initializecreds(options.user, options.password)
            bs2.channel.dll.downloadComponent.argtypes = [c_char_p, c_char_p]
            bs2.channel.dll.downloadComponent.restype = c_int

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

            ret = bs2.channel.dll.downloadComponent(ctypes.create_string_buffer(\
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
        inputline = list()
        client = None

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

    def sessionvalidation(self, options):
        """ session validation function

        :param options: command line options
        :type options: list.
        """

        url = None
        if options.user or options.password or options.url:
            if options.url:
                url = options.url
        else:
            if self._rdmc.app.config.get_url():
                url = self._rdmc.app.config.get_url()

        if url and not "https://" in url:
            url = "https://" + url

        return url

    def definearguments(self, customparser):
        """ Wrapper function for download command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        customparser.add_option(
            '--url',
            dest='url',
            help='Use the provided iLO URL to login.',
            default="",
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
            '--sessionid',
            dest='sessionid',
            help="Optionally include this flag if you would prefer to "\
            "connect using a session id instead of a normal login.",
            default=None
        )
        customparser.add_option(
            '--includelogs',
            dest='includelogs',
            action="store_true",
            help="Optionally include logs in the data retrieval process.",
            default=False,
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
            '--outdir',
            dest='outdir',
            help="""output directory for saving the file.""",
            default="",
        )
        customparser.add_option(
            '-e',
            '--enc',
            dest='encode',
            action='store_true',
            help=SUPPRESS_HELP,
            default=False,
        )
