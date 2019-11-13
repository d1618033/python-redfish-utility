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
""" Virtual Media Command for rdmc """

import sys

from argparse import ArgumentParser
from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group
from rdmc_helper import ReturnCodes, InvalidCommandLineError, Encryption, \
                                InvalidCommandLineErrorOPTS, IloLicenseError

class VirtualMediaCommand(RdmcCommandBase):
    """ Changes the iscsi configuration for the server that is currently """ \
                                                            """ logged in """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='virtualmedia',\
            usage='virtualmedia [ID] [URI] [OPTIONS]\n\n\tRun without' \
                    ' arguments to view the available virtual media sources.' \
                    '\n\texample: virtualmedia\n\n\tInsert virtual media and ' \
                    'set to boot on next restart.\n\texample: virtualmedia 2 ' \
                    'http://xx.xx.xx.xx/vm.iso --bootnextreset\n\n\tRemove ' \
                    'current inserted media.\n\texample: virtualmedia 2 --remove',\
            summary='Command for inserting and removing virtual media.',\
            aliases=['virtualmedia'],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.getobj = rdmcObj.commands_dict["GetCommand"](rdmcObj)
        self.setobj = rdmcObj.commands_dict["SetCommand"](rdmcObj)
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)
        self.rebootobj = rdmcObj.commands_dict["RebootCommand"](rdmcObj)

    def run(self, line):
        """ Main iscsi configuration worker function

        :param line: string of arguments passed in
        :type line: str.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        if len(args) > 2:
            raise InvalidCommandLineError("Invalid number of parameters. " \
                "virtualmedia command takes a maximum of 2 parameters.")
        else:
            self.virtualmediavalidation(options)

        resp = self._rdmc.app.get_handler(\
                          '/rest/v1/Managers/1/VirtualMedia/1', response=True, silent=True)

        if not resp.status == 200:
            raise IloLicenseError('')

        self.selobj.run("VirtualMedia.")
        ilover = self._rdmc.app.getiloversion()

        if self._rdmc.app.monolith.is_redfish:
            isredfish = True
            paths = self.getobj.getworkerfunction("@odata.id", options, results=True, uselist=False)
            ids = self.getobj.getworkerfunction("Id", options, results=True, uselist=False)
            paths = {ind:path for ind, path in enumerate(paths)}
            ids = {ind:id for ind, id in enumerate(ids)}
            for path in paths:
                paths[path] = paths[path]['@odata.id']
        else:
            isredfish = False
            paths = self.getobj.getworkerfunction("links/self/href", options, \
                    results=True, uselist=False)
            ids = self.getobj.getworkerfunction("Id", options, results=True, uselist=False)
            paths = {ind:path for ind, path in enumerate(paths)}
            ids = {ind:id for ind, id in enumerate(ids)}
            for path in paths:
                paths[path] = paths[path]['links']['self']['href']
        # To keep indexes consistent between versions
        if not list(ids.keys())[0] == list(list(ids.values())[0].values())[0]:
            finalpaths = {}
            for path in paths:
                finalpaths.update({int(list(ids[path].values())[0]): paths[path]})
            paths = finalpaths
        if options.removevm:
            self.vmremovehelper(args, options, paths, isredfish, ilover)
        elif len(args) == 2:
            self.vminserthelper(args, options, paths, isredfish, ilover)
        elif options.bootnextreset:
            self.vmbootnextreset(args, paths)
        elif not args:
            self.vmdefaulthelper(options, paths)
        else:
            raise InvalidCommandLineError("Invalid parameter(s). Please run"\
                                      " 'help virtualmedia' for parameters.")

        return ReturnCodes.SUCCESS

    def vmremovehelper(self, args, options, paths, isredfish, ilover):
        """Worker function to remove virtual media

        :param args: arguments passed from command line
        :type args: list
        :param paths: virtual media paths
        :type paths: list
        :param isredfish: redfish flag
        :type isredfish: bool
        :param ilover: iloversion
        :type ilover: int
        :param options: command line options
        :type options: list.
        """
        path = None

        if isredfish:
            path, body = self.vmredfishhelper('remove', args[0])
        else:
            if ilover <= 4.230:
                body = {"Image": None}
            else:
                body = {"Action": "EjectVirtualMedia", "Target": "/Oem/Hp"}

        try:
            path = paths[int(args[0])] if not path else path
        except:
            raise InvalidCommandLineError("Invalid input value for virtual " \
                                      "media please run the command with no " \
                                      "arguments for possible values.")

        if ilover <= 4.230:
            self._rdmc.app.patch_handler(path, body)
        else:
            self._rdmc.app.post_handler(path, body)

        if options.reboot:
            self.rebootobj.run(options.reboot)

    def vminserthelper(self, args, options, paths, isredfish, ilover):
        """Worker function to insert virtual media

        :param args: arguments passed from command line
        :type args: list
        :param paths: virtual media paths
        :type paths: list
        :param isredfish: redfish flag
        :type isredfish: bool
        :param ilover: iloversion
        :type ilover: int
        :param options: command line options
        :type options: list.
        """
        path = None
        if not args[1].startswith('http://') and not args[1].startswith('https://'):
            raise InvalidCommandLineError("Virtual media path must be a URL.")

        if isredfish:
            path, body = self.vmredfishhelper('insert', args[0], args[1])
        else:
            if ilover <= 4.230:
                body = {"Image": args[1]}
            else:
                body = {"Action": "InsertVirtualMedia", "Target": "/Oem/Hp", "Image": args[1]}

        try:
            path = paths[int(args[0])] if not path else path
        except:
            raise InvalidCommandLineError("Invalid input value for virtual " \
                                          "media please run the command with " \
                                          "no arguments for possible values.")

        if ilover <= 4.230:
            self._rdmc.app.patch_handler(path, body)
        else:
            self._rdmc.app.post_handler(path, body)

        if options.bootnextreset:
            self.vmbootnextreset(args, paths)

        if options.reboot:
            self.rebootobj.run(options.reboot)

    def vmdefaulthelper(self, options, paths):
        """Worker function to reset virtual media config to default

        :param paths: virtual media paths
        :type paths: list
        :param options: command line options
        :type options: list.
        """
        images = {}
        count = 0
        mediatypes = self.getobj.getworkerfunction(\
            "MediaTypes", options, results=True, uselist=False)
        ids = self.getobj.getworkerfunction("Id", options, results=True, uselist=False)
        ids = {ind:id for ind, id in enumerate(ids)}
        mediatypes = {ind:med for ind, med in enumerate(mediatypes)}
        # To keep indexes consistent between versions
        if not list(ids.keys())[0] == list(list(ids.values())[0].values())[0]:
            finalmet = {}
            for mount in mediatypes:
                finalmet.update({int(list(ids[mount].values())[0]): mediatypes[mount]})
            mediatypes = finalmet

        for path in paths:
            count += 1
            image = self._rdmc.app.get_handler(paths[path], service=True, silent=True)
            image = image.dict['Image']
            images.update({path: image})

        sys.stdout.write("Available Virtual Media Options:\n")

        for image in images:
            media = ""

            if images[image]:
                imagestr = images[image]
            else:
                imagestr = "None"

            for medtypes in mediatypes[image]['MediaTypes']:
                media += medtypes + " "

            sys.stdout.write("[%s] Media Types Available: %s Image Inserted:" \
                                        " %s\n" %(str(image), str(media), imagestr))

    def vmbootnextreset(self, args, paths):
        """Worker function to boot virtual media on next serverreset

        :param args: arguments passed from command line
        :type args: list
        :param paths: all virtual media paths
        :type paths: list
        """
        try:
            path = paths[int(args[0])]
        except:
            raise InvalidCommandLineError("Invalid input value for virtual media"\
                                        " please run the command with no " \
                                        "arguments for possible values.")

        self._rdmc.app.patch_handler(path, \
                    {"Oem":{self.typepath.defs.oemhp:{"BootOnNextServerReset":\
                                            True}}}, service=True, silent=True)

    def vmredfishhelper(self, action, number, image=None):
        """Redfish version of the worker function

        :param action: action item
        :type action: str
        :param number: virtual media ID
        :type number: int
        """

        results = self._rdmc.app.select(selector="VirtualMedia.")
        bodydict = None

        try:
            for result in results:
                if result.resp.dict['Id'] == number:
                    bodydict = result.resp.dict
                    break
        except:
            pass

        if not bodydict:
            raise InvalidCommandLineError("Invalid input value for virtual media"\
                                            " please run the command with no " \
                                            "arguments for possible values.")
        if action == 'remove' and not bodydict['Inserted']:
            raise InvalidCommandLineError("Invalid input value for virtual media."\
                    " No media present in this drive to unmount. Please recheck " \
                                            "arguments for possible values.")

        if action == 'insert' and image:
            for item in bodydict['Oem'][self.typepath.defs.oemhp]['Actions']:
                if 'InsertVirtualMedia' in item:
                    if self.typepath.defs.isgen10:
                        action = item.split('#')[-1]
                    else:
                        action = "InsertVirtualMedia"

                    path = bodydict['Oem'][self.typepath.defs.oemhp]['Actions'][item]['target']
                    body = {"Action": action, "Image": image}
                    break
        elif action == 'remove':
            for item in bodydict['Oem'][self.typepath.defs.oemhp]['Actions']:
                if 'EjectVirtualMedia' in item:
                    if self.typepath.defs.isgen10:
                        action = item.split('#')[-1]
                    else:
                        action = "EjectVirtualMedia"

                    path = bodydict['Oem'][self.typepath.defs.oemhp]['Actions'][item]['target']
                    body = {"Action": action}
                    break
        else:
            return None, None

        return path, body

    def virtualmediavalidation(self, options):
        """ sigrecomputevalidation method validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        inputline = list()

        try:
            client = self._rdmc.app.current_client
        except:
            if options.user or options.password or options.url:
                if options.url:
                    inputline.extend([options.url])
                if options.user:
                    if options.encode:
                        options.user = Encryption.decode_credentials(options.user)
                    inputline.extend(["-u", options.user])
                if options.password:
                    if options.encode:
                        options.password = Encryption.decode_credentials(options.password)
                    inputline.extend(["-p", options.password])
                if options.https_cert:
                    inputline.extend(["--https", options.https_cert])
            else:
                if self._rdmc.app.config.get_url():
                    inputline.extend([self._rdmc.app.config.get_url()])
                if self._rdmc.app.config.get_username():
                    inputline.extend(["-u", self._rdmc.app.config.get_username()])
                if self._rdmc.app.config.get_password():
                    inputline.extend(["-p", self._rdmc.app.config.get_password()])
                if self._rdmc.app.config.get_ssl_cert():
                    inputline.extend(["--https", self._rdmc.app.config.get_ssl_cert()])

        if inputline:
            self.lobobj.loginfunction(inputline)
        elif not client:
            raise InvalidCommandLineError("Please login or pass credentials" \
                                          " to complete the operation.")

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        add_login_arguments_group(customparser)

        customparser.add_argument(
            '--reboot',
            dest='reboot',
            help="Use this flag to perform a reboot command function after"\
            " completion of operations.  For help with parameters and"\
            " descriptions regarding the reboot flag, run help reboot.",
            default=None,
        )
        customparser.add_argument(
            '--remove',
            dest='removevm',
            action="store_true",
            help="Use this flag to remove the media from the selection.",
            default=False
        )
        customparser.add_argument(
            '--bootnextreset',
            dest='bootnextreset',
            action="store_true",
            help="Use this flag if you wish to boot from the image on "\
            "next server reboot. NOTE: The image will be ejected "\
            "automatically on the second server reboot so that the server "\
            "does not boot to this image twice.",
            default=False
        )
        customparser.add_argument(
            '-j',
            '--json',
            dest='json',
            action="store_true",
            help="Optionally include this flag if you wish to change the"\
            " displayed output to JSON format. Preserving the JSON data"\
            " structure makes the information easier to parse.",
            default=False
        )
