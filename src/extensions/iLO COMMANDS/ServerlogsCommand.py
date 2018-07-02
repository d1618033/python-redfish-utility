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
""" Log Operations Command for rdmc """

import os
import sys
import json
import time
import ctypes
import string
import shlex
import tempfile
import datetime
import platform
import itertools
import subprocess

from Queue import Queue
from optparse import OptionParser

from redfish.rest.v1 import SecurityStateError
import redfish.hpilo.risblobstore2 as risblobstore2

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
                InvalidCommandLineErrorOPTS, InvalidFileInputError, \
                NoContentsFoundForOperationError, IncompatibleiLOVersionError,\
                InvalidCListFileError, PartitionMoutingError, \
                MultipleServerConfigError, UnabletoFindDriveError, \
                InvalidMSCfileInputError

if os.name == 'nt':
    import win32api
elif sys.platform != 'darwin':
    import pyudev

class ServerlogsCommand(RdmcCommandBase):
    """ Download logs from the server that is currently logged in """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='serverlogs',\
            usage='serverlogs [LOG_SELECTION] [OPTIONS]\n\n\tDownload the AHS' \
                ' logs from the logged in server.\n\texample: serverlogs ' \
                '--selectlog=AHS \n\n\tClear the AHS logs ' \
                'from the logged in server.\n\texample: serverlogs ' \
                '--selectlog=AHS --clearlog\n\n\tDownload the IEL' \
                ' logs from the logged in server.\n\texample: serverlogs ' \
                '--selectlog=IEL -f IELlog.txt\n\n\tClear the IEL logs ' \
                'from the logged in server.\n\texample: serverlogs ' \
                '--selectlog=IEL --clearlog\n\n\tDownload the IML' \
                ' logs from the logged in server.\n\texample: serverlogs ' \
                '--selectlog=IML -f IMLlog.txt\n\n\tClear the IML logs ' \
                'from the logged in server.\n\texample: serverlogs ' \
                '--selectlog=IML --clearlog\n\n\t(IML LOGS ONLY FEATURE)' \
                '\n\tInsert entry in the IML logs from the logged in ' \
                'server.\n\texample: serverlogs --selectlog=IML -m "Text' \
                ' message for maintenance"\n\n\tDownload logs from multiple servers' \
                '\n\texample: serverlogs --mpfile mpfilename.txt -o output' \
                'directorypath --mplog=IEL,IML\n\n\tNote: multiple server file ' \
                'format (1 server per new line)\n\t--url <iLO url/hostname> ' \
                '-u admin -p password\n\t--url <iLO url/hostname> -u admin -' \
                'p password\n\t--url <iLO url/hostname> -u admin -p password'\
                '\n\n\tInsert customized string '\
                'if required for AHS\n\texample: serverlogs --selectlog=' \
                'AHS --customiseAHS "from=2014-03-01&&to=2014' \
                '-03-30"\n\n\t(AHS LOGS ONLY FEATURE)\n\tInsert the location/' \
                'path of directory where AHS log needs to be saved.'\
                ' \n\texample: serverlogs --selectlog=AHS '\
                '--directorypath=C:\\Python27\\DataFiles',\
            summary='Download and perform log operations.',\
            aliases=['logservices'],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = self._rdmc.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)
        self.dontunmount = None
        self.queue = Queue()
        self.abspath = None
        self.lib = None

    def run(self, line):
        """Main serverlogs function

        :param line: string of arguments passed in
        :type line: str.
        """
        try:
            (options, _) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.serverlogsvalidation(options)

        if options.mpfilename:
            sys.stdout.write("Downloading logs for multiple servers...\n")
            return self.gotompfunc(options)

        self.serverlogsworkerfunction(options)

        if options.logout:
            self.logoutobj.run("")

        return ReturnCodes.SUCCESS

    def serverlogsworkerfunction(self, options):
        """"Main worker function outlining the process

        :param options: command line options
        :type options: list.
        """
        if not options.service:
            raise InvalidCommandLineErrorOPTS("")

        if options.service == 'IML':
            path = self.returnimlpath(options=options)
        elif options.service == 'IEL':
            path = self.returnielpath(options=options)
        elif options.service == 'AHS' and options.filter:
            raise InvalidCommandLineError("Cannot filter AHS logs.")
        elif options.service == 'AHS' and self.typepath.url.\
                startswith(u"blobstore") and not options.clearlog:
            self.downloadahslocally(options=options)
            return
        elif options.service == 'AHS':
            path = self.returnahspath(options)
        else:
            sys.stdout.write('Log opted does not exist!\n')
            raise InvalidCommandLineErrorOPTS("")

        data = None

        if options.clearlog:
            self.clearlog(path)
        elif options.mainmes:
            self.addmaintenancelogentry(options, path=path)
        else:
            data = self.downloaddata(path=path, options=options)

        self.savedata(options=options, data=data)

    def gotompfunc(self, options):
        """"Function to download logs from multiple servers concurrently

        :param options: command line options
        :type options: list.
        """
        if options.mpfilename:
            mfile = options.mpfilename
            outputdir = None

            if options.outdirectory:
                outputdir = options.outdirectory

            if self.runmpfunc(mpfile=mfile, outputdir=outputdir, options\
                                                                =options):
                return ReturnCodes.SUCCESS
            else:
                raise MultipleServerConfigError("One or more servers "\
                                    "failed to download logs.")

    def runmpfunc(self, mpfile=None, outputdir=None, options=None):
        """ Main worker function for multi file command

        :param mpfile: configuration file
        :type mpfile: string.
        :param outputdir: custom output directory
        :type outputdir: string.
        """
        self.logoutobj.run("")
        data = self.validatempfile(mpfile=mpfile, options=options)

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
                sys.stdout.write("The given output folder path does not " \
                                                                    "exist.\n")
                raise InvalidCommandLineErrorOPTS("")

            dirpath = outputdir
        else:
            dirpath = os.getcwd()

        dirname = '%s_%s' % (datetime.datetime.now().strftime(outputform), 'MSClogs')
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
            urlfilename = urlvar.split('//')[-1]
            line[line.index('-f')+1] = str(line[line.index('-f')+1]) + urlfilename
            listargforsubprocess = [sys.executable] + line

            if os.name is not 'nt':
                listargforsubprocess = " ".join(listargforsubprocess)

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

    def validatempfile(self, mpfile=None, options=None):
        """ Validate temporary file

        :param mpfile: configuration file
        :type mpfile: string.
        :param lfile: custom file name
        :type lfile: string.
        """
        sys.stdout.write('Checking given server information...\n')

        if not mpfile:
            return False
        elif mpfile.startswith(('"', "'")) and mpfile[0] == mpfile[-1]:
            mpfile = mpfile[1:-1]

        if not os.path.isfile(mpfile) or not options.mplog:
            raise InvalidFileInputError("File '%s' doesn't exist, please " \
                            "create file by running save command." % mpfile)

        logs = self.checkmplog(options)

        try:
            with open(mpfile, "r") as myfile:
                data = list()
                cmdtorun = ['serverlogs']
                globalargs = ['-v', '--nocache']

                while True:
                    line = myfile.readline()
                    if not line:
                        break

                    for logval in logs:
                        cmdargs = ['--selectlog='+ str(logval), '-f', str(logval)]
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

    def checkmplog(self, options):
        """Function to validate mplogs options

        :param options: command line options
        :type options: list.
        """
        if options.mplog:
            logs = str(options.mplog)
            if ',' in logs:
                logs = logs.split(',')
                return logs
            if logs in ('all', 'IEL', 'IML', 'AHS'):
                if logs == 'all':
                    logs = ['IEL', 'IML', 'AHS']
                else:
                    logs = [logs]
                return logs
        raise InvalidCommandLineErrorOPTS("Error in mplogs options")

    def addmaintenancelogentry(self, options, path=None):
        """Worker function to add maintenance log

        :param options: command line options
        :type options: list.
        :param path: path to post maintainence log
        :type path: str
        """
        if options.mainmes is None:
            raise InvalidCommandLineErrorOPTS("")

        if options.service != 'IML':
            sys.stdout.write('Log opted cannot make maintenance entries!\n')
            raise InvalidCommandLineErrorOPTS("")

        message = options.mainmes

        if message.endswith(('"', "'")) and message.startswith(('"', "'")):
            message = message[1:-1]

        if path:
            bodydict = dict()
            bodydict[u"path"] = path
            bodydict[u"body"] = {u"EntryCode": u"Maintenance", \
                                                            u"Message":message}

            self._rdmc.app.post_handler(path, bodydict[u"body"], \
                                                verbose=self._rdmc.opts.verbose)

    def clearlog(self, path):
        """Worker function to clear logs.

        :param path: path to post clear log action
        :type path: str
        """
        if path and self.typepath.defs.isgen9:
            if path.endswith(u"/Entries"):
                path = path[:-len(u"/Entries")]
            elif path.endswith(u"Entries/"):
                path = path[:-len(u"Entries/")]

            bodydict = dict()
            bodydict[u"path"] = path
            bodydict[u"body"] = {u"Action":u"ClearLog"}
            self._rdmc.app.post_handler(path, bodydict[u"body"], \
                                                verbose=self._rdmc.opts.verbose)
        elif path:
            action = path.split(u'/')[-2]
            bodydict = dict()
            bodydict[u"path"] = path
            bodydict[u"body"] = {u"Action":action}
            self._rdmc.app.post_handler(path, bodydict[u"body"], \
                                                verbose=self._rdmc.opts.verbose)

    def downloaddata(self, path=None, options=None):
        """Worker function to download the log files

        :param options: command line options
        :type options: list.
        :param path: path to download logs
        :type path: str
        """
        if path:
            if options.service == 'AHS':
                data = self._rdmc.app.get_handler(path, silent=True, \
                                                        uncache=True)
                if data:
                    return data.read
                else:
                    raise NoContentsFoundForOperationError\
                                            (u"Unable to retrieve AHS logs.")
            else:
                data = self._rdmc.app.get_handler(path, silent=True)

            datadict = data.dict

            try:
                completedatadictlist = datadict[u'Items'] if u'Items' in\
                                            datadict else datadict[u'Members']
            except:
                sys.stdout.write(u'No data available within log.\n')
                raise NoContentsFoundForOperationError("Unable to retrieve logs.")

            if self.typepath.defs.flagforrest:
                morepages = True

                while morepages:
                    if 'links' in datadict and 'NextPage' in datadict['links']:
                        next_link_uri = path + '?page=' + \
                                    str(datadict['links']['NextPage']['page'])

                        href = u'%s' % next_link_uri
                        data = self._rdmc.app.get_handler(href, silent=True)
                        datadict = data.dict

                        try:
                            completedatadictlist = completedatadictlist+\
                                                            datadict[u'Items']
                        except:
                            sys.stdout.write(u'No data available within log.\n')
                            raise NoContentsFoundForOperationError(u"Unable " \
                                                           "to retrieve logs.")
                    else:
                        morepages = False
            else:
                datadict = list()

                for members in completedatadictlist:
                    memberpath = members[self.typepath.defs.hrefstring]
                    data = self._rdmc.app.get_handler(memberpath, silent=True)
                    datadict = datadict+[data.dict]

                completedatadictlist = datadict

            if completedatadictlist:
                try:
                    return completedatadictlist
                except Exception:
                    sys.stdout.write(u"Could not get the data from server!\n")
                    raise NoContentsFoundForOperationError(u"Unable to " \
                                                            "retrieve logs.")
            else:
                sys.stdout.write(u"No data present!\n")
                raise NoContentsFoundForOperationError(u"Unable to retrieve " \
                                                                        "logs.")
        else:
            sys.stdout.write(u"Path not found for input log!\n")
            raise NoContentsFoundForOperationError(u"Unable to retrieve logs.")

    def returnimlpath(self, options=None):
        """Return the requested path of the IML logs

        :param options: command line options
        :type options: list.
        """
        path = ""
        sel = self.typepath.defs.typestring
        val = self.typepath.defs.logservicetype
        filtereddatainstance = self._rdmc.app.filter(query=val, sel=sel, \
                                                                        val=val)

        try:
            filtereddictslists = [x.resp.dict for x in filtereddatainstance]
            if not filtereddictslists:
                raise NoContentsFoundForOperationError("Unable to retrieve instance.")
            for filtereddict in filtereddictslists:
                if filtereddict[u'Name'] == u'Integrated Management Log':
                    if options.clearlog:
                        if self.typepath.defs.flagforrest:
                            linkpath = filtereddict[u'links']
                            selfpath = linkpath[u'self']
                            path = selfpath[u'href']
                        elif self.typepath.defs.isgen9:
                            path = filtereddict[self.typepath.defs.hrefstring]
                        else:
                            actiondict = filtereddict[u"Actions"]
                            clearkey = [x for x in actiondict if x.\
                                                endswith(u"ClearLog")]
                            path = actiondict[clearkey[0]][u"target"]
                    else:
                        linkpath = filtereddict[u'links'] if u"links" in \
                                                filtereddict else filtereddict
                        dictpath = linkpath[u'Entries']
                        dictpath = dictpath[0] if isinstance(dictpath, list) \
                                                                else dictpath
                        path = dictpath[self.typepath.defs.hrefstring]
            if not path:
                raise NoContentsFoundForOperationError("Unable to retrieve logs.")
        except NoContentsFoundForOperationError as excp:
            raise excp
        except Exception as excp:
