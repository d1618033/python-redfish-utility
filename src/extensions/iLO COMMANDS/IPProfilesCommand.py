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
""" RawGet Command for rdmc """

import sys
import os
import json
import re
import time
import base64
import gzip
from cStringIO import StringIO

from datetime import datetime

from optparse import OptionParser

import redfish

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, UI,\
                    InvalidFileFormattingError, UnableToDecodeError, \
                    PathUnavailableError, InvalidFileInputError

class IPProfilesCommand(RdmcCommandBase):
    """ Raw form of the get command """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='ipprofiles',\
            usage='ipprofile [OPTIONS]\n\n\tDecodes and lists ' \
                    'ipprofiles. This is default option. No argument required'\
                    '\n\texample: ipprofiles'\
                    '\n\n\tAdds a new ipprofile from the provided json file.'\
                    '\n\tNOTE: Path can be absolute or from the '\
                    'same path you launch iLOrest.'\
                    '\n\texample: ipprofiles path'\
                    '\n\n\tDelete an ipprofile or list of profiles.\n\t'
                    'Provide the unique key that corresponds to the ipprofile'\
                    ' data you want to delete.\n\tSeveral keys can be comma-separated'\
                    ' with no space in between to delete more than one profile. '\
                    '\n\texample: ipprofiles -d key1,key2,key3...'\
                    '\n\n\tCopies all the ip profiles into the ip job queue .'\
                    'and start it\n\texample: ipprofiles --start',\
            summary='This is used to manage hpeipprofile data store.',\
            aliases=['ipprofiles'],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.setobj = rdmcObj.commands_dict["SetCommand"](rdmcObj)
        self.bootorderobj = rdmcObj.commands_dict["BootOrderCommand"](rdmcObj)
        self.path = '/redfish/v1/systems/1/hpeip/HpeIpProfiles/'
        self.ipjobs = '/redfish/v1/Systems/1/HpeIp/HpeIpJobs/'
        self.syspath = '/redfish/v1/Systems/1/'

    def run(self, line):
        """ Main raw get worker function

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

        self.validation(options)

        self.ipprofileworkerfunction(options, args)

    def ipprofileworkerfunction(self, options, args):
        """
        Ipprofile manager worker function. It calls appropriate function.
        :param options: command line options
        :type options: list.
        :param args: command line args
        :type args: string.
        """

        if options.del_key:
            self.deletekeyfromipprofiledata(options)
            return ReturnCodes.SUCCESS

        if options.start_ip:
            self.addprofileandstartjob(options)
            return ReturnCodes.SUCCESS

        if len(args) == 1:
            self.encodeandpatchipprofiledata(args)
            return ReturnCodes.SUCCESS

        self.getipprofiledataanddecode(options)

    def getipprofiledataanddecode(self, options):
        """
        Retrieves and decodes, if encoded, data from hpeprofile data store
        :param options: command line options
        :type options: list.
        :return returncode: int
        """

        try:
            results = self._rdmc.app.get_handler(self.path, \
                verbose=self._rdmc.opts.verbose, silent=True)
        except:
            raise PathUnavailableError("The Intelligent Provisioning resource "\
                                       "is not available on this system.")

        j2python = json.loads(results.read)
        for _, val in enumerate(j2python.keys()):
            if isinstance(val, basestring):
                result = self.decode_base64_string(str(j2python[val]))
                if result is not None:
                    j2python[val] = result

        results.read = json.dumps(j2python, ensure_ascii=False)

        if results and results.status == 200:
            if results.dict:
                if options.filename:
                    output = json.dumps(results.dict, indent=2,\
                                                    cls=redfish.ris.JSONEncoder)

                    filehndl = open(options.filename[0], "w")
                    filehndl.write(output)
                    filehndl.close()

                    sys.stdout.write(u"Results written out to '%s'.\n" % \
                                                            options.filename[0])
                else:
                    UI().print_out_json(results.dict)
        else:
            return ReturnCodes.NO_CONTENTS_FOUND_FOR_OPERATION

    def encodeandpatchipprofiledata(self, args):
        """
        Reads file in the given path, encode it,
        and apply it on iLO hpeipprofiles data store.
        :param args: command line args
        :type args: string.
        :retirn returncode: int
        """

        contentsholder = self.encode_base64_string(args)

        if "path" in contentsholder and "body" in contentsholder:
            self._rdmc.app.patch_handler(contentsholder["path"], \
                  contentsholder["body"], verbose=self._rdmc.opts.verbose)

        return ReturnCodes.SUCCESS

    def deletekeyfromipprofiledata(self, options):
        """
        Provide a string which represents a valid key in
        hpeipprofiles data store.
        :param options: command line options
        :type options: list.
        :return returncode: int
        """

        get_results = self._rdmc.app.get_handler(self.path,\
                verbose=self._rdmc.opts.verbose, silent=True)

        j2python = json.loads(get_results.read)
        all_keys = options.del_key[0].split(',')
        for ky in all_keys:
            if isinstance(ky, basestring) and j2python.get(ky.strip(), False):
                del j2python[ky.strip()]
            else:
                raise InvalidFileFormattingError(u"%s was not found .\n" % ky)

        payload = {}
        payload["path"] = self.path
        payload["body"] = j2python

        self._rdmc.app.put_handler(payload["path"], payload["body"],\
              verbose=self._rdmc.opts.verbose)

        return ReturnCodes.SUCCESS

    def addprofileandstartjob(self, options):
        """
        Adds ip profile into the job queue and start it.
        :return returncode: int
        """

        ipprovider = self.hasipprovider()
        if ipprovider is None:
            raise PathUnavailableError(u"System does not support this feature of IP.\n")

        ipjob = self.hasipjobs()
        if not ipjob:
            raise InvalidFileFormattingError(u"System does not have any IP"\
                                        u" profile to copy to the job queue.\n")

        current_state = self.inipstate(ipprovider)
        if current_state is None:
            raise PathUnavailableError(u"System does not support this feature of IP.\n")

        later_state = False
        ipstate = current_state["InIP"]
        if isinstance(ipstate, bool) and ipstate:
            #make sure we are in IP state.  Reset and monitor
            self.resetinipstate(ipprovider, current_state)
            #if we are in ip, monitor should be fast, use 15 seconds
            later_status = self.monitorinipstate(ipprovider, 3)
            if  later_status:
                self.copyjobtoipqueue(ipjob)
                sys.stdout.write(u"Copy operation was successful...\n")
                return ReturnCodes.SUCCESS

        if not isinstance(ipstate, bool):
#       inip is in an unknown state, so ...
        #patch to false, reboot, then monitor...if it turns true later...
        #then we are in IP state otherwise, manually check system...
            self.resetinipstate(ipprovider, current_state)
            later_status = self.monitorinipstate(ipprovider, 3)
            if  later_status:
                self.copyjobtoipqueue(ipjob)
                sys.stdout.write(u"Copy operation was successful...\n")
                return ReturnCodes.SUCCESS

        try:
            self.bootorderobj.run("--onetimeboot=Utilities "\
                                                    "--reboot=ColdBoot --commit")
        except:
            raise InvalidFileFormattingError(u"System failed to reboot")

        #After reboot, login again
        self.validation(options)

        later_state = self.monitorinipstate(ipprovider)
        if later_state:
            self.copyjobtoipqueue(ipjob)
            sys.stdout.write(u"Copy operation was successful...\n")
        else:
            raise InvalidFileFormattingError(u"\nSystem reboot took longer than 4 minutes."\
                u"something is wrong. You need to physically check this system.\n")

        return ReturnCodes.SUCCESS

    def resetinipstate(self, ipprovider, current_state):
        """
        Regardless of revious value, sets InIP value to False
        :param ipprovider: url path of heip.
        :type ipprovider: string.
        :param current_state: the value of InIP.
        :type current_state: dict
        """

        current_state['InIP'] = False

        payload = {}
        payload["path"] = ipprovider
        payload["body"] = current_state

        self._rdmc.app.put_handler(payload["path"], payload["body"],\
              verbose=self._rdmc.opts.verbose, silent=True)

    def monitorinipstate(self, ipprovider, timer=48):
        """
        Monitor InIP value every 5 seconds until it turns true or time expires.
        :param ipprovider: url path of heip.
        :type ipprovider: string.
        :param current_state: the value of InIP.
        :type current_state: boolean or unknown value.
        :param timer: time it takes iLO to boot into F10 assuming we are in boot state.
        :type timer: int
        :return ipstate: boolean
        """

        retry = timer # 48 * 5 = 4 minutes
        ipstate = False
        progress = self.progressbar()
        sys.stdout.write(u'\n')
        while retry > 0:
            time.sleep(5)
            progress.next()
            status = self.inipstate(ipprovider)
            if isinstance(status['InIP'], bool) and status['InIP']:
                ipstate = True
                break
            retry = retry - 1
        sys.stdout.write(u'\n')

        return ipstate

    def progressbar(self):
        """
        An on demand function use to output the progress while iLO is booting into F10.
        """
        while True:
            yield sys.stdout.write(u'>>>')

    def copyjobtoipqueue(self, ipjob):
        """
        Copies HpeIpJobs to Job queue. Function assumes there is a job to copy.
        A check was already done to make sure we have a job to copy in hasipjobs()
        :param ipjob: url path of heip.
        :type ipjob: list of dictionary.
        """

        get_results = self._rdmc.app.get_handler(self.ipjobs,\
                verbose=self._rdmc.opts.verbose, silent=True)

        j2python = json.loads(get_results.read)

        for ipj in ipjob:
            ky = ipj.keys()[0]
            j2python[ky] = ipj[ky]

        payload = {}
        payload["path"] = self.ipjobs
        payload["body"] = j2python

        self._rdmc.app.put_handler(payload["path"], payload["body"],\
              verbose=self._rdmc.opts.verbose, silent=True)

    def inipstate(self, ipprovider):
        """
        A check is done to determine if this version of iLO has InIP profile.
        :param ipprovider: url path of heip.
        :type ipprovider: string.
        :return is_inip: None or dict
        """

        if ipprovider.startswith('/redfish/'):
            get_results = self._rdmc.app.get_handler(ipprovider,\
                verbose=self._rdmc.opts.verbose, silent=True)
            result = json.loads(get_results.read)

            is_inip = None
            try:
                if 'InIP' in result.keys():
                    is_inip = result
            except KeyError:
                pass

        return is_inip

    def hasipjobs(self):
        """
        A check is done to determine if there is a job in HpeIpJobs we can
        copy to IP job queue
        :param options: command line options
        :type options: list.
        :return list_dict: list of dicts
        """

        results = self._rdmc.app.get_handler(self.path,\
                verbose=self._rdmc.opts.verbose, silent=True)

        j2python = json.loads(results.read)
        for _, val in enumerate(j2python.keys()):
            if isinstance(val, basestring):
                result = self.decode_base64_string(str(j2python[val]))
                if result is not None:
                    j2python[val] = result

        list_dict = []

        for key, value in j2python.iteritems():
            if not re.match('@odata', key):
                if len(key) >= 13 and key.isdigit():
                    list_dict.append({key:value}) # list of dict with valid key/value

        return list_dict

    def hasipprovider(self):
        """
        A check is done here to determine if this version of iLO has IP provider
        profile path using the  "Oem.Hpe.Links.HpeIpProvider"

        :return is_provider: None or string.
        """
        get_results = self._rdmc.app.get_handler(self.syspath, \
                verbose=self._rdmc.opts.verbose, silent=True)

        result = json.loads(get_results.read)

        is_ipprovider = None
        try:
            is_ipprovider = result['Oem']['Hpe']['Links']\
                ['HpeIpProvider'].values()[0]
        except KeyError:
            pass

        return is_ipprovider

    def validation(self, options):
        """ IPProfiles validation function

        :param options: command line options
        :type options: list.
        """
        inputline = list()

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

            self.lobobj.loginfunction(inputline, skipbuild=True)

    def decode_base64_string(self, str_b64):
        """
        Decodes a given string that was encoded with base64 and gzipped.
        :param str_b64: a string that was base64 encoded and the  gzipped
        :type str_b64: string.
        """

        read_data = None
        if isinstance(str_b64, basestring) and str_b64:
            try:
                decoded_str = base64.decodestring(str(str_b64))
                inbuffer = StringIO(decoded_str)
                gzffile = gzip.GzipFile(mode='rb', fileobj=inbuffer)
                read_data = ""
                for line in gzffile.readlines():
                    read_data = read_data + line
            except:
                pass

            return read_data

    def encode_base64_string(self, args):
        """
        Encode a given string  with base64 and gzip it.
        :param args: command line args
        :type args: string.
        """

        payload = {}
        filename = args[0]
        if filename:
            if not os.path.isfile(filename):
                raise InvalidFileInputError("File '%s' doesn't exist. "\
                    "Please create file by running 'save' command."\
                     % filename)

            try:
                inputfile = open(filename, 'r')
                contentsholder = json.loads(inputfile.read())
            except:
                raise InvalidFileFormattingError("Input file '%s' was not "\
                                                 "format properly."
                                                 % filename)

            try:
                text = json.dumps(contentsholder)
                buf = StringIO()
                gzfile = gzip.GzipFile(mode='wb', fileobj=buf)
                gzfile.write(text)
                gzfile.close()

                en_text = base64.encodestring(buf.getvalue())

                epoch = datetime.utcfromtimestamp(0)
                now = datetime.utcnow()
                delta = now - epoch
                time_stamp = delta.total_seconds() * 1000
                time_stamp = repr(time_stamp).split('.')[0]

                body_text = {time_stamp: en_text.strip()}
                payload["body"] = body_text
                payload["path"] = self.path
            except:
                raise UnableToDecodeError("Error while encoding string.")

        return payload

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
            help="""Write results to the specified file.""",
            action="append",
            default=None,
        )
        customparser.add_option(
            '-d',
            '--delete',
            dest='del_key',
            action='append',
            help='Look for the key or keys in the ipprofile manager and delete',
            default=None,
        )
        customparser.add_option(
            '-s',
            '--start',
            dest='start_ip',
            action='store_true',
            help='Copies all the ip profile into the job queue and start it',
            default=None,
        )
