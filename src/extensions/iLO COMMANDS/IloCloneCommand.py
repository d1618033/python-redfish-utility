###
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
###

# -*- coding: utf-8 -*-
""" Ilo Clone command for rdmc """

import os
import sys
import json
import time
import urllib
import getpass

from optparse import OptionParser
from collections import (OrderedDict)

import redfish.ris

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError,\
                    InvalidCommandLineErrorOPTS, InvalidFileFormattingError, \
                    InvalidFileInputError, NoContentsFoundForOperationError, \
                    IncompatibleiLOVersionError, FileEncryption

class IloCloneCommand(RdmcCommandBase):
    """ Clone iLO config of currently logged in server and copy it to another """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='iloclone',\
            usage='iloclone [OPTIONS]\n\n\tCreate a clone file from the ' \
                'current logged in server.\n\texample: iloclone save -f  ' \
                'clone_file_to_save.json\n\n\tLoad the saved clone file ' \
                'to currently logged in server.\n\texample: iloclone load' \
                ' -f clone_file_to_load.json\n\n\tNOTE: This command is ' \
                'only available in local mode.\n\t      During clone load,'\
                ' login using an ilo account with full privileges (such as '\
                'the Administrator account) to ensure all items are cloned '\
                'successfully.',\
            summary='Clone the iLO config of the currently logged in server ' \
                'and copy it to the server in the arguments.',\
            aliases=['iloclone'],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.selobj = rdmcObj.commandsDict["SelectCommand"](rdmcObj)
        self.logobj = rdmcObj.commandsDict["LogoutCommand"](rdmcObj)
        self.loginobj = rdmcObj.commandsDict["LoginCommand"](rdmcObj)
        self.rebootobj = rdmcObj.commandsDict["RebootCommand"](rdmcObj)

    def run(self, line, testing=False):
        """ Main iLO clone function

        :param line: string of arguments passed in
        :type line: str.
        :param testing: flag for automatic testing
        :type testing: bool
        """
        try:
            (options, args) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.clonevalidation(options)

        isredfish = self._rdmc.app.current_client.monolith.is_redfish
        hrefstring = self._rdmc.app.current_client.monolith._hrefstring
        typestring = self._rdmc.app.current_client.monolith._typestring

        if not self.typepath.flagiften:
            raise IncompatibleiLOVersionError("iloclone command is only " \
                                                "available on iLO5 systems.")

        if len(args) == 2:
            myfile = args[1]
        else:
            myfile = options.filename

        if 'save' in args:
            clone = self.gather_clone_items(isredfish, hrefstring, typestring, \
                                                    options, testing=testing)
            self.save_clone(clone, myfile, options)
        elif 'load' in args:
            del args[args.index('load')]

            while True:
                if not testing:
                    ans = raw_input("Are you sure you would like to continue? "\
                                "All user settings will be erased. (y/n)")
                else:
                    break

                if ans.lower() == 'y':
                    break
                elif ans.lower() == 'n':
                    sys.stdout.write("Stopping command without resetting to "\
                                     "factory default settings.\n")
                    return ReturnCodes.SUCCESS

            self.apply_clone(myfile, options, testing=testing)
        else:
            raise InvalidCommandLineError("Please use save argument for saving"\
                                          " a clone file or load argument for "\
                                          "loading a clone file onto a server.")

        return ReturnCodes.SUCCESS

    def gather_clone_items(self, isredfish, href, typestring, options, testing):
        """ gathers the data necessary to produce clone

        :param isredfish: flag to indicate if iLO is using redfish API
        :type redfish: bool
        :param href: the key identifying hypertext reference string
        :type href: str
        :param typestring: the key identifying type
        :type typestring: str
        :param options: command line options
        :type options: list.
        :param testing: flag for automatic testing
        :type: bool
        """
        clone = []

        #Select items needed
        if isredfish:
            selects = ['ManagerAccountCollection.', 'AccountService.P',
                       self.typepath.defs.hpilolicensecollectiontype,
                       'EthernetInterface.P',
                       'Manager.P',
                       self.typepath.defs.hpilodatetimetype+'P',
                       self.typepath.defs.snmpservice+'P',
                       self.typepath.defs.hpilofederationgrouptypecoll,
                       self.typepath.defs.hpilossotype+'P',
                       self.typepath.defs.hpeskmtype+'P',
                       'ComputerSystem.P', 'Power.P',
                       self.typepath.defs.biostype+'P',
                       'HpeServerBootSettings.P',
                       self.typepath.defs.hpsecureboot+'P',
                       self.typepath.defs.managernetworkservicetype+'P']

        self.selobj.run(self.typepath.defs.resourcedirectorytype)

        for item in self._rdmc.app.current_client.monolith.types:
            if self.typepath.defs.resourcedirectorytype in item:
                respobj = self._rdmc.app.current_client.monolith.types[item]\
                    ['Instances'][0].resp.obj
                break

        if respobj:
            sys.stdout.write("Gathering data required for clone. This may "\
                             "take a while...\nYou may be prompted to enter "\
                             "some information to complete the clone file.\n")

            #Regular Patch/Post
            for item in selects:
                if item[-1] == 'P':
                    item = item[0:-1]
                    method = 'PATCH'
                else:
                    method = 'POST'

                for resource in respobj['Instances']:
                    if typestring in resource.iterkeys() and item in \
                                                        resource[typestring]:
                        path = resource[href]

                        try:
                            if item == self.typepath.defs.biostype \
                                            or item == 'HpeServerBootSettings.':
                                if not path.lower().endswith('/settings/'):
                                    continue
                            elif self.typepath.defs.hpilossotype in \
                                                            resource[typestring]:
                                self.configure_sso(clone, path, options)

                            data = self._rdmc.app.get_handler(path, \
                                                               silent=True).dict

                            if data and method.lower() == 'patch':
                                data = self.patch_helper(data, options.uniqueoverride)

                                if item == 'EthernetInterface.':
                                    if '/systems/' in path.lower():
                                        continue

                                    data = self.patch_ei(data)
                                elif item == self.typepath.defs.hpeskmtype:
                                    data = self.patch_eskm(data)
                                elif item == 'ComputerSystem.':
                                    if "Boot" in data:
                                        del data["Boot"]

                                    if "IndicatorLED" in data:
                                        del data["IndicatorLED"]

                                if not data:
                                    continue

                            elif data and method.lower() == 'post':
                                data = self.post_helper(data, path, clone, \
                                                                testing=testing)

                            if data:
                                if isinstance(data, list):
                                    clone.append({path: data})
                                else:
                                    clone.append({path: {method: data}})

                        except Exception, excp:
                            raise excp
            #Actions
            for resource in respobj['Instances']:
                if typestring in resource.iterkeys():
                    path = resource[href]

                    if 'Manager.' in resource[typestring] and not testing:
                        try:
                            self.post_factory_defaults(clone, path)
                            self.reset_ilo(clone, path)
                        except NoContentsFoundForOperationError:
                            raise NoContentsFoundForOperationError(\
                                                    "%s in unavailable." % path)
                    elif 'HpeHttpsCert.' in resource[typestring] and \
                                                            options.httpscert:
                        self.post_https_cert(clone, path, options)

        else:
            raise NoContentsFoundForOperationError("No resource directory " \
                                                                    "found.")

        return clone

    def apply_clone(self, myfile, options, testing):
        """Load the clone into the server

         :param myfile: file containing the saved ilo config
         :type myfile: ilo config file
         :param options: file containing the saved ilo config
         :type options: ilo config file
         :param testing: flag for automatic testing
         :type testing: bool
         """
        clone = self.load_clone(myfile, options)
        if self._rdmc.app.current_client.base_url == "blobstore://":
            logininfo = ""
            ping = True
        elif options.url and options.user and options.password:
            logininfo = "%s -u %s -p %s " % (options.url, options.user,\
                                                   options.password)
            ping = False
        else:
            logininfo = ""
            ping= False

        for item in clone:
            #if there is something to apply
            if item:
                for path in item:
                    if item and item[path] and isinstance(item, dict):
                        if isinstance(item[path], list) or 'POST' in \
                                                            item[path].keys():
                            if isinstance(item[path], list):
                                for instance in item[path]:
                                    sys.stdout.write('\nPosting: ' + path + '\n')

                                    try:
                                        self._rdmc.app.post_handler(path, \
                                                            instance["POST"])
                                    except Exception, excp:
                                        sys.stderr.write('Error.\n')
                                continue

                            try:
                                #continue so we don't reset every time we test
                                if 'resettofactorydefaults' in path.lower():
                                    if ping == False:
                                        continue
                                    try:
                                        sys.stdout.write("Waiting for iLO to " \
                                                            "factory reset...")
                                        self._rdmc.app.post_handler(path,\
                                            item[path]['POST'], service=True, \
                                            silent=True)
                                    except Exception, excp:
                                        sys.stderr.write('Error posting to ' \
                                                            'factory defaults.')
                            except Exception, excp:
                                sys.stderr.write(str(excp) + '\n')

                            if 'resettofactorydefaults' in path.lower():
                                self.logobj.run("")
                                self.timer(minutes=3, ping=ping)
                                self.loginobj.run(logininfo)
                            elif 'manager.reset' in path.lower():
                                sys.stdout.write("Waiting for iLO to reset..." \
                                                                        "\n")

                                self._rdmc.app.post_handler(path,\
                                            item[path]['POST'], service=True, \
                                            silent=True)
                                self.timer(minutes=3, ping=ping)
                                self.loginobj.run(logininfo)
                            else:
                                sys.stdout.write('\nPosting: ' + path + '\n')

                                try:
                                    self._rdmc.app.post_handler(path, \
                                                            item[path]["POST"])
                                except Exception, excp:
                                    sys.stderr.write('Error.\n')

                        elif 'PATCH' in item[path].keys():
                            if isinstance(item[path]['PATCH'], list):
                                for instance in item[path]['PATCH']:
                                    sys.stdout.write('\nPatching: ' + path + \
                                                                        '\n')

                                    try:
                                        self._rdmc.app.patch_handler(path, \
                                                                    instance)
                                    except:
                                        continue
                                continue

                            sys.stdout.write('\nPatching: ' + path + '\n')

                            try:
                                self._rdmc.app.patch_handler(path,\
                                                            item[path]['PATCH'])
                            except:
                                continue

        #reboot the server after everything is completed
        self.logobj.run("")
        self.loginobj.run(logininfo)

        if not testing:
            self.rebootobj.run("")

    def post_helper(self, data, path, clone, testing):
        """ helper to format post data properly

        :param data: body of the post
        :type data: dict
        :param path: path to post
        :type path: str
        :param clone: clone config data
        :type clone: list
        :param testing: flag for automatic testing
        :type testing: bool
        """
        if 'LicenseService' in path:
            data = self.post_license(data, path)
        elif 'AccountService' in path:
            data = self.post_accounts(data, clone, testing=testing)
        elif 'FederationGroups' in path:
            data = self.post_federation(data, clone, testing=testing)

        return data

    def patch_helper(self, body, removeunique):
        """ helper to remove some properties before patching

        :param body: body of the post
        :type body: dict
        :param removeunique: flag to remove unique properties
        :type removeunique: bool.
        """
        removelist = ['actions', 'availableactions', 'status', 'links']

        values = OrderedDict(sorted(body.items(), key=lambda x: x[0]))
        for dictentry in values.keys():
            if dictentry.lower() in removelist:
                del values[dictentry]

        try:
            for dictentry in values['Oem'][self.typepath.defs.oemhp].keys():
                if dictentry.lower() in removelist:
                    del values['Oem'][self.typepath.defs.\
                                      oemhp][dictentry]
        except:
            pass

        values = self._rdmc.app.remove_readonly(values, removeunique)

        try:
            #special power case
            if values['Oem'][self.typepath.defs.oemhp]\
                            ['SNMPPowerThresholdAlert']['ThresholdWatts'] < 74:
                del values['Oem'][self.typepath.defs.oemhp]\
                                ['SNMPPowerThresholdAlert']['ThresholdWatts']
        # fix any extra caveats here
        except:
            pass

        return values

    def patch_eskm(self, values):
        """ helper for patching eskm

        :param values: dictionary with eskm values
        :type values: dict
        """
        eskmfound = False
        removelist = []

        if 'KeyManagerConfig' in values:

            if 'ESKMLocalCACertificateName' in values['KeyManagerConfig'] and \
                    values['KeyManagerConfig']['ESKMLocalCACertificateName']:
                eskmfound = True

            if 'AccountGroup' in values['KeyManagerConfig'] and \
                                values['KeyManagerConfig']['AccountGroup']:
                eskmfound = True

            if eskmfound:
                loginname = raw_input("Please input ESKM LoginName"\
                        " (leave blank if ESKM is not being used):\n")
                password = raw_input("Please input ESKM Password"\
                        " (leave blank if ESKM is not being used):\n")

                if loginname and password:
                    values['KeyManagerConfig']['LoginName'] = loginname
                    values['KeyManagerConfig']['Password'] = password
                    eskmfound = True
                else:
                    eskmfound = False

        if not eskmfound:
            del values['KeyManagerConfig']

        for value in values.keys():
            if not values[value]:
                removelist.append(value)

        if 'PrimaryKeyServerAddress' in removelist and \
                                    'SecondaryKeyServerAddress' in removelist:
            if 'KeyServerRedundancyReq' in values.keys():
                removelist.append('KeyServerRedundancyReq')

        for item in removelist:
            del values[item]

        return values

    def patch_ei(self, data):
        """ helper for patching EthernetInterfaces

        :param data: dictionary with ethernet interface values
        :type data: dict
        """
        dhcpsettingsv4 = data['Oem'][self.typepath.defs.oemhp]["DHCPv4"]
        v4vals = data['Oem'][self.typepath.defs.oemhp]['IPv4']

        try:
            dhcpsettingsv6 = data['Oem'][self.typepath.defs.oemhp]["DHCPv6"]
            v6vals = data['Oem'][self.typepath.defs.oemhp]['IPv6']
        except:
            dhcpsettingsv6 = None

        if dhcpsettingsv4['UseDomainName'] or dhcpsettingsv6 and \
                                            dhcpsettingsv6['UseDomainName']:
            del data['Oem'][self.typepath.defs.oemhp]['DomainName']

        if dhcpsettingsv4['UseDNSServers']:
            del v4vals['DNSServers']

        if dhcpsettingsv6 and dhcpsettingsv6['UseDNSServers']:
            del v6vals['DNSServers']

        if dhcpsettingsv4['UseWINSServers']:
            del v4vals['WINSServers']

        if data['AutoNeg'] or data['AutoNeg'] is None:
            del data['FullDuplex']
            del data['SpeedMbps']

        if 'FrameSize' in data.keys():
            del data['FrameSize']

        del data['MACAddress']
        del data['IPv4Addresses']
        del v4vals['StaticRoutes']

        if dhcpsettingsv6:
            del data['IPv6StaticAddresses']

        return data

    def post_https_cert(self, clone, path, options):
        """ post https certificate

        :param clone: clone config data
        :type clone: list
        :param path: path to post
        :type path: str
        :param options: command options
        :type options: list
        """
        resp = self._rdmc.app.get_handler(path, silent=True)

        filehnd = options.httpscert

        try:
            with open(filehnd) as certfile:
                certdata = certfile.read()
                certfile.close()
        except:
            return

        if resp:
            resp = resp.dict

            for item in resp['Actions']:
                if 'ImportCertificate' in item:
                    action = item.split('#')[-1]
                    path = resp['Actions'][item]['target']
                    break

            body = {path: {'POST': {"Action": action, "Certificate": certdata}}}

        if 'manager.reset' in str(clone[-1]).lower():
            clone.insert(clone.index(clone[-1]), body)
        else:
            clone.append(body)

    def post_factory_defaults(self, clone, path):
        """ post factory default settings

        :param clone: clone config data
        :type clone: list
        :param path: path to post
        :type path: str
        """
        resp = self._rdmc.app.get_handler(path, silent=True)

        if resp:
            path = resp.dict['Oem'][self.typepath.defs.oemhp]['Actions']\
            ['#HpeiLO.ResetToFactoryDefaults']['target']
            body = {path: {'POST': {'Action': 'HpeiLO.ResetToFactoryDefaults', \
                                                    'ResetType': 'Default'}}}
            clone.insert(0, body)
        else:
            raise NoContentsFoundForOperationError

    def post_license(self, clone, path):
        """ helper to format license posts

        :param clone: clone config data
        :type clone: list
        :param path: path to post
        :type path: str
        """
        resp = self._rdmc.app.get_handler(path+'1/', silent=True)

        if resp:
            try:
                key = resp.dict['ConfirmationRequest']['EON']['LicenseKey']
            except:
                key = resp.dict['LicenseKey']

        data = []

        if not key:
            data = {}
        else:
            data.append({"POST":{"LicenseKey": key}})

        return data

    def post_accounts(self, accounts, clone, testing):
        """ helper to format account posts

        :param accounts: accounts present in the server
        :type accounts: dict
        :param clone: clone config data
        :type clone: list
        :param testing: flag for automatic testing
        :type testing: bool
        """

        typestr = self._rdmc.app.current_client.monolith._hrefstring
        newaccounts = {'Members': []}
        data = []

        for account in accounts[self.typepath.defs.collectionstring]:
            account = self._rdmc.app.get_handler(account[typestr], \
                                                            silent=True).dict
            newaccounts['Members'].append(account)

        accounts = newaccounts

        for account in accounts[self.typepath.defs.collectionstring]:
            loginname = account['Oem'][self.typepath.defs.oemhp]['LoginName']
            privileges = account['Oem'][self.typepath.defs.oemhp]['Privileges']
            username = account['UserName']

            if not testing:
                sys.stdout.write("Please input the password for user, %s:" \
                                                                "\n" % username)
                password = getpass.getpass()

                if password and password != '\r':
                    password = password
            else:
                password = 'password'

            if loginname == 'Administrator':
                path = account['@odata.id']

                if path[-1] == '/':
                    path = path[:-2] + '1/'
                else:
                    path = path[:-1] + '1'

                clone.append({path:{"PATCH": {"UserName": username, \
                                              "Password": password, \
                                              "Oem":{self.typepath.defs.oemhp: \
                                                 {"Privileges": privileges}}}}})
                continue
            data.append({"POST":{"UserName": username, "Password": password, \
                                 "Oem":{self.typepath.defs.oemhp:{"LoginName":\
                                      loginname, "Privileges": privileges}}}})

        return data

    def post_federation(self, data, clone, testing):
        """ helper to format federation posts

        :param data: body of the post
        :type data: dict
        :param clone: clone config data
        :type clone: list
        :param testing: flag for automatic testing
        :type testing: bool
        """
        typestr = self._rdmc.app.current_client.monolith._hrefstring
        federations = []

        if 'Members' in data:
            members = data['Members']
        else:
            return None

        for item in members:
            fed = self._rdmc.app.get_handler(item[typestr], silent=True).dict

            if not testing:
                sys.stdout.write("Please input the key for federation, %s:\n" \
                                                                % fed["Name"])
                key = getpass.getpass()

                if key and key != '\r':
                    key = key
            else:
                key = 'testkeys'

            if fed["Name"] == 'DEFAULT':
                path = fed['@odata.id']
                priv = fed["Privileges"]
                clone.append({path:{"PATCH": {"Key": key, "Privileges": priv}}})
                continue

            fed = {"POST":{"Name": fed["Name"], "Key": key, \
                                            "Privileges": fed["Privileges"]}}
            federations.append(fed)

        data = federations
        return data

    def reset_ilo(self, clone, path):
        """ post reset ilo

        :param clone: clone config data
        :type clone: list
        :param path: path to post
        :type path: str
        """
        resp = self._rdmc.app.get_handler(path, silent=True)

        if resp:
            path = resp.dict['Actions']['#Manager.Reset']['target']
            body = {"Action": "Manager.Reset"}
            clone.append({path: {'POST': body}})
        else:
            raise NoContentsFoundForOperationError

    def configure_sso(self, clone, path, options):
        """ import dns and certificate

        :param clone: clone config data
        :type clone: list
        :param path: path to post
        :type path: str
        :param options: command line options
        :type options: list.
        """
        dnslist = []
        body = None
        certbody = None
        resp = self._rdmc.app.get_handler(path, silent=True)

        if resp:
            resp = resp.dict

            for action in resp['Actions']:
                if 'ImportDNSName' in action:
                    dnspath = resp['Actions'][action]['target']
                elif 'ImportCertificate' in action:
                    certpath = resp['Actions'][action]['target']

            if 'ManagerTrustedCertificates' in resp:
                for dns in resp['ManagerTrustedCertificates']:
                    dnslist.append(dns['ServerName'])

        if len(dnslist) > 1:
            body = []
            for dns in dnslist:
                body.append({'POST': {"DNSName": dns}})
        elif dnslist:
            body = {'POST': {"DNSName": dnslist[0]}}

        if body:
            clone.append({dnspath: body})

        if options.ssocert:
            cert = None

            try:
                cert = open(options.ssocert, 'r')

                if cert:
                    certtext = cert.read()
                    cert.close()

                if certtext:
                    certbody = {'POST': {"Action": \
                                 "HpeiLOSSO.ImportCertificate", \
                                 "CertType": "DirectImportCert", \
                                 "CertInput": certtext}}
            except:
                pass

            try:
                if not certbody:
                    urllib.urlopen(options.ssocert).close()
                    certbody = {'POST': {"Action": "ImportCertificate", \
                                "CertType": "ImportCertUri", \
                                "CertInput": options.ssocert}}
            except:
                pass

            if not certbody:
                sys.stderr.write('SSO cert option is not valid file or URI\n')
            else:
                clone.append({certpath: certbody})

    def save_clone(self, clone, filename, options):
        """ save the clone file

        :param clone: filename to save the clone config data
        :type clone: list
        :param filename: filename containing the clone config data
        :type filename: str
        :param options: command line options
        :type options: list.
        """
        if not filename:
            filename = 'clone.json'

        if options.encryption:
            outfile = open(filename, 'wb')
            outfile.write(FileEncryption().encrypt_file(json.dumps(clone, \
                                separators=(',', ':'), \
                                cls=redfish.ris.JSONEncoder),\
                                options.encryption))
        else:
            outfile = open(filename, 'w')
            #compact
            outfile.write(json.dumps(clone, separators=(',', ':'), \
                                                    cls=redfish.ris.JSONEncoder))

            #human-readable
            #outfile.write(json.dumps(clone, indent=2, cls=redfish.ris.JSONEncoder))
        outfile.close()

        sys.stdout.write("Configuration saved to: %s\n" % filename)

    def load_clone(self, filename, options):
        """ load the clone file onto the server

        :param filename: filename containing the clone config data
        :type filename: str
        :param options: command line options
        :type options: list.
        """
        loadcontents = None

        if not filename:
            filename = 'clone.json'

        if not os.path.isfile(filename):
            raise InvalidFileInputError("File '%s' doesn't exist. Please " \
                            "create file by running save command." % file)
        if options.encryption:
            with open(filename, "rb") as myfile:
                data = myfile.read()
                data = FileEncryption().decrypt_file(data, \
                                                    options.encryption)
        else:
            myfile = open(filename, 'r')
            data = myfile.read()

        myfile.close()

        try:
            loadcontents = json.loads(data)
        except:
            raise InvalidFileFormattingError("Invalid file formatting " \
                                                "found in file %s" % file)

        return loadcontents

    def timer(self, minutes=1, ping=False):
        """ helper that waits a certain number of minutes before returning or
        pings a server until service is restored (ping only available in local)

        :param minutes: time in minutes
        :type minutes: int
        :param ping: value indicating if ping or timer function
        :type ping: bool
        """
        if ping:
            results = None
            timeout = 0

            while True:
                if not results:
                    try:
                        if timeout == 0:
                            time.sleep(10)

                        self._rdmc.app.login(is_redfish=True)
                        results = self._rdmc.app.get_handler(self.typepath.\
                                                    defs.startpath, silent=True)

                        timeout = 0
                        self._rdmc.app.logout()
                    except:
                        self._rdmc.app.logout()
                        time.sleep(5)
                        timeout += 1
                else:
                    try:
                        if timeout == 0:
                            time.sleep(10)

                        self._rdmc.app.login(is_redfish=True)
                        self._rdmc.app.select(self.typepath.defs.biostype)
                        time.sleep(10)
                        self._rdmc.app.logout()
                        return
                    except:
                        self._rdmc.app.logout()
                        time.sleep(5)
                        timeout += 1

                if timeout >= 60:
                    raise NoContentsFoundForOperationError("Unable to connect" \
                                                                    " to iLO.")
        else:
            for minute in range(minutes):
                if minute + 1 == minutes:
                    sys.stdout.write("1 minute remaining...\n")
                else:
                    sys.stdout.write("%s minutes remaining...\n" \
                                                        % str(minutes-minute))

                time.sleep(60)

    def clonevalidation(self, options):
        """ results method validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        inputline = list()

        try:
            client = self._rdmc.app.get_current_client()
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
            self.loginobj.loginfunction(inputline)
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
            '-f',
            '--filename',
            dest='filename',
            help="Use this flag if you wish to use a different"\
            " filename than the default one. The default filename is" \
            " clone.json.",
            default=None,
        )
        customparser.add_option(
            '--ssocert',
            dest='ssocert',
            help="Use this flag during iloclone save if you wish to import a SSO"\
            " certificate to the server to be cloned. Add the sso cert file or "\
            "URL to be used to the working directory before running clone load.",
            default=None,
        )
        customparser.add_option(
            '--httpscert',
            dest='httpscert',
            help="Use this flag during iloclone save if you wish to import a SSO"\
            " certificate to the server to be cloned. Add the https cert file to"\
            " be used to the working directory before running clone load.",
            default=None,
        )
        customparser.add_option(
            '--uniqueitemoverride',
            dest='uniqueoverride',
            action='store_false',
            help="Override the measures stopping the tool from writing "\
            "over items that are system unique.",
            default=True
        )
        customparser.add_option(
            '-e',
            '--encryption',
            dest='encryption',
            help="Optionally include this flag to encrypt/decrypt a file "\
            "using the key provided.",
            default=None
        )
