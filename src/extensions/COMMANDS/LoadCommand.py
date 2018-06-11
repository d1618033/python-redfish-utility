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
""" Load Command for RDMC """

import os
import sys
import json
import shlex
import subprocess

from Queue import Queue
from datetime import datetime
from optparse import OptionParser

import redfish.ris

from redfish.ris.rmc_helper import LoadSkipSettingError
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
                    InvalidCommandLineErrorOPTS, InvalidFileFormattingError, \
                    NoChangesFoundOrMadeError, InvalidFileInputError, \
                    NoDifferencesFoundError, MultipleServerConfigError, \
                    InvalidMSCfileInputError, Encryption

from rdmc_base_classes import RdmcCommandBase, HARDCODEDLIST

#default file name
__filename__ = 'ilorest.json'

class LoadCommand(RdmcCommandBase):
    """ Constructor """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='load',\
            usage='load [OPTIONS]\n\n\tRun to load the default configuration' \
            ' file\n\texample: load\n\n\tLoad configuration file from a ' \
            'different file\n\tif any property values have changed, the ' \
            'changes are committed and the user is logged out of the server'\
            '\n\n\texample: load -f output.json\n\n\tLoad configurations to ' \
            'multiple servers\n\texample: load -m mpfilename.txt -f output.' \
            'json\n\n\tNote: multiple server file format (1 server per new ' \
            'line)\n\t--url <iLO url/hostname> -u admin -p password\n\t--url' \
            ' <iLO url/hostname> -u admin -p password\n\t--url <iLO url/' \
            'hostname> -u admin -p password',\
            summary='Loads the server configuration settings from a file.',\
            aliases=[],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self.filenames = None
        self.mpfilename = None
        self.queue = Queue()
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)
        self.setobj = rdmcObj.commands_dict["SetCommand"](rdmcObj)
        self.comobj = rdmcObj.commands_dict["CommitCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """ Main load worker function

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

        self.loadvalidation(options)
        returnvalue = False

        loadcontent = dict()

        if options.mpfilename:
            sys.stdout.write("Loading configuration for multiple servers...\n")
        else:
            sys.stdout.write("Loading configuration...\n")

        for files in self.filenames:
            if not os.path.isfile(files):
                raise InvalidFileInputError("File '%s' doesn't exist. Please " \
                                "create file by running save command." % files)
            if options.encryption:
                with open(files, "rb") as myfile:
                    data = myfile.read()
                    data = Encryption().decrypt_file(data, \
                                                        options.encryption)
            else:
                with open(files, "r") as myfile:
                    data = myfile.read()

            try:
                loadcontents = json.loads(data)
            except:
                raise InvalidFileFormattingError("Invalid file formatting " \
                                                    "found in file %s" % files)

            if options.mpfilename:
                mfile = options.mpfilename
                outputdir = None

                if options.outdirectory:
                    outputdir = options.outdirectory

                if self.runmpfunc(mpfile=mfile, lfile=files, \
                                                        outputdir=outputdir):
                    return ReturnCodes.SUCCESS
                else:
                    raise MultipleServerConfigError("One or more servers "\
                                        "failed to load given configuration.")

            results = False

            for loadcontent in loadcontents:


                for content, loaddict in loadcontent.iteritems():
                    inputlist = list()

                    if content == "Comments":
                        continue

                    inputlist.append(content)
                    if options.biospassword:
                        inputlist.extend(["--biospassword", \
                                                        options.biospassword])

                    self.selobj.selectfunction(inputlist)
                    selector = self._rdmc.app.get_selector()
                    if self._rdmc.app.get_selector().lower() not in \
                                                                content.lower():
                        raise InvalidCommandLineError("Selector not found.\n")

                    try:
                        for _, items in loaddict.iteritems():
                            try:
                                if self._rdmc.app.loadset(selector=selector,\
                                      seldict=items, \
                                      latestschema=options.latestschema, \
                                      uniqueoverride=options.uniqueoverride):
                                    results = True
                            except LoadSkipSettingError, excp:
                                returnvalue = True
                                results = True
                            except Exception, excp:
                                raise excp
                    except redfish.ris.ValidationError, excp:
                        errs = excp.get_errors()

                        for err in errs:
                            if isinstance(err, \
                                          redfish.ris.RegistryValidationError):
                                sys.stderr.write(err.message)
                                sys.stderr.write(u'\n')

                                try:
                                    if err.reg:
                                        err.reg.print_help(str(err.sel))
                                        sys.stderr.write(u'\n')
                                except:
                                    pass
                        raise redfish.ris.ValidationError(excp)
                    except Exception, excp:
                        raise excp

                try:
                    if results:
                        self.comobj.commitfunction(options=options)
                except NoChangesFoundOrMadeError, excp:
                    if returnvalue:
                        pass
                    else:
                        raise excp

            if not results:
                raise NoDifferencesFoundError("No differences found from " \
                                                    "current configuration.")

        #Return code
        if returnvalue:
            return ReturnCodes.LOAD_SKIP_SETTING_ERROR

        return ReturnCodes.SUCCESS

    def loadvalidation(self, options):
        """ Load method validation function

        :param options: command line options
        :type options: list.
        """
        inputline = list()
        runlogin = False

        if self._rdmc.opts.latestschema:
            options.latestschema = True

        if self._rdmc.app.config._ac__format.lower() == 'json':
            options.json = True

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

        if inputline:
            runlogin = True
            if not inputline:
                sys.stdout.write(u'Local login initiated...\n')
        if options.biospassword:
            inputline.extend(["--biospassword", options.biospassword])

        try:
            if runlogin:
                self.lobobj.loginfunction(inputline)
        except Exception, excp:
            if options.mpfilename:
                pass
            else:
                raise excp

        #filename validations and checks
        if options.filename:
            self.filenames = options.filename
        elif self._rdmc.app.config:
            if self._rdmc.app.config._ac__loadfile:
                self.filenames = [self._rdmc.app.config._ac__loadfile]

        if not self.filenames:
            self.filenames = [__filename__]

    def verify_file(self, filedata, inputfile):
        """ Function used to handle oddly named files and convert to JSON

        :param filedata: input file data
        :type filedata: string.
        :param inputfile: current input file
        :type inputfile: string.
        """
        try:
            tempholder = json.loads(filedata)
            return tempholder
        except:
            raise InvalidFileFormattingError("Invalid file formatting found" \
                                                    " in file %s" % inputfile)

    def get_current_selector(self, path=None):
        """ Returns current selected content minus hard coded list

        :param path: current path
        :type path: string.
        """
        contents = self._rdmc.app.get_save(onlypath=path)

        if not contents:
            contents = list()

        for content in contents:
            for k in content.keys():
                if k.lower() in HARDCODEDLIST or '@odata' in k.lower():
                    del content[k]

        return contents

    def runmpfunc(self, mpfile=None, lfile=None, outputdir=None):
        """ Main worker function for multi file command

        :param mpfile: configuration file
        :type mpfile: string.
        :param lfile: custom file name
        :type lfile: string.
        :param outputdir: custom output directory
        :type outputdir: string.
        """
        self.logoutobj.run("")
        data = self.validatempfile(mpfile=mpfile, lfile=lfile)

        if not data:
            return False

        processes = []
        finalreturncode = True
        outputform = '%Y-%m-%d-%H-%M-%S'

        if outputdir:
            if outputdir.endswith(('"', "'")) and \
                                            outputdir.startswith(('"', "'")):
                outputdir = outputdir[1:-1]

            if not os.path.isdir(outputdir):
                sys.stdout.write("The give output folder path does not " \
                                                                    "exist.\n")
                raise InvalidCommandLineErrorOPTS("")

            dirpath = outputdir
        else:
            dirpath = os.getcwd()

        dirname = '%s_%s' % (datetime.now().strftime(outputform), 'MSClogs')
        createdir = os.path.join(dirpath, dirname)
        os.mkdir(createdir)

        oofile = open(os.path.join(createdir, 'CompleteOutputfile.txt'), 'w+')
        sys.stdout.write('Create multiple processes to load configuration '\
                                            'concurrently to all servers...\n')

        while True:
            if not self.queue.empty():
                line = self.queue.get()
            else:
                break

            finput = '\n'+ 'Output for '+ line[line.index('--url')+1]+': \n\n'
            urlvar = line[line.index('--url')+1]
            listargforsubprocess = [sys.executable] + line

            if os.name is not 'nt':
                listargforsubprocess = " ".join(listargforsubprocess)

            urlfilename = urlvar.split('//')[-1]
            logfile = open(os.path.join(createdir, urlfilename+".txt"), "w+")
            pinput = subprocess.Popen(listargforsubprocess, shell=True,\
                                                stdout=logfile, stderr=logfile)

            processes.append((pinput, finput, urlvar, logfile))

        for pinput, finput, urlvar, logfile in processes:
            pinput.wait()
            returncode = pinput.returncode
            finalreturncode = finalreturncode and not returncode

            logfile.close()
            logfile = open(os.path.join(createdir, urlvar+".txt"), "r+")
            oofile.write(finput + str(logfile.read()))
            oofile.write('-x+x-'*16)
            logfile.close()

            if returncode == 0:
                sys.stdout.write('Loading Configuration for {} : SUCCESS\n'\
                                                                .format(urlvar))
            else:
                sys.stdout.write('Loading Configuration for {} : FAILED\n'\
                                                                .format(urlvar))
                sys.stderr.write('ILOREST return code : {}.\nFor more '\
                         'details please check {}.txt under {} directory.\n'\
                                        .format(returncode, urlvar, createdir))

        oofile.close()

        if finalreturncode:
            sys.stdout.write('All servers have been successfully configured.\n')

        return finalreturncode

    def validatempfile(self, mpfile=None, lfile=None):
        """ Validate temporary file

        :param mpfile: configuration file
        :type mpfile: string.
        :param lfile: custom file name
        :type lfile: string.
        """
        sys.stdout.write('Checking given server information...\n')

        if not mpfile:
            return False

        if not os.path.isfile(mpfile):
            raise InvalidFileInputError("File '%s' doesn't exist, please " \
                            "create file by running save command." % mpfile)

        try:
            with open(mpfile, "r") as myfile:
                data = list()
                cmdtorun = ['load']
                cmdargs = ['-f', str(lfile)]
                globalargs = ['-v', '--nocache']

                while True:
                    line = myfile.readline()

                    if not line:
                        break

                    if line.endswith(os.linesep):
                        line.rstrip(os.linesep)

                    args = shlex.split(line, posix=False)

                    if len(args) < 5:
                        sys.stderr.write('Incomplete data in input file: {}\n'\
                                                                .format(line))
                        raise InvalidMSCfileInputError('Please verify the '\
                                            'contents of the %s file' %mpfile)
                    else:
                        linelist = globalargs + cmdtorun + args + cmdargs
                        line = str(line).replace("\n", "")
                        self.queue.put(linelist)
                        data.append(linelist)
        except Exception, excp:
            raise excp

        if data:
            return data

        return False

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
            '-m',
            '--multiprocessing',
            dest='mpfilename',
            help="""use the provided filename to obtain data""",
            default=None,
        )
        customparser.add_option(
            '-o',
            '--outputdirectory',
            dest='outdirectory',
            help="""use the provided directory to output data for multiple server configuration""",
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
        customparser.add_option(
            '-e',
            '--encryption',
            dest='encryption',
            help="Optionally include this flag to encrypt/decrypt a file "\
            "using the key provided.",
            default=None
        )
        customparser.add_option(
            '--reboot',
            dest='reboot',
            help="Use this flag to perform a reboot command function after"\
            " completion of operations.  For help with parameters and"\
            " descriptions regarding the reboot flag, run help reboot.",
            default=None,
        )