#             self._rdmc.app.warn(str(excp))
            sys.stdout.write('No path found for the entry.\n')
            raise NoContentsFoundForOperationError("Unable to retrieve logs.")

        if self._rdmc.opts.verbose:
            sys.stdout.write(str(path)+'\n')

        return path

    def returnielpath(self, options=None):
        """Return the requested path of the IEL logs

        :param options: command line options
        :type options: list.
        """
        path = ""
        sel = self.typepath.defs.typestring
        val = self.typepath.defs.logservicetype
        filtereddatainstance = self._rdmc.app.filter(query=val, sel=sel, \
                                                                        val=val)

        try:
            filtereddictslists = [x.resp.dict for x in filtereddatainstance]
            if not filtereddictslists:
                raise NoContentsFoundForOperationError("Unable to retrieve instance.")
            for filtereddict in filtereddictslists:
                if filtereddict[u'Name'] == u'iLO Event Log':
                    if options.clearlog:
                        if self.typepath.defs.flagforrest:
                            linkpath = filtereddict[u'links']
                            selfpath = linkpath[u'self']
                            path = selfpath[u'href']
                        elif self.typepath.defs.isgen9:
                            path = filtereddict[self.typepath.defs.hrefstring]
                        else:
                            actiondict = filtereddict[u"Actions"]
                            clearkey = [x for x in actiondict if \
                                                        x.endswith(u"ClearLog")]
                            path = actiondict[clearkey[0]][u"target"]
                    else:
                        linkpath = filtereddict[u'links'] if u"links" in \
                                                filtereddict else filtereddict
                        dictpath = linkpath[u'Entries']
                        dictpath = dictpath[0] if isinstance(dictpath, list) else\
                                                                    dictpath
                        path = dictpath[self.typepath.defs.hrefstring]

            if not path:
                raise NoContentsFoundForOperationError("Unable to retrieve logs.")
        except NoContentsFoundForOperationError as excp:
            raise excp
        except Exception as excp:
