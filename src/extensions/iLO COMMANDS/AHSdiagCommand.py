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
""" AHS diag Command for rdmc """

import os
import sys

from optparse import OptionParser
from ctypes import (c_char_p, c_ubyte, c_int, cdll, POINTER, create_string_buffer)

from redfish.hpilo.rishpilo import HpIlo
from rdmc_base_classes import RdmcCommandBase
import redfish.hpilo.risblobstore2 as risblobstore2
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
                                                    InvalidCommandLineErrorOPTS

if os.name != 'nt':
    from _ctypes import dlclose

class AHSdiagCommand(RdmcCommandBase):
    """ Add Sign/Marker posts into the AHS logs of the server """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='ahsdiag',\
            usage='\n\tahsdiag --WriteSignPost \n\tahsdiag --WriteMarkerPost'\
                    ' --instance 1 --markervalue 3 --markertext "DIMM Test Start"',\
            aliases=["ahsops"],\
            summary='Adding sign or Marker Post into AHS logs.',\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commandsDict["LoginCommand"](rdmcObj)
        self.selobj = rdmcObj.commandsDict["SelectCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commandsDict["LogoutCommand"](rdmcObj)
        self.serverlogsobj = rdmcObj.commandsDict["ServerlogsCommand"](rdmcObj)

        self.dynamicclass = -1
        self.lib = None
        self.channel = None

    def run(self, line):
        """ Main ahsdiag function

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

        self.ahsdiagvalidation()

        self.ahsdiagworkerfunction(options)

        return ReturnCodes.SUCCESS

    def ahsdiagworkerfunction(self, options):
        """Main ahsdig worker function

        :param options: command line options
        :type options: list.
        """
        if not options:
            raise InvalidCommandLineErrorOPTS("")

        if self.lib is None and self.channel is None:
            self.loadlib()
        if options.signpost and options.markerpost:
            raise InvalidCommandLineErrorOPTS("")
        if options.signpost:
            if options.inst or options.mval or options.mtext:
                raise InvalidCommandLineError("")
            self.addsignpost(options)
        elif options.markerpost:
            if options.inst and options.mval and options.mtext:
                self.addmarkerpost(options)
            else:
                raise InvalidCommandLineErrorOPTS("")
        else:
            sys.stdout.write('Choose an operation!\n')
            raise InvalidCommandLineErrorOPTS("")

    def addsignpost(self, options):
        """Function to add signpost

        :param options: command line options
        :type options: list.
        """
        sys.stdout.write("Start writing sign post ... \n")
        try:
            for i in range(3):
                if self.spregister():
                    break
                sys.stdout.write("attempting to register singnost..."\
                                 "failed {0} times\n".format(i))
                self.closedll()
                self.loadlib()
            sys.stdout.write("Successfully registered.\n")
            fail = True
            for _ in range(3):
                if self.signpostregister():
                    sys.stdout.write("Signpost was successful!\n")
                    fail = False
                    break
                else:
                    sys.stdout.write("Signpost attempt failed!\n")
            if options.postIML and fail:
                self.addimlpost(options)
            self.unregister()
        except Exception as excp:
            self.channel.close()
            raise excp

    def spregister(self):
        """Function that registers the signpost"""
        self.bb_class_allocate()
        if self.dynamicclass == -1:
            return False
        self.lib.bb_register_wrapper(self.dynamicclass)
        size = self.lib.sizeofbbregister()
        rcode = self.dowriteread(size)
        if rcode == 0:
            self.lib.bb_descriptor_code_wrapper()
            size = self.lib.sizeofbbdescriptorcode()
            rcode = self.dowriteread(size)
        return True

    def bb_class_allocate(self):
        """Function to obtain a handle for further operations"""
        self.lib.bb_class_allocate_wrapper()
        self.lib.getreq.restype = POINTER(c_ubyte)
        ptrreq = self.lib.getreq()
        sizeofbbchifresp = self.lib.sizeofBBCHIFRESP()
        size = self.lib.sizeofbbclassalloc()
        data = bytearray(ptrreq[:size][:])
        retlen = self.channel.write_raw(data)
        if retlen is not size:
            sys.stdout.write("Incomplete data was written"\
                                        " into iLO.\n")
        if retlen > 0:
            flag = True
            while flag:
                resp = self.channel.read_raw()
                resp = resp[:sizeofbbchifresp]
                self.lib.setresp.argtypes = [c_char_p]
                resp = "".join(map(chr, resp))
                resp = create_string_buffer(resp)
                self.lib.setresp(resp)
                if len(resp) != 0:
                    self.dynamicclass = self.lib.respmsgrcode()
                    sys.stdout.write("Do Read Return error code:{0}\n".\
                                     format(self.dynamicclass))
                    return
                else:
                    self.dynamicclass = 0
                    return
                if not self.lib.resphdrseqandpackseqcheck():
                    flag = False
        if retlen == -1:
            sys.stdout.write("return do Write code failed:{0}\n".format(retlen))
            retlen = self.channel.write_raw(data)
            if retlen is not size:
                sys.stdout.write("Incomplete data was written"\
                                        " into iLO.\n")
            if retlen <= 0:
                self.dynamicclass = -1
                return
            flag = True
            while flag:
                resp = self.channel.read_raw()
                resp = resp[:sizeofbbchifresp]
                resp = create_string_buffer(resp)
                self.lib.setresp.argtypes = [c_char_p]
                self.lib.setresp(resp)
                if len(resp) != 0:
                    self.dynamicclass = self.lib.respmsgrcode()
                    sys.stdout.write("Do Read Return error code{0}\n".\
                                     format(self.dynamicclass))
                    return
                else:
                    self.dynamicclass = 0
                    return
                if self.lib.resphdrseqandpackseqcheck():
                    flag = False
        self.dynamicclass = -1

    def unregister(self):
        """Function to unregister the handle"""
        self.lib.bb_unregister_wrapper()
        size = self.lib.sizeinunregister()
        rcode = self.dowriteread(size)
        if rcode == 0:
            sys.stdout.write("Unregistration successful!\n")
        else:
            sys.stdout.write("Failed to unregister with "\
                             "code:{0}.\n".format(rcode))

    def dowriteread(self, size):
        """Function responsible for communication with the iLO

        :param size: size of the buffer to be read or written
        :type size: int
        """
        ptrreq = self.lib.getreq()
        sizeofbbchifresp = self.lib.sizeofBBCHIFRESP()
        data = bytearray(ptrreq[:size][:])
        retlen = self.channel.write_raw(data)
        if retlen < 0:
            self.resetilo()
            return -1
        resp = self.channel.read_raw()
        if len(resp) < 0:
            self.resetilo()
            return -1
        resp = resp[:sizeofbbchifresp]
        self.lib.setresp.argtypes = [c_char_p]
        resp = "".join(map(chr, resp))
        resp = create_string_buffer(resp)
        self.lib.setresp(resp)
        rcode = self.lib.respmsgrcode()
        if rcode == 0:
            self.lib.updatehandle()
        return rcode

    def signpostregister(self):
        """Worker function of signpost register"""
        self.lib.bb_code_set_wrapper()
        size = self.lib.sizeinbbcodeset()
        returnval = self.dowriteread(size)
        if returnval is not 0:
            self.printsignpostregister(returnval)
            return False
        self.lib.bb_log_wrapper()
        size = self.lib.sizeinbblog()
        returnval = self.dowriteread(size)
        if returnval is not 0:
            self.printsignpostregister(returnval)
            return False
        self.lib.bb_log_static_wrapper()
        size = self.lib.sizeinbblog()
        returnval = self.dowriteread(size)
        if returnval is not 0:
            self.printsignpostregister(returnval)
            return False
        return True

    def printsignpostregister(self, returnval):
        """Commonly used output statement.

        :param returnval: return code for signpost
        :type returnval: int
        """
        sys.stdout.write("return signpost register failed={0}\n".\
                         format(returnval))

    def addmarkerpost(self, options):
        """Function to add marker post

        :param options: command line options
        :type options: list.
        """
        sys.stdout.write("Start writing marker post ... \n")
        try:
            for i in range(3):
                if self.mpregister():
                    break
                sys.stdout.write("attempting to register Marker Post..."\
                                 "failed {0} times\n".format(i))
                self.closedll()
                self.loadlib()
            sys.stdout.write("Successfully registered.\n")
            fail = True
            for _ in range(3):
                if self.markerpostregister(options):
                    sys.stdout.write("Marker Post was successful!\n")
                    fail = False
                    break
                else:
                    sys.stdout.write("Marker Post attempt failed!\n")
            if options.postIML and fail:
                self.addimlpost(options)
            self.unregister()
        except Exception as excp:
            self.channel.close()
            raise excp

    def mpregister(self):
        """Function that registers the marker post"""
        self.bb_class_allocate()
        sys.stdout.write("return code(dynamic class)={0}.\n".\
                         format(self.dynamicclass))
        if self.dynamicclass == -1:
            return False
        self.lib.bb_register_mwrapper(self.dynamicclass)
        size = self.lib.sizeofbbregister()
        rcode = self.dowriteread(size)
        if rcode == 0:
            self.lib.bb_descriptor_code_mwrapper()
            size = self.lib.sizeofbbdescriptorcode()
            rcode = self.dowriteread(size)
            self.lib.bb_descriptor_field_mwrapper()
            size = self.lib.sizeofbbdescriptorcode()
            rcode = self.dowriteread(size)
        return True

    def markerpostregister(self, options):
        """Worker function of marker post register

        :param options: command line options
        :type options: list.
        """
        self.lib.bb_code_set_mwrapper()
        size = self.lib.sizeinbbcodeset()
        returnval = self.dowriteread(size)
        if returnval is not 0:
            return False
        mval = int(options.mval)
        minst = int(options.inst)
        mtext = create_string_buffer(options.mtext)
        self.lib.markerpost_wrapper.argtypes = [c_int, c_int, c_char_p]
        self.lib.markerpost_wrapper(mval, minst, mtext)
        size = self.lib.sizeinbblogm()
        returnval = self.dowriteread(size)
        if returnval is not 0:
            return False
        return True

    def resetilo(self):
        """Function to reset iLO"""
        self.channel.close()
        self.channel = HpIlo()

    def loadlib(self):
        """Function to load the so library"""
        try:
            if os.name == 'nt':
                sys.stdout.write('Operation can be performed only on '\
                                 'linux systems!\n')
                raise InvalidCommandLineErrorOPTS("")
            else:
                self.channel = HpIlo()
                self.lib = risblobstore2.BlobStore2.gethprestchifhandle()
        except Exception as excp:
            raise InvalidCommandLineErrorOPTS(excp)

    def closedll(self):
        """Deallocate dll handle."""
        try:
            dlclose(self.lib)
        except Exception:
            pass

    def addimlpost(self, options):
        """Adding maintenance post from serverlogs.

        :param options: command line options
        :type options: list.
        """
        if options.signpost:
            imltext = u"Signpost Writing Failed"
        elif options.markerpost:
            imltext = u"Markerpost Writing Failed"
        options.service = u'IML'
        options.clearlog = None
        options.mainmes = imltext
        path = self.serverlogsobj.returnimlpath()
        self.serverlogsobj.addmaintenancelogentry(options, path=path)

    def ahsdiagvalidation(self):
        """ahsdiag method validation function """
        client = None
        try:
            client = self._rdmc.app.get_current_client()
        except Exception:
            if client:
                if not client.base_url == u'blobstore://.' or \
                        self._rdmc.app.config.get_url():
                    raise InvalidCommandLineError("ahsdiag command "\
                        "available for linux local login only.\n")
            if self._rdmc.app.config.get_url():
                raise InvalidCommandLineError("ahsdiag command "\
                        "available for linux local login only.\n")
            if not client:
                self.lobobj.run("")

    def definearguments(self, customparser):
        """Defines the required arguments for ahsdiag command.

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return
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
            '-s',
            '--WriteSignPost',
            dest='signpost',
            action="store_true",
            help="""Writes a sign post into the AHS log.""",
            default=False,
        )
        customparser.add_option(
            '-r',
            '--WriteMarkerPost',
            dest='markerpost',
            action="store_true",
            help="""Writes a marker post into the AHS log.""",
            default=False,
        )
        customparser.add_option(
            '-i',
            '--instance',
            dest='inst',
            help="""Argument required by marker post.""",
            default=None,
        )
        customparser.add_option(
            '-l',
            '--markervalue',
            dest='mval',
            help="""Argument required by marker post.""",
            default=None,
        )
        customparser.add_option(
            '-t',
            '--markertext',
            dest='mtext',
            help="""Argument required by marker post.""",
            default=None,
        )
        customparser.add_option(
            '-p',
            '--WriteIMLPost',
            dest='postIML',
            action="store_true",
            help="""Writes an IML entry if failure occurs.""",
            default=False,
        )
