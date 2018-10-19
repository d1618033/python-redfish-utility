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
""" Single Sign On Command for rdmc """

from optparse import OptionParser, SUPPRESS_HELP
from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
            InvalidCommandLineErrorOPTS, NoContentsFoundForOperationError, Encryption

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
            optparser=OptionParser())
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
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        if not len(args) == 2:
            raise InvalidCommandLineError("singlsignon command only takes "\
                                                                "2 parameters.")

        if options.encode and options.user and options.password:
            options.user = Encryption.decode_credentials(options.user)
            options.password = Encryption.decode_credentials(options.password)

        self.singlesignonvalidation(options)

        actionitem = None
        select = self.typepath.defs.hpilossotype
        results = self._rdmc.app.filter(select, None, None)

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

            body = {"Action": actionitem, "CertType": certtype, \
                                                        "CertInput": certtext}

        elif args[0].lower() == 'deleterecord':
            if args[1].lower() == 'all':
                actionitem = "DeleteAllSSORecords"
                body = {"Action": actionitem}
            else:
                actionitem = "DeleteSSORecordbyNumber"

                try:
                    body = {"Action": actionitem, "RecordNumber": int(args[1])}
                except:
                    raise InvalidCommandLineError("Record to delete must"\
                                                                " be a number")
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
            '-e',
            '--enc',
            dest='encode',
            action='store_true',
            help=SUPPRESS_HELP,
            default=False,
        )