#             self._rdmc.app.warn(str(excp))
            sys.stdout.write(u'No path found for the entry.\n')
            raise NoContentsFoundForOperationError(u"Unable to retrieve logs.")

        if self._rdmc.opts.verbose:
            sys.stdout.write(str(path)+'\n')

        return path

    def returnahspath(self, options):
        """Return the requested path of the AHS logs

        :param options: command line options
        :type options: list.
        """
        path = ""

        if options.filename:
            raise InvalidCommandLineError("AHS logs to be downloadded with " \
                            "default name! Re-run command without filename!")

        sel = self.typepath.defs.typestring
        val = self.typepath.defs.hpiloactivehealthsystemtype
        filtereddatainstance = self._rdmc.app.filter(query=val, sel=sel, \
                                                                        val=val)

        try:
            filtereddictslists = [x.resp.dict for x in filtereddatainstance]

            if not filtereddictslists:
                raise NoContentsFoundForOperationError("Unable to retrieve log"\
                                                                " instance.")

            for filtereddict in filtereddictslists:
                if options.clearlog:
                    if self.typepath.defs.flagforrest:
                        linkpath = filtereddict[u'links']
                        selfpath = linkpath[u'self']
                        path = selfpath[u'href']
                    elif self.typepath.defs.isgen9:
                        path = filtereddict[self.typepath.defs.hrefstring]
                    else:
                        actiondict = filtereddict[u"Actions"]
                        clearkey = [x for x in actiondict if \
                                                        x.endswith(u"ClearLog")]
                        path = actiondict[clearkey[0]][u"target"]
                else:
                    linkpath = filtereddict[u'links'] if u'links' in \
                                        filtereddict else filtereddict[u"Links"]

                    ahslocpath = linkpath[u'AHSLocation']
                    path = ahslocpath[u'extref']
                    weekpath = None

                    if options.downloadallahs:
                        path = path
                    elif options.customiseAHS:
                        custr = options.customiseAHS
                        if custr.startswith(("'", '"')) and custr.\
                                                        endswith(("'", '"')):
                            custr = custr[1:-1]

                        if custr.startswith(u"from="):
                            path = path.split(u"downloadAll=1")[0]

                        path = path+custr
                    else:
                        if 'RecentWeek' in linkpath.keys():
                            weekpath = linkpath[u"RecentWeek"][u'extref']
                        elif "AHSFileStart" in filtereddict.keys():
                            enddate = filtereddict["AHSFileEnd"].split("T")[0]
                            startdate = filtereddict["AHSFileStart"].\
                                                                split("T")[0]

                            enddat = map(int, enddate.split('-'))
                            startdat = map(int, startdate.split('-'))

                            weekago = datetime.datetime.now() - \
                                                    datetime.timedelta(days=6)
                            weekagostr = map(int, (str(weekago).split()[0]).\
                                                                    split('-'))

                            strdate = min(max(datetime.date(weekagostr[0], \
                                weekagostr[1], weekagostr[2]), \
                                  datetime.date(startdat[0], startdat[1], \
                                    startdat[2])), datetime.date(enddat[0], \
                                                         enddat[1], enddat[2]))

                            aweekstr = "from=" + str(strdate) + "&&to=" + \
                                                                        enddate
                        else:
                            week_ago = datetime.datetime.now() - \
                                                    datetime.timedelta(days=6)
                            aweekstr = "from=" + str(week_ago).split()[0] + \
                                        "&&to=" + str(datetime.datetime.now()).\
                                        split()[0]

                        path = path.split(u"downloadAll=1")[0]
                        path = weekpath if weekpath else path+aweekstr

            if not path:
                raise NoContentsFoundForOperationError("Unable to retrieve logs.")
        except NoContentsFoundForOperationError as excp:
            raise excp
        except Exception as excp:
