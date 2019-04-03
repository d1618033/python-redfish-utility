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
""" Factory Defaults Command for rdmc """
import os
import sys

from optparse import OptionParser, SUPPRESS_HELP

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, InvalidCommandLineErrorOPTS, \
                    NoContentsFoundForOperationError, InvalidFileInputError, Encryption, UploadError

class IloBackupRestoreCommand(RdmcCommandBase):
    """ Backup and restore server using iLO's .bak file """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='backuprestore',\
            usage='backuprestore [OPTIONS]\n\n\t'\
                'Create a .bak file. \n\texample: backuprestore backup\n\n\t' \
                'Restore a server using a .bak file. \n\texample: backuprestore '\
                'restore\n\n\tNOTE: This command is designed to only restore\n\tthe '\
                'machine from which the backup file was created against.\n\tIf you would like to '\
                'take one configuration and apply it\n\tto multiple systems see the '\
                'serverclone command.\n\tThis command is only available in remote mode.',\
            summary='Backup and restore iLO to a server using a .bak file.',\
            aliases=['br'],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """ Main factorydefaults function

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

        if not len(args) == 1:
            raise InvalidCommandLineError("backuprestore command takes one argument.")

        self.ilobackuprestorevalidation(options)

        if self._rdmc.app.current_client.get_base_url() == "blobstore://.":
            raise InvalidCommandLineError("This command is only available remotely.")


        sessionkey = self._rdmc.app.get_current_client()._rest_client.get_session_key()
        sessionkey = (sessionkey).encode('ascii', 'ignore')

        if args[0].lower() == 'backup':
            self.backupserver(options, sessionkey)
        elif args[0].lower() == 'restore':
            self.restoreserver(options, sessionkey)
        else:
            raise InvalidCommandLineError("%s is not a valid option for this "\
                                          "command."% str(args[0]))

        return ReturnCodes.SUCCESS

    def backupserver(self, options, skey):
        """Create .bak file for a server

        :param options: command options
        :type options: list.
        :param skey: sessionkey of the currently logged in server
        :type skey: str.
        """
        select = "HpeiLOBackupRestoreService."
        backupfile = None
        results = self._rdmc.app.select(selector=select)

        try:
            results = results[0]
        except:
            pass

        if results:
            service = results.resp.dict
        else:
            raise NoContentsFoundForOperationError("%s not found.It may not " \
                                       "be available on this system." % select)

        backuplocation = service['BackupFileLocation']
        backupname = backuplocation.split('/')[-1]

        postdata = []
        postdata.append(('sessionKey', skey))

        if options.fpass:
            postdata.append(('password', options.fpass))
        sys.stdout.write("Downloading backup file %s..." % backupname)
        backupfile = self._rdmc.app.post_handler(backuplocation, postdata,\
          service=True, silent=True, response=True)

        if backupfile:
            sys.stdout.write("Download complete.\n")
            outfile = open(backupname, 'wb')
            outfile.write(backupfile.ori)
            outfile.close()
        else:
            raise NoContentsFoundForOperationError("Unable to download file.\n")

    def restoreserver(self, options, skey):
        """Use a .bak file to restore a server

        :param options: command options
        :type options: list.
        :param skey: sessionkey of the currently logged in server
        :type skey: str.
        """

        select = "HpeiLOBackupRestoreService."

        if options.filename:
            filename = options.filename[0]
        else:
            files = []
            files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.bak')]
            if files and len(files) > 1:
                raise InvalidFileInputError("More than one .bak file found in "\
                                            "the current directory. Please specify "\
                                            "a file using the -f option.")
            elif not files:
                raise InvalidFileInputError("No .bak file found in current "\
                                            "directory. Please specify a file using the -f option.")
            else:
                filename = files[0]

        results = self._rdmc.app.select(selector=select)

        try:
            results = results[0]
        except:
            pass

        if results:
            service = results.resp.dict
        else:
            raise NoContentsFoundForOperationError("%s not found.It may not " \
                                       "be available on this system." % select)
        restorelocation = service['HttpPushUri']
        postdata = []

        with open(filename, 'rb') as fle:
            bakfile = fle.read()
        postdata.append(('sessionKey', skey))
        if options.fpass:
            postdata.append(('password', options.fpass))
        postdata.append(('file', (filename, bakfile, 'application/octet-stream')))

        resp = self._rdmc.app.post_handler(restorelocation, postdata, service=False, silent=True, \
                                    headers={'Cookie': 'sessionKey=' + skey}, response=True)

        if not resp.status == 200:
            if resp.ori == 'invalid_restore_password':
                raise UploadError("Invalid or no password supplied during restore. Please "\
                                  "supply the password used during creation of the backup file.")
            else:
                raise UploadError("Error while uploading the backup file.")
        else:
            sys.stdout.write("Restore in progress. iLO while be unresponsive while the "\
                                        "restore completes.\nYour session will be terminated.\n")
            self.logoutobj.run("")

    def ilobackuprestorevalidation(self, options):
        """ factory defaults validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        inputline = list()

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

        if inputline:
            self.lobobj.loginfunction(inputline)
        elif not client:
            raise InvalidCommandLineError("Please login or pass credentials to complete the "\
                                                                                    "operation.")

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
            '-f',
            '--filename',
            dest='filename',
            help="Use this flag to specify which backup file to restore. By "\
            "default the commmand will try to find a .bak file in the current "\
            "working directory.",
            action="append",
            default=None,
        )
        customparser.add_option(
            '--filepass',
            dest='fpass',
            help="Optionally use the provided password when creating the "\
                "backup file. The same password must be used for restoring.",
            default=None,
        )
        customparser.add_option(
            '-e',
            '--enc',
            dest='encode',
            action='store_true',
            help=SUPPRESS_HELP,
            default=False,
        )
