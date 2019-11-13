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
""" Single Sign On Command for rdmc """
from argparse import ArgumentParser
from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group
from rdmc_helper import ReturnCodes, InvalidCommandLineError, Encryption, \
            InvalidCommandLineErrorOPTS, NoContentsFoundForOperationError

class SingleSignOnCommand(RdmcCommandBase):
    """ Commands Single Sign On actions to the server """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='singlesignon',\
            usage='singlesignon [OPTIONS]\n\n\tDelete all SSO records.\n\t' \
                'example: singlesignon deleterecord all\n\n\tDelete a ' \
                'specific SSO record.\n\texample: singlesignon ' \
                'deleterecord 1\n\n\tImport a DNS name.\n\texample: ' \
                'singlesignon importdns dnsname\n\n\tImport certificate' \
                ' from URI or file.\n\texample: singlesignon importcert cert',\
            summary="Command for all single sign on available actions. ",\
            aliases=['sso'],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)

    def run(self, line):
        """ Main SingleSignOnCommand function

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

        if not len(args) == 2:
            raise InvalidCommandLineError("singlesignon command only takes 2 parameters.")

        self.singlesignonvalidation(options)

        actionitem = None
        select = self.typepath.defs.hpilossotype
        results = self._rdmc.app.select(selector=select)

        try:
            results = results[0]
        except:
            pass

        if results:
            path = results.resp.request.path
        else:
            raise NoContentsFoundForOperationError("%s not found." % select)

        bodydict = results.resp.dict

        if args[0].lower() == 'importdns':
            actionitem = "ImportDNSName"
            body = {"Action": actionitem, "DNSName": args[1]}
        elif args[0].lower() == 'importcert':
            cert = None
            certtype = None
            actionitem = "ImportCertificate"

            try:
                cert = open(args[1], 'r')

                if cert:
                    certtext = cert.read()
                    cert.close()

                if certtext:
                    certtype = "DirectImportCert"
            except:
                pass

            if not certtype:
                certtype = "ImportCertUri"
                certtext = args[1]

            body = {"Action": actionitem, "CertType": certtype, "CertInput": certtext}

        elif args[0].lower() == 'deleterecord':
            if args[1].lower() == 'all':
                actionitem = "DeleteAllSSORecords"
                body = {"Action": actionitem}
            else:
                actionitem = "DeleteSSORecordbyNumber"

                try:
                    body = {"Action": actionitem, "RecordNumber": int(args[1])}
                except:
                    raise InvalidCommandLineError("Record to delete must be a number")
        else:
            raise InvalidCommandLineError('%s is not a valid command.' % args[0])

        try:
            for item in bodydict['Actions']:
                if actionitem in item:
                    if self.typepath.defs.isgen10:
                        actionitem = item.split('#')[-1]
                        body["Action"] = actionitem

                    path = bodydict['Actions'][item]['target']
                    break
        except:
            pass

        self._rdmc.app.post_handler(path, body)

        return ReturnCodes.SUCCESS

    def singlesignonvalidation(self, options):
        """ single sign on validation function

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