#             self._rdmc.app.warn(str(excp))
            sys.stdout.write('No path found for the entry.\n')
            raise NoContentsFoundForOperationError("Unable to retrieve logs.")

        if self._rdmc.opts.verbose:
            sys.stdout.write(str(path)+'\n')

        return path

    def savedata(self, options=None, data=None):
        """Save logs into the specified filename

        :param options: command line options
        :type options: list.
        :param data: log data
        :type data: dict
        """
        if data:
            data = self.filterdata(data=data, tofilter=options.filter)
            if options.service == 'AHS':
                filename = self.getahsfilename(options)

                with open(filename, 'wb') as foutput:
                    foutput.write(data)
            elif options.filename:
                with open(options.filename[0], 'w') as foutput:
                    if options.json:
                        foutput.write(str(json.dumps(data, indent=2)))
                    else:
                        foutput.write(str(json.dumps(data)))
            else:
                sys.stdout.write('Provide filename to store data.\n')
                raise InvalidFileInputError("")

    def downloadahslocally(self, options=None):
        """Download AHS logs locally

        :param options: command line options
        :type options: list.
        """
        try:
            self.downloadahslocalworker(options)
        except Exception, excp:
            self.unmountbb()
            raise excp
        return

    def downloadahslocalworker(self, options):
        """Worker function to download AHS logs locally

        :param options: command line options
        :type options: list.
        """
        self.dontunmount = True

        if self.typepath.ilogen < 4:
            raise IncompatibleiLOVersionError(u"Need at least iLO 4 for "\
                                                    u"this program to run!\n")

        if options.filename:
            raise InvalidCommandLineErrorOPTS("AHS logs must be downloaded with " \
                            "default name! Re-run command without filename!")

        if int(risblobstore2.BlobStore2().get_security_state()) > 3:
            raise SecurityStateError("AHS logs cannot be downloaded" \
                                        " locally in high security state.\n")

        self.lib = risblobstore2.BlobStore2.gethprestchifhandle()

        sys.stdout.write(u"Mounting AHS partition...\n")

        try:
            (manual_ovr, abspath) = self.getbbabspath()
        except PartitionMoutingError:
            self.mountbb()
            (manual_ovr, abspath) = self.getbbabspath()
            self.dontunmount = False

        self.abspath = os.path.join(abspath, 'data')

        self.updateiloversion()
        allfiles = self.getfilenames(options=options)
        cfilelist = self.getclistfilelisting()
        self.getdatfilelisting(cfilelist=cfilelist, allfile=allfiles)
        self.createahsfile(ahsfile=self.getahsfilename(options))

        if not manual_ovr:
            self.unmountbb()
        else:
            self.unmountbb()
            self.manualunmountbb(abspath)

    def updateiloversion(self):
        """Update iloversion to create appropriate headers."""
        self.lib.updateiloversion.argtypes = [ctypes.c_float]
        self.lib.updateiloversion(float('2.'+str(self.typepath.ilogen)))

    def createahsfile(self, ahsfile=None):
        """Create the AHS file

        :param ahsfile: ahsfilename
        :type ahsfile: str
        """
        self.clearahsfile(ahsfile=ahsfile)
        self.lib.setAHSFilepath.argtypes = [ctypes.c_char_p]
        self.lib.setAHSFilepath(os.path.abspath(ahsfile))
        self.lib.setBBdatapath.argtypes = [ctypes.c_char_p]
        self.lib.setBBdatapath(self.abspath)
        self.lib.createAHSLogFile_G9()

    def clearahsfile(self, ahsfile=None):
        """Clear the ahslog file if already present in filesystem

        :param ahsfile: ahsfilename
        :type ahsfile: str
        """
        try:
            os.remove(ahsfile)
        except:
            pass

    def getdatfilelisting(self, cfilelist=None, allfile=None):
        """Create headers based on the AHS log files within blackbox

        :param cfilelist: configuration files in blackbox
        :type cfilelist: list of strings
        :param allfile: all files within blackbox
        :type allfile: list
        """
        for files in allfile:
            if files.startswith((".", "..")):
                continue

            bisrequiredfile = False

            if files.split(".")[0] in [x.split(".")[0] for x in cfilelist]:
                if files.endswith("bb"):
                    bisrequiredfile = True
                    self.lib.updatenfileoptions()

            self.lib.gendatlisting.argtypes = [ctypes.c_char_p, \
                                                ctypes.c_bool, ctypes.c_uint]

            filesize = os.stat(os.path.join(self.abspath, files)).st_size
            self.lib.gendatlisting(files, bisrequiredfile, filesize)

    def getfilenames(self, options=None):
        """Get all file names from the blacbox directory."""
        datelist = list()
        allfiles = list()

        filenames = next(os.walk(self.abspath))[2]
        timenow = (str(datetime.datetime.now()).split()[0]).split('-')
        strdate = enddate = datetime.date(int(timenow[0]),\
                                            int(timenow[1]), int(timenow[2]))

        if not options.downloadallahs and not options.customiseAHS:
            weekago = datetime.datetime.now() - datetime.timedelta(days=6)
            weekagostr = (str(weekago).split()[0]).split('-')
            strdate = datetime.date(int(weekagostr[0]), int(weekagostr[1]), \
                                                            int(weekagostr[2]))

        if options.customiseAHS:
            instring = options.customiseAHS
            if instring.startswith(("'", '"')) and instring.\
                                                endswith(("'", '"')):
                instring = instring[1:-1]
            try:
                (strdatestr, enddatestr) = map(lambda e: e.split('-'), \
                                    instring.split("from=")[-1].split("&&to="))
                strdate = datetime.date(int(strdatestr[0]),\
                                      int(strdatestr[1]), int(strdatestr[2]))
                enddate = datetime.date(int(enddatestr[0]),\
                                      int(enddatestr[1]), int(enddatestr[2]))
            except Exception as excp:
                self._rdmc.app.warn(excp)
                raise InvalidCommandLineError("Cannot parse customized AHSinput.")

        atleastonefile = False
        for files in filenames:
            if not files.endswith("bb"):
                #Check the logic for the non bb files
                allfiles.append(files)
                continue

            if options.downloadallahs:
                atleastonefile = True
            filenoext = files.rsplit(".", 1)[0]
            filesplit = filenoext.split("-")

            try:
                newdate = datetime.date(int(filesplit[1]),\
                                      int(filesplit[2]), int(filesplit[3]))
                datelist.append(newdate)

                if (strdate <= newdate) and (newdate <= enddate) and \
                                    not options.downloadallahs:
                    allfiles.append(files)
                    atleastonefile = True
            except:
                pass

        if options.downloadallahs:
            strdate = min(datelist) if datelist else strdate
            enddate = max(datelist) if datelist else enddate
        else:
            strdate = max(min(datelist), strdate) if datelist else strdate
            enddate = min(max(datelist), enddate) if datelist else enddate

        if atleastonefile:
            self.updateminmaxdate(strdate=strdate, enddate=enddate)
            return filenames if options.downloadallahs else allfiles
        else:
            raise NoContentsFoundForOperationError("No AHS log files "\
                                                                "found.")

    def updateminmaxdate(self, strdate=None, enddate=None):
        """Get the minimum and maximum date of files into header

        :param strdate: starting date of ahs logs
        :type strdate: dateime obj
        :param enddate: ending date of ahs logs
        :type enddate: datetime obj
        """
        self.lib.updateMinDate.argtypes = [ctypes.c_int, \
                                                    ctypes.c_int, ctypes.c_int]
        self.lib.updateMinDate(strdate.year, strdate.month, strdate.day)
        self.lib.updateMaxDate.argtypes = [ctypes.c_int, \
                                                    ctypes.c_int, ctypes.c_int]
        self.lib.updateMaxDate(enddate.year, enddate.month, enddate.day)

    def getclistfilelisting(self):
        """Get files present within clist.pkg ."""
        sclistpath = os.path.join(self.abspath, "clist.pkg")
        cfilelist = []
        if os.path.isfile(sclistpath):
            cfile = open(sclistpath, 'rb')
            data = cfile.read()

            if data == "":
                raise InvalidCListFileError("Could not read Cfile\n")

            sizeofcfile = len(str(data))
            sizeofrecord = self.lib.sizeofchifbbfilecfgrecord()
            count = sizeofcfile/sizeofrecord
            revcount = 0

            while count >= 1:
                dat = data[revcount*sizeofrecord:(revcount+1)*sizeofrecord]
                dat = ctypes.create_string_buffer(dat)
                self.lib.getbbfilecfgrecordname.argtypes = [ctypes.c_char_p]
                self.lib.getbbfilecfgrecordname.restype = ctypes.c_char_p
                ptrname = self.lib.getbbfilecfgrecordname(dat)
                name = str(bytearray(ptrname[:32][:]))

                if name not in cfilelist:
                    cfilelist.append(name)

                count = count-1
                revcount = revcount+1

        return cfilelist

    def getbbabspath(self):
        """Get blackbox folder path."""
        count = 0

        while count < 20:
            if os.name == 'nt':
                drives = self.get_available_drives()

                for i in drives:
                    try:
                        label = win32api.GetVolumeInformation(i+':')[0]

                        if label == 'BLACKBOX':
                            abspathbb = i+':\\'
                            return (False, abspathbb)
                    except:
                        pass
            else:
                with open('/proc/mounts', 'r') as fmount:
                    while True:
                        lin = fmount.readline()

                        if len(lin.strip()) == 0:
                            break

                        if r"/BLACKBOX" in lin:
                            abspathbb = lin.split()[1]
                            return (False, abspathbb)

                if count > 3:
                    found, path = self.manualmountbb()
                    if found:
                        return (True, path)

            count = count+1
            time.sleep(1)

        raise PartitionMoutingError("iLO not responding to request " \
                                                "for mounting AHS partition")

    def manualmountbb(self):
        """Manually mount blackbox when after fixed time."""

        try:
            context = pyudev.Context()
            for device in context.list_devices(subsystem="block"):
                if device.get("ID_FS_LABEL") == "BLACKBOX":
                    dirpath = os.path.join(tempfile.gettempdir(), "BLACKBOX")

                    if not os.path.exists(dirpath):
                        try:
                            os.makedirs(dirpath)
                        except Exception, excp:
                            raise excp

                    pmount = subprocess.Popen(['mount', device.device_node, \
                        dirpath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    _, _ = pmount.communicate()

                    return (True, dirpath)
        except UnicodeDecodeError as excp:
            self.unmountbb()
            raise UnabletoFindDriveError(excp)

        return (False, None)

    def manualunmountbb(self, dirpath):
        """Manually unmount blackbox when after fixed time

        :param dirpath: mounted directory path
        :type dirpath: str
        """
        pmount = subprocess.Popen(['umount', dirpath], stdout=subprocess.PIPE, \
                                                        stderr=subprocess.PIPE)
        _, _ = pmount.communicate()

    def mountbb(self):
        """Mount blackbox."""
        bs2 = risblobstore2.BlobStore2()
        bs2.mount_blackbox()
        bs2.channel.close()

    def unmountbb(self):
        """Unmount blacbox."""
        if not self.dontunmount:
            bs2 = risblobstore2.BlobStore2()
            bs2.bb_media_unmount()
            bs2.channel.close()

    def get_available_drives(self):
        """Obtain all drives"""
        if 'Windows' not in platform.system():
            return []

        drive_bitmask = ctypes.cdll.kernel32.GetLogicalDrives()

        return list(itertools.compress(string.ascii_uppercase,\
            [ord(drive) - ord('0') for drive in bin(drive_bitmask)[:1:-1]]))

    def filterdata(self, data=None, tofilter=None):
        """Filter the logs

        :param data: log data
        :type data: dict
        :param tofilter: command line filter option
        :type tofilter: str
        """
        if tofilter and data:
            try:
                if (str(tofilter)[0] == str(tofilter)[-1])\
                                    and str(tofilter).startswith(("'", '"')):
                    tofilter = tofilter[1:-1]

                (sel, val) = tofilter.split('=')
                sel = sel.strip()
                val = val.strip()

                if val.lower() == "true" or val.lower() == "false":
                    val = val.lower() in ("yes", "true", "t", "1")
            except:
                raise InvalidCommandLineError("Invalid filter" \
                  " parameter format [filter_attribute]=[filter_value]")

            data = self._rdmc.app.filter_output(data, sel, val)
            if not data:
                raise NoContentsFoundForOperationError("Filter returned"\
                                                                " no matches.")

        return data

    def getahsfilename(self, options):
        """Create a default name if no ahsfilename is passed

        :param options: command line options
        :type options: list.
        """

        sel = self.typepath.defs.typestring
        val = u"ComputerSystem."
        filtereddatainstance = self._rdmc.app.filter(query=val, sel=sel, \
                                                                    val=val)
        snum = None

        try:
            filtereddictslists = [x.resp.dict for x in filtereddatainstance]

            if not filtereddictslists:
                raise NoContentsFoundForOperationError("")
        except Exception:
            try:
                resp = self._rdmc.app.get_handler(self.typepath.defs.systempath,\
                    silent=True, service=True, uncache=True)
                snum = resp.dict[u"SerialNumber"] if resp else snum
            except:
                raise NoContentsFoundForOperationError(u"Unable to retrieve " \
                                                            "log instance.")

        snum = filtereddictslists[0][u"SerialNumber"] if not snum else snum
        snum = u'UNKNOWN' if snum.isspace() else snum
        timenow = (str(datetime.datetime.now()).split()[0]).split('-')
        todaysdate = ''.join(timenow)

        ahsdefaultfilename = u'HPE_'+snum+u'_'+todaysdate+u'.ahs'

        if options.directorypath:
            ahsdefaultfilename = os.path.join(options.directorypath, \
                                                            ahsdefaultfilename)

        return ahsdefaultfilename

    def serverlogsvalidation(self, options):
        """ Serverlogs method validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        inputline = list()

        try:
            client = self._rdmc.app.get_current_client()
            if options.user and options.password:
                if not client.get_username():
                    client.set_username(options.user)
                if not client.get_password():
                    client.set_password(options.password)
        except Exception:
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

        if not inputline and not client:
            sys.stdout.write(u'Local login initiated...\n')
        if inputline or not client:
            self.lobobj.loginfunction(inputline)

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return
        customparser.add_option(
            '-f',
            '--filename',
            dest='filename',
            help="Use this flag if you wish to use a different"\
            " filename than the default one. The default filename is" \
            " ilorest.json.",
            action="append",
            default=None,
        )
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
            '--logout',
            dest='logout',
            action="store_true",
            help="Optionally include the logout flag to log out of the"\
            " server after this command is completed. Using this flag when"\
            " not logged in will have no effect",
            default=None,
        )
        customparser.add_option(
            '--selectlog',
            dest='service',
            help="""Read log from the given log service. Options: IML, """\
                    """IEL or AHS.""",
            default=None,
        )
        customparser.add_option(
            '--clearlog',
            '-c',
            dest='clearlog',
            action="store_true",
            help="""Clears the logs for a the selected option.""",
            default=None,
        )
        customparser.add_option(
            '--maintenancemessage',
            '-m',
            dest='mainmes',
            help="""Maintenance message to be inserted into the log. """\
                    """(IML LOGS ONLY FEATURE)""",
            default=None,
        )
        customparser.add_option(
            '--customiseAHS',
            dest='customiseAHS',
            help="""Allows customized AHS log data to be downloaded.""",
            default=None,
        )
        customparser.add_option(
            '--downloadallahs',
            dest='downloadallahs',
            action="store_true",
            help="""Allows complete AHS log data to be downloaded.""",
            default=None,
        )
        customparser.add_option(
            '--directorypath',
            dest='directorypath',
            help="""Directory path for the ahs file.""",
            default=None,
        )
        customparser.add_option(
            '--mpfile',
            dest='mpfilename',
            help="""use the provided filename to obtain server information.""",
            default=None,
        )
        customparser.add_option(
            '-o',
            '--outputdirectory',
            dest='outdirectory',
            help="""use the provided directory to output data for multiple server downloads.""",
            default=None,
        )
        customparser.add_option(
            '--mplog',
            dest='mplog',
            help="""used to indicate the logs to be downloaded on multiple servers. """\
            """Allowable values: IEL, IML, AHS, all or combination of any two.""",
            default=None,
        )
