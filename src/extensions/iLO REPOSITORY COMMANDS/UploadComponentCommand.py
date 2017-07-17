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
""" Upload Component Command for rdmc """

import os
import sys
import json
import time
import shutil

from random import choice
from string import ascii_lowercase
from optparse import OptionParser

import ctypes
from ctypes import c_char_p, c_int, c_uint32

import redfish.hpilo.risblobstore2 as risblobstore2
from redfish.ris.rmc_helper import InvalidPathError

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, \
            InvalidCommandLineError, IncompatibleiLOVersionError, TimeOutError

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

    return str(hours) + " hour(s) " + str(minutes) + \
            " minute(s) " + str(seconds) + " second(s) "

class UploadComponentCommand(RdmcCommandBase):
    """ Constructor """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self, \
            name='uploadcomp', \
            usage='uploadcomp [OPTIONS]\n\n\tRun to upload the component on ' \
                'to iLO Repository\n\n\tUpload component to the iLO ' \
                'repository.\n\texample: uploadcomp --component <path> ' \
                '--compsig <path_to_signature>\n\n\tFlash the component ' \
                'instead of add to the iLO repository.\n\texample: ' \
                'uploadcomp --component <binary_path> --update_target=True ' \
                '--update_repository=False', \
            summary='Upload components/binary to the iLO Repository.', \
            aliases=['Uploadcomp'], \
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commandsDict["LoginCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commandsDict["LogoutCommand"](rdmcObj)

    def run(self, line):
        """ Wrapper function for upload command main function

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

        if options.sessionid:
            url = self.sessionvalidation(options)
        else:
            url = None
            self.uploadcommandvalidation(options)

        if options.sessionid and not url:
            raise InvalidCommandLineError(\
                                      'Url muse be included with sessionid. \
                                      Session is not required for local mode.')

        if not options.sessionid and self.typepath.defs.isgen9:
            raise IncompatibleiLOVersionError(\
                      'iLO Repository commands are only available on iLO 5.')

        filestoupload = self._check_and_split_files(options)

        if options.forceupload or self.componentvalidation(options, url, \
                                                                filestoupload):
            start_time = time.time()
            ret = ReturnCodes.FAILED_TO_UPLOAD_COMPONENT

            if not url and 'blobstore' in self._rdmc.app.get_current_client()\
                                                    ._rest_client.get_base_url():
                ret = self.uploadlocally(filestoupload, options)
            else:
                ret = self.uploadfunction(filestoupload, options, url)

            sys.stdout.write("%s\n" % human_readable_time(time.time() - \
                                                                    start_time))

            if len(filestoupload) > 1:
                path, _ = os.path.split((filestoupload[0])[1])
                shutil.rmtree(path)

            if options.logout:
                self.logoutobj.run("")
        else:
            sys.stdout.write('Upload stopped by user due to filename conflict.'\
                         ' If you would like to bypass this check include the'\
                         ' "--forceupload" flag.\n')
            ret = ReturnCodes.SUCCESS

        return ret

    def componentvalidation(self, options, url, filelist):
        """ Check and split the file to upload on to iLO Repository

        :param options: command line options
        :type options: list.
        :param url: url for sessionid
        :type url: string
        """
        validation = True
        prevfile = None

        path = '/redfish/v1/UpdateService/ComponentRepository/?$expand=.'
        results = self._rdmc.app.get_handler(path, sessionid=options.sessionid,\
            url=url, verbose=self._rdmc.opts.verbose, service=True, silent=True)

        results = results.dict

        if 'Members' in results:
            for comp in results['Members']:
                for filehndl in filelist:
                    if comp['Filename'] in filehndl[0] and not \
                            options.forceupload and not filehndl[0] == prevfile:
                        ans = raw_input("A component with the same name has " \
                                    "been found Are you sure you would like"\
                                    " to continue upload? (y/n)")

                        if ans.lower() == 'n':
                            validation = False
                            break

                    prevfile = filehndl[0]

        return validation

    def _check_and_split_files(self, options):
        """ Check and split the file to upload on to iLO Repository

        :param options: command line options
        :type options: list.
        """
        maxcompsize = 32 * 1024 * 1024
        size = os.path.getsize(options.component)
        filelist = []

        # Lets get the component filename
        _, filename = os.path.split(options.component)

        # This is to upload the binary directly to flash scenario
        if not options.componentsig:
            if not self.findcompsig(filename):
                return [(filename, options.component, options.componentsig, 0)]

        if size > maxcompsize:
            sys.stdout.write("Component is more than 32MB in size. ")
            sys.stdout.write("Component size = %s\n" % str(size))
            section = 1

            sigpath, _ = os.path.split(options.componentsig)
            filebasename = filename[:filename.rfind('.')]
            tempfoldername = \
                    "bmn" + ''.join(choice(ascii_lowercase) for i in range(12))

            tempdir = os.path.join(self._rdmc.app.config.get_cachedir(), \
                                                                tempfoldername)

            sys.stdout.write("Spliting component. Temporary " \
                                            "cache directory at %s\n" % tempdir)

            if not os.path.exists(tempdir):
                os.makedirs(tempdir)

            with open(options.component, 'rb') as component:
                while True:
                    data = component.read(maxcompsize)
                    if len(data) != 0:
                        sectionfilename = filebasename + "_part" + str(section)
                        sectionfilepath = os.path.join(tempdir, sectionfilename)

                        sectioncompsigpath = os.path.join(sigpath, \
                                                  sectionfilename + ".compsig")

                        writefile = open(sectionfilepath, 'wb')
                        writefile.write(data)
                        writefile.close()

                        item = (filename, sectionfilepath, sectioncompsigpath, \
                                                                    section - 1)

                        filelist.append(item)
                        section += 1

                    if len(data) != maxcompsize:
                        break

            return filelist
        else:
            return [(filename, options.component, options.componentsig, 0)]

    def uploadfunction(self, filelist, options=None, url=None):
        """ Main upload command worker function

        :param filelist: List of files to upload.
        :type filelist: list.
        :param options: command line options
        :type options: list.
        """

        #returns a tuple with the state and the result dict
        state, result = self.get_update_service_state(options.sessionid, url)

        if (state != "COMPLETED" and
                state != "COMPLETE" and
                state != "ERROR" and
                state != "IDLE"):
            sys.stdout.write("iLO UpdateService is busy. Please try again.")

            return ReturnCodes.UPDATE_SERVICE_BUSY

        try:
            sessionkey = self._rdmc.app.get_current_client()._rest_client.\
                                                            get_session_key()
        except:
            sessionkey = options.sessionid

        etag = ""
        hpe = result['Oem']['Hpe']
        urltosend = "/cgi-bin/uploadFile"

        if 'PushUpdateUri' in hpe:
            urltosend = hpe['PushUpdateUri']
        elif 'HttpPushUri' in result:
            urltosend = result['HttpPushUri']
        else:
            return ReturnCodes.FAILED_TO_UPLOAD_COMPONENT

        for item in filelist:
            ilo_upload_filename = item[0]

            ilo_upload_compsig_filename = ilo_upload_filename[\
                                  :ilo_upload_filename.rfind('.')] + ".compsig"

            componentpath = item[1]
            compsigpath = item[2]

            _, filename = os.path.split(componentpath)

            if not etag:
                etag = "sum" + filename.replace('.', '')
                etag = etag.replace('-', '')
                etag = etag.replace('_', '')

            section_num = item[3]
            sessionkey = (sessionkey).encode('ascii', 'ignore')

            parameters = {'UpdateRepository': options.update_repository, \
                          'UpdateTarget': options.update_target, \
                          'ETag': etag, \
                          'Section': section_num}
            try:
                data = [('sessionKey', sessionkey),
                        ('parameters', json.dumps(parameters))]

                if not compsigpath:
                    compsigpath = self.findcompsig(componentpath)
                if compsigpath:
                    data.append(('compsig', ilo_upload_compsig_filename, \
                                                    open(compsigpath, 'rb')))

                data.append(('file', ilo_upload_filename, open(componentpath, \
                                                                        'rb')))

                res = self._rdmc.app.post_handler(str(urltosend), data, \
                    response=True, sessionid=options.sessionid, url=url, \
                     headers={'Cookie': 'sessionKey=' + sessionkey})

                if res.status != 200:
                    return ReturnCodes.FAILED_TO_UPLOAD_COMPONENT
                else:
                    sys.stdout.write("Component " + filename + \
                                                    " uploaded successfully\n")

                if not self.wait_for_state_change(sessionid=options.sessionid, \
                                                                    url=url):
                    # Failed to upload the component.
                    raise TimeOutError("Update service busy.")

            except Exception as excep:
                raise excep

        return ReturnCodes.SUCCESS

    def wait_for_state_change(self, wait_time=300, sessionid=None, url=None):
        """ Wait for the iLO UpdateService to a move to terminal state.
        :param options: command line options
        :type options: list.
        :param wait_time: time to wait on upload
        :type wait_time: int.
        """
        total_time = 0
        spinner = ['|', '/', '-', '\\']
        state = ""
        sys.stdout.write("Waiting for iLO UpdateService to finish "\
                                                "processing the component\n")

        while total_time < wait_time:
            state, _ = self.get_update_service_state(sessionid, url)

            if state == "ERROR":
                return False
            elif state != "COMPLETED" and state != "IDLE" and state != "COMPLETE":
                # Lets try again after 8 seconds
                count = 0

                #fancy spinner
                while count <= 32:
                    sys.stdout.write('Updating: %s\r' % spinner[count % 4])
                    time.sleep(0.25)
                    count += 1

                total_time += 8
            else:
                break

        if total_time > wait_time:
            raise TimeOutError("UpdateService in " + state + " state for " + \
                                                        str(wait_time) + "s")

        return True

    def get_update_service_state(self, sessionid=None, url=None):
        """ Get the current UpdateService state

        :param options: command line options
        :type options: list.
        """
        path = "/redfish/v1/UpdateService"
        results = self._rdmc.app.get_handler(path, sessionid=sessionid, \
                                     url=url, verbose=self._rdmc.opts.verbose, \
                                     service=True, silent=True)

        if results and results.status == 200 and results.dict:
            output = results.dict

            if self._rdmc.opts.verbose:
                sys.stdout.write("UpdateService state = " + \
                                 (output['Oem']['Hpe']['State']).upper()+ "\n")

            return (output['Oem']['Hpe']['State']).upper(), results.dict
        else:
            return 'UNKNOWN', {}

    def findcompsig(self, comppath):
        """Try to find compsig if not included
        :param comppath: Path of file to find compsig for.
        :type comppath: str.
        """
        compsig = ''

        if comppath.endswith('.exe') or comppath.endswith('.zip'):
            cutpath = comppath.split(os.sep)
            filename = cutpath[-1].split('.')[0]

            try:
                location = os.sep.join(cutpath[:-1])
            except:
                location = os.curdir

            if not location:
                location = os.curdir

            files = [f for f in os.listdir(location) if os.path.isfile\
                                                    (os.path.join(location, f))]

            for filehndl in files:
                if filehndl.startswith(filename) and \
                                                filehndl.endswith('.compsig'):
                    sys.stdout.write('Compsig found for file.\n')

                    if location != '.':
                        compsig = location + os.sep + filehndl
                    else:
                        compsig = filehndl

                    break

        return compsig

    def uploadlocally(self, filelist, options=None):
        """Upload component locally

        :param filelist: List of files to upload.
        :type filelist: list.
        :param options: command line options
        :type options: list.
        """
        try:
            lib = risblobstore2.BlobStore2.gethprestchifhandle()
            lib.uploadComponent.argtypes = [c_char_p, c_char_p, c_char_p, c_uint32]
            lib.uploadComponent.restype = c_int

            multiupload = False

            for item in filelist:

                ilo_upload_filename = item[0]
                componentpath = item[1]
                compsigpath = item[2]

                if not compsigpath:
                    compsigpath = self.findcompsig(componentpath)

                _, filename = os.path.split(componentpath)

                # 0x00000001  // FUM_WRITE_NAND
                # 0x00000002  // FUM_USE_NAND
                # 0x00000004  // FUM_NO_FLASH
                # 0x00000008  // FUM_FORCE
                # 0x00000010  // FUM_SIDECAR
                # 0x00000020  // FUM_APPEND

                if not compsigpath and options.update_target:
                    # Just update the firmware
                    dispatchflag = ctypes.c_uint32(0x00000000)
                elif not compsigpath and not options.update_target and \
                                                    options.update_repository:
                    # uploading a secuare flash binary image onto the NAND
                    dispatchflag = ctypes.c_uint32(0x00000001 | 0x00000004)
                else:
                    # Uploading a component with a side car file.
                    dispatchflag = \
                        ctypes.c_uint32(0x00000001 | 0x00000004 | 0x00000010)

                if multiupload:
                    # For second upload to append if the component is > 32MB in size
                    dispatchflag = \
                                ctypes.c_uint32(0x00000001 | 0x00000004 | \
                                                        0x00000010 | 0x00000020)

                sys.stdout.write("Uploading component " + filename)
                ret = lib.uploadComponent(\
                  ctypes.create_string_buffer(compsigpath.encode('utf-8')),
                  ctypes.create_string_buffer(componentpath.encode('utf-8')),
                  ctypes.create_string_buffer(ilo_upload_filename), \
                                                                dispatchflag)

                if ret != 0:
                    sys.stdout.write("Component " + filename + \
                                                            " upload failed\n")

                    risblobstore2.BlobStore2.unloadchifhandle(lib)
                    return ReturnCodes.FAILED_TO_UPLOAD_COMPONENT
                else:
                    sys.stdout.write("Component " + filename + \
                                                    " uploaded successfully\n")

                multiupload = True

            risblobstore2.BlobStore2.unloadchifhandle(lib)

        except Exception as excep:
            raise excep

        return ReturnCodes.SUCCESS

    def uploadcommandvalidation(self, options):
        """ upload command method validation function

        :param options: command line options
        :type options: list.
        """
        inputline = list()

        if not options.component:
            raise InvalidCommandLineError("The component option is required"\
                                          " for this operation.")

        if not os.path.exists(options.component):
            raise InvalidPathError("Component not found at specified path.")

        if options.componentsig  and (not os.path.exists(options.componentsig)):
            raise InvalidCommandLineError("Component signature not found.")

        try:
            self._rdmc.app.get_current_client()
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

            if not len(inputline):
                sys.stdout.write(u'Local login initiated...\n')
            self.lobobj.loginfunction(inputline)

    def sessionvalidation(self, options):
        """ Raw get validation function

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
        """ Define command line argument for the upload command

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        customparser.add_option(
            '--url',
            dest='url',
            help='Use the provided iLO URL to login.',
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
            '--component',
            dest='component',
            help="""Component or binary file path to upload to the update service.""",
            default="",
        )
        customparser.add_option(
            '--compsig',
            dest='componentsig',
            help='Component signature file path needed by iLO to authenticate the '\
            'component file. If not provided will try to find the ' \
            'signature file from component file path.',
            default="",
        )
        customparser.add_option(
            '--forceupload',
            dest='forceupload',
            action="store_true",
            help='Add this flag to force upload components with the same name '\
                    'already on the repository.',
            default=False,
        )
        customparser.add_option(
            '--update_repository',
            dest='update_repository',
            action="store_false",
            help='If true uploads the component/binary on to the Repository, '\
            'Default[True] ',
            default=True,
        )
        customparser.add_option(
            '--update_target',
            dest='update_target',
            action="store_true",
            help='If true the uploaded component/binary will be flashed, Default[False] ',
            default=False,
        )
