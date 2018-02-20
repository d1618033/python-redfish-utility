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
""" Certificates Command for rdmc """

import sys

from optparse import OptionParser
from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
            InvalidCommandLineErrorOPTS, NoContentsFoundForOperationError, \
            InvalidFileInputError, IncompatibleiLOVersionError

__filename__ = 'certificate.txt'

class CertificateCommand(RdmcCommandBase):
    """ Commands Certificates actions to the server """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='certificate',\
            usage='certificate [OPTIONS]\n\n\tImport auth CA certificate.' \
            '\n\texample: certificate ca certfile.txt\n\n\tImport auth '\
            'CRL certificate.\n\texample: certificate crl uri\n\n\t'\
            'Import an iLO TLS certificate.\n\texample: certificate tls'\
            ' certfile.txt\n\n\tGenerate an https certificate signing'\
            ' request.\n\texmaple: certificate csr [ORG_NAME] [ORG_UNIT]'\
            ' [COMMON_NAME] [COUNTRY] [STATE] [CITY]\n\n\tNOTE: please make ' \
            'sure the order of arguments is correct. The\n\tparameters ' \
            'are extracted base on their position in the arguments ' \
            'list.\n\n\tGet certificate signing request.\n\texample: '\
            'certificate getcsr\n\n\tNOTE: Use the singlesignon command '
            'to import single sign on certificates',\
            summary="Command for importing both iLO and login authorization "\
                "certificates as well as generating iLO certificate signing "\
                "requests",\
            aliases=["certificate"],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commandsDict["LoginCommand"](rdmcObj)

    def run(self, line):
        """ Main Certificates Command function

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

        if args[0].lower() == 'getcsr' and not len(args) == 1:
            raise InvalidCommandLineError("This certificates command only " \
                                                        "takes 1 parameter.")
        elif args[0].lower() == 'csr' and not len(args) == 7:
            raise InvalidCommandLineError("This certificates command takes "\
                                                                "7 parameters.")
        elif not 'csr' in args[0].lower() and not len(args) == 2:
            raise InvalidCommandLineError("This certificates command only " \
                                                        "takes 2 parameters.")

        self.certificatesvalidation(options)

        if args[0].lower() == 'csr':
            self.generatecerthelper(args)
        elif args[0].lower() == 'ca':
            self.importcahelper(args)
        elif args[0].lower() == 'getcsr':
            self.getcerthelper(args, options)
        elif args[0].lower() == 'crl':
            self.importcrlhelper(args)
        elif args[0].lower() == 'tls':
            self.importtlshelper(args)
        else:
            raise InvalidCommandLineError("Invalid argument for certificates"\
                                                                    " command.")

        return ReturnCodes.SUCCESS

    def generatecerthelper(self, args):
        """ Main Certificates Command function

        :param args: list of args
        :type args: list.
        """

        select = self.typepath.defs.hphttpscerttype
        results = self._rdmc.app.filter(select, None, None)

        try:
            results = results[0]
        except:
            pass

        if results:
            path = results.resp.request.path
        else:
            raise NoContentsFoundForOperationError("Unable to find %s" % select)

        bodydict = results.resp.dict

        try:
            for item in bodydict['Actions']:
                if 'GenerateCSR' in item:
                    if self.typepath.defs.isgen10:
                        action = item.split('#')[-1]
                    else:
                        action = "GenerateCSR"

                    path = bodydict['Actions'][item]['target']
                    break
        except:
            action = "GenerateCSR"

        body = {"Action": action, "OrgName":args[1], "OrgUnit":args[2],\
                "CommonName": args[3], "Country": args[4], "State": args[5],\
                                                     "City": args[6]}

        sys.stdout.write("iLO is creating a new certificate signing request"\
                         " This process can take up to 10 minutes.\n")

        self._rdmc.app.post_handler(path, body)

    def getcerthelper(self, _, options):
        """ Helper function for importing CRL certificate

        :param options: list of options
        :type options: list.
        """

        select = self.typepath.defs.hphttpscerttype
        results = self._rdmc.app.filter(select, None, None)

        try:
            results = results[0]
        except:
            pass

        if results:
            try:
                csr = results.resp.dict['CertificateSigningRequest']
            except:
                raise NoContentsFoundForOperationError('Unable to find ' \
                                       'certificate. If you just generated a ' \
                                       'new certificate signing request the ' \
                                       'process may take up to 10 minutes.')

            if not options.filename:
                filename = __filename__
            else:
                filename = options.filename[0]

            outfile = open(filename, 'w')
            outfile.write(csr)
            outfile.close()

            sys.stdout.write("Certificate saved to: %s\n" % filename)
        else:
            raise NoContentsFoundForOperationError("Unable to find %s" % select)

    def importtlshelper(self, args):
        """ Helper function for importing TLS certificate

        :param args: list of args
        :type args: list.
        """
        file = args[1]

        try:
            with open(file) as certfile:
                certdata = certfile.read()
                certfile.close()
        except:
            raise InvalidFileInputError("Error loading the specified file.")

        select = self.typepath.defs.hphttpscerttype
        results = self._rdmc.app.filter(select, None, None)

        try:
            results = results[0]
        except:
            pass

        if results:
            path = results.resp.request.path
        else:
            raise NoContentsFoundForOperationError("Unable to find %s" % select)

        bodydict = results.resp.dict
        try:
            for item in bodydict['Actions']:
                if 'ImportCertificate' in item:
                    if self.typepath.defs.isgen10:
                        action = item.split('#')[-1]
                    else:
                        action = "ImportCertificate"
                    path = bodydict['Actions'][item]['target']
                    break
        except:
            action = "ImportCertificate"

        body = {"Action": action, "Certificate": certdata}

        self._rdmc.app.post_handler(path, body)

    def importcrlhelper(self, args):
        """ Helper function for importing CRL certificate

        :param args: list of args
        :type args: list.
        """
        if not self.typepath.flagiften:
            raise IncompatibleiLOVersionError("This certificate is not " \
                                                    "available on this system.")

        select = 'HpeCertAuth.'
        results = self._rdmc.app.filter(select, None, None)

        try:
            results = results[0]
        except:
            pass

        if results:
            bodydict = results.resp.dict
        else:
            raise NoContentsFoundForOperationError("Unable to find %s" % select)

        for item in bodydict['Actions']:
            if 'ImportCRL' in item:
                action = item.split('#')[-1]
                path = bodydict['Actions'][item]['target']
                break

        body = {"Action": action, "ImportUri": args[1]}

        self._rdmc.app.post_handler(path, body)

    def importcahelper(self, args):
        """ Helper function for importing TLS certificate

        :param args: list of args
        :type args: list.
        """
        if not self.typepath.flagiften:
            raise IncompatibleiLOVersionError("This certificate is not " \
                                                    "available on this system.")

        file = args[1]

        try:
            with open(file) as certfile:
                certdata = certfile.read()
                certfile.close()
        except:
            raise InvalidFileInputError("Error loading the specified file.")

        select = 'HpeCertAuth.'
        results = self._rdmc.app.filter(select, None, None)

        try:
            results = results[0]
        except:
            pass

        if results:
            bodydict = results.resp.dict
        else:
            raise NoContentsFoundForOperationError("Unable to find %s" % select)

        for item in bodydict['Actions']:
            if 'ImportCACertificate' in item:
                action = item.split('#')[-1]
                path = bodydict['Actions'][item]['target']
                break

        body = {"Action": action, "Certificate": certdata}

        self._rdmc.app.post_handler(path, body)

    def certificatesvalidation(self, options):
        """ certificates validation function

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

        if len(inputline):
            self.lobobj.loginfunction(inputline)
        elif not client:
            raise InvalidCommandLineError("Please login or pass credentials" \
                                                " to complete the operation.")

    def definearguments(self, customparser):
        """ Wrapper function for certificates command main function

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
            help="Use this flag if you wish to use a different"\
            " filename for the certificate signing request. The default" \
            " filename is %s." % __filename__,
            action="append",
            default=None,
        )
