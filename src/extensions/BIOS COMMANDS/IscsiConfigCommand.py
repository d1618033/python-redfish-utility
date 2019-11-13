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
""" IscsiConfig Command for rdmc """

import re
import sys
import json

from argparse import ArgumentParser

import redfish.ris

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group
from rdmc_helper import ReturnCodes, InvalidCommandLineError, InvalidCommandLineErrorOPTS, \
                NicMissingOrConfigurationError, BootOrderMissingEntriesError, Encryption

class IscsiConfigCommand(RdmcCommandBase):
    """ Changes the iscsi configuration for the server that is currently logged in """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='iscsiconfig',\
            usage='iscsiconfig [ISCSI CONFIGURATION] [OPTIONS]\n\n\tRun without' \
                        ' arguments for available NIC sources for iSCSI' \
                        ' configuration.\n\texample: iscsiconfig\n\n\tDisplay' \
                        ' the current iSCSI configuration:\n\texample: ' \
                        'iscsiconfig --list\n\n\tSaving current iSCSI ' \
                        'configuration to a file:\n\texample: iscsiconfig ' \
                        '--list -f output.txt\n\n\tLoading iSCSI ' \
                        'configurations from a file:\n\texample: iscsiconfig ' \
                        '--modify output.txt\n\n\tIn order to add a NIC ' \
                        'source to an iSCSI boot attempt you must run \n\t"' \
                        'iscsiconfig" without any paramters. This will ' \
                        'display a list of NIC\n\tsources which are currently' \
                        ' present in the system.\n\tAdding an iSCSI boot ' \
                        'attempt:\n\texample: iscsiconfig --add [1]\n\n\tIn ' \
                        'order to delete an iSCSI boot attempt you must run' \
                        '\n\t"iscsiconfig --list" to view the currently ' \
                        'configured attempts.\n\tOnce you find the attempt ' \
                        'you want to delete simply pass the attempt\n\tnumber' \
                        ' to the iSCSI delete function.\n\tDeleting an iSCSI ' \
                        'boot attempt:\n\texample: iscsiconfig --delete 1',\
            summary='Displays and configures the current iscsi settings.',\
            aliases=['iscsiconfig'],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.getobj = rdmcObj.commands_dict["GetCommand"](rdmcObj)
        self.setobj = rdmcObj.commands_dict["SetCommand"](rdmcObj)
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)
        self.rebootobj = rdmcObj.commands_dict["RebootCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)

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

        self.iscsiconfigurationvalidation(options)

        if self.typepath.defs.isgen10:
            iscsipath = self.gencompatpaths(selector="HpeiSCSISoftwareInitiator.", rel=False)
            iscsisettingspath = iscsipath + 'settings'
            bootpath = self.gencompatpaths(selector="HpeServerBootSettings.")
        else:
            if self.typepath.defs.biospath[-1] == '/':
                iscsipath = self.typepath.defs.biospath + 'iScsi/'
                iscsisettingspath = self.typepath.defs.biospath + 'iScsi/settings/'
                bootpath = self.typepath.defs.biospath + 'Boot/'
            else:
                iscsipath = self.typepath.defs.biospath + '/iScsi'
                iscsisettingspath = self.typepath.defs.biospath + '/iScsi/settings'
                bootpath = self.typepath.defs.biospath + '/Boot'

        if options.list:
            self.listoptionhelper(options, iscsipath, iscsisettingspath, bootpath)
        elif options.modify:
            self.modifyoptionhelper(options, iscsisettingspath)
        elif options.add:
            self.addoptionhelper(options, iscsipath, iscsisettingspath, bootpath)
        elif options.delete:
            self.deleteoptionhelper(options, iscsisettingspath)
        elif not args:
            self.defaultsoptionhelper(options, iscsipath, bootpath)
        else:
            if len(args) < 2:
                self.iscsiconfigurationvalidation(options)
            else:
                raise InvalidCommandLineError("Invalid number of parameters. " \
                        "Iscsi configuration takes a maximum of 1 parameter.")

        if options.reboot:
            self.rebootobj.run(options.reboot)

        #Return code
        return ReturnCodes.SUCCESS

    def gencompatpaths(self, selector=None, rel=False):
        """Helper function for finding gen compatible paths

        :param selector: the type selection for the get operation
        :type selector: str.
        :param rel: flag to tell select function to reload selected instance
        :type rel: boolean.
        :returns: returns urls
        """

        # TODO: gen9 bool check.
        # Don't think it's grabbing a path
        self._rdmc.app.select(selector=selector, rel=rel)
        props = self._rdmc.app.getprops(skipnonsetting=False)
        for prop in props:
            name = prop.get('Name')
            if 'current' in name.lower():
                try:
                    path = prop.get('@odata.id')
                except:
                    sys.stdout.write('ERROR: URI path could not be found.')
        return path

    def addoptionhelper(self, options, iscsipath, iscsisettingspath, bootpath):
        """ Helper function to add option for iscsi

        :param options: command line options
        :type options: list.
        :param iscsipath: current iscsi path
        :type iscsipath: str.
        :param iscsisettingspath: current iscsi settings path
        :type iscsisettingspath: str.
        :param bootpath: current boot path
        :type bootpath: str.
        """
        devicealloc = list()
        self.selobj.selectfunction("HpBiosMapping.")
        pcisettingsmap = next(iter(self.getobj.getworkerfunction(\
                        "BiosPciSettingsMappings", options, results=True, uselist=True)), None)

        for item in pcisettingsmap["BiosPciSettingsMappings"]:
            if "Associations" in item:
                if "EmbNicEnable" in item["Associations"] or "EmbNicConfig" in item["Associations"]:
                    _ = [devicealloc.append(x) for x in item["Subinstances"]]

                for assoc in item["Associations"]:
                    if re.match("FlexLom[0-9]Enable", str(assoc)) or \
                                    re.match("PciSlot[0-9]Enable", str(assoc)):
                        _ = [devicealloc.append(x) for x in item["Subinstances"]]

        self.selobj.selectfunction("HpiSCSISoftwareInitiator.")
        self.validateinput(deviceallocsize=len(devicealloc), options=options)

        foundlocation = False
        iscsibootsources = self.rawdatahandler(action="GET", silent=True, \
                           jsonflag=True, path=iscsisettingspath)

        count = 0
        attemptinstancenumber = self.bootattemptcounter(iscsibootsources\
                                            [self.typepath.defs.iscsisource])
        self.pcidevicehelper(devicealloc, iscsipath, bootpath, options=options)

        for item in iscsibootsources[self.typepath.defs.iscsisource]:
            try:
                if not item[self.typepath.defs.iscsiattemptinstance]:
                    nicsourcedata = devicealloc[int(options.add[1:-1])-1]["Associations"]

                    iscsibootsources[self.typepath.defs.iscsisource][count]\
                    ["iSCSINicSource"] = nicsourcedata[1] if \
                        isinstance(nicsourcedata[0], dict) else nicsourcedata[0]

                    iscsibootsources[self.typepath.defs.iscsisource][count]\
                            [self.typepath.defs.iscsiattemptinstance] = attemptinstancenumber
                    iscsibootsources[self.typepath.defs.iscsisource][count]\
                        [self.typepath.defs.iscsiattemptname] = str(attemptinstancenumber)
                    foundlocation = True
                    break
            except Exception:
                raise NicMissingOrConfigurationError("Invalid input value for configuring NIC.")
            count += 1

        if foundlocation:
            self._rdmc.app.patch_handler(iscsisettingspath, iscsibootsources, \
                                         optionalpassword=options.biospassword)
        else:
            raise NicMissingOrConfigurationError("Failed to add NIC. All NICs" \
                                             " have already been configured.")

    def bootattemptcounter(self, bootsources):
        """ Helper function to count the current boot entries for iscsi

        :param bootsources: current iscsi boot sources
        :type bootsources: list.
        """
        size = 0
        count = list()

        for item in bootsources:
            size += 1

            if item[self.typepath.defs.iscsiattemptinstance]:
                count.append(int(item[self.typepath.defs.iscsiattemptinstance]))

        if size == len(count):
            raise NicMissingOrConfigurationError("Failed to add NIC. All " \
                                          "NICs have already been configured.")

        count.sort(key=None, reverse=False)

        if len(count) > 0:
            iterate = 0

            for i in range(1, size+1, 1):
                if iterate < len(count) and i == count[iterate]:
                    iterate += 1
                else:
                    return iterate+1
        else:
            return int(1)

    def deleteoptionhelper(self, options, iscsisettingspath):
        """ Helper function to delete option for iscsi

        :param options: command line options
        :type options: list.
        :param iscsisettingspath: current iscsi settings path
        :type iscsisettingspath: string.
        """
        patch = None

        self.selobj.selectfunction("HpBaseConfigs.")
        contents = self._rdmc.app.getprops(selector="BaseConfigs")

        for content in contents:
            for key in content["BaseConfigs"][0]["default"]:
                if key == self.typepath.defs.iscsisource:
                    patch = content["BaseConfigs"][0]["default"][key]

        if not patch:
            raise NicMissingOrConfigurationError("Could not access Base Configurations.")

        self.validateinput(options=options, deleteoption=True)

        foundlocation = False
        iscsibootsources = self.rawdatahandler(action="GET", silent=True, \
                        jsonflag=False, path=iscsisettingspath)
        holdetag = iscsibootsources.getheader('etag')
        iscsibootsources = json.loads(iscsibootsources.read)

        try:
            count = 0
            for item in iscsibootsources[self.typepath.defs.iscsisource]:
                if item[self.typepath.defs.iscsiattemptinstance] == int(options.delete):
                    iscsibootsources[self.typepath.defs.iscsisource][count] = patch[count]
                    foundlocation = True

                count += 1
        except Exception:
            raise NicMissingOrConfigurationError("The NIC targeted for delete"\
                                        " does not exist. The request for " \
                                        "delete could not be completed.")

        if foundlocation:
            self._rdmc.app.put_handler(iscsisettingspath, iscsibootsources, \
                                        optionalpassword=options.biospassword, \
                                        headers={'if-Match':holdetag})
            self._rdmc.app.get_handler(iscsisettingspath, silent=True)
        else:
            raise NicMissingOrConfigurationError("The given attempt instance does not exist.")

    def listoptionhelper(self, options, iscsipath, iscsisettingspath, bootpath):
        """ Helper function to list options for iscsi

        :param options: command line options
        :type options: list.
        :param iscsipath: current iscsi path
        :type iscsipath: str.
        :param iscsisettingspath: current iscsi settings path
        :type iscsisettingspath: str.
        :param bootpath: current boot path
        :type bootpath: str.
        """
        self.selobj.selectfunction("HpBiosMapping.")
        pcisettingsmap = next(iter(self.getobj.getworkerfunction(\
                                    "BiosPciSettingsMappings", options, \
                                    results=True, uselist=True)), None)

        devicealloc = list()
        for item in pcisettingsmap["BiosPciSettingsMappings"]:
            if "Associations" in item:
                if "EmbNicEnable" in item["Associations"] or "EmbNicConfig" in item["Associations"]:
                    _ = [devicealloc.append(x) for x in item["Subinstances"]]

                for assoc in item["Associations"]:
                    if re.match("FlexLom[0-9]Enable", str(assoc)) or \
                                    re.match("PciSlot[0-9]Enable", str(assoc)):
                        _ = [devicealloc.append(x) for x in item["Subinstances"]]

        if self.typepath.defs.isgen10:
            newpcilist = []

            self.selobj.selectfunction("HpeServerPciDeviceCollection")
            pcideviceslist = next(iter(self.getobj.getworkerfunction("Members", options, \
                                   results=True, uselist=False)), None)

            for device in pcideviceslist["Members"]:
                newpcilist.append(self._rdmc.app.get_handler(device['@odata.id'], silent=True).dict)

            pcideviceslist = newpcilist
        else:
            self.selobj.selectfunction(["Collection."])
            pcideviceslist = next(iter(self.getobj.getworkerfunction("Items", options, \
                            results=True, uselist=False, filtervals=("MemberType", \
                                                        "HpServerPciDevice.*"))), None)["Items"]

        self.selobj.selectfunction("HpiSCSISoftwareInitiator.")
        iscsibootsources = self.rawdatahandler(action="GET", silent=True, \
                        jsonflag=True, path=iscsisettingspath)
        structeredlist = list()

        self.pcidevicehelper(devicealloc, iscsipath, bootpath, pcideviceslist)

        for item in iscsibootsources[self.typepath.defs.iscsisource]:
            if item["iSCSINicSource"]:
                for device in devicealloc:
                    listval = 1 if isinstance(device["Associations"][0], dict) else 0
                    if item["iSCSINicSource"] == device["Associations"][listval]:
                        for pcidevice in pcideviceslist:
                            if device["CorrelatableID"] == pcidevice["UEFIDevicePath"]:
                                inputstring = pcidevice["DeviceType"] + " " + \
                                            str(pcidevice["DeviceInstance"]) + " Port " + \
                                            str(pcidevice["DeviceSubInstance"])\
                                            + " : " + pcidevice["Name"]
                                structeredlist.append({inputstring: \
                                   {str("Attempt " + \
                                    str(item[self.typepath.defs.iscsiattemptinstance])): item}})
            else:
                structeredlist.append({"Not Added": {}})
        try:
            if iscsibootsources is None:
                raise BootOrderMissingEntriesError('No entries found for iscsi boot sources.\n\n')
            elif not options.filename:
                self.print_iscsi_config_helper(structeredlist, "Current iSCSI Attempts: \n")
        except Exception as excp:
            raise excp

        if structeredlist is None:
            sys.stderr.write('No entries found for iscsi boot sources.\n\n')
        elif options.filename:
            output = json.dumps(structeredlist, indent=2, cls=redfish.ris.JSONEncoder, \
                                                                                    sort_keys=True)
            filehndl = open(options.filename[0], "w")
            filehndl.write(output)
            filehndl.close()

            sys.stdout.write("Results written out to '%s'\n" % options.filename[0])

    def defaultsoptionhelper(self, options, iscsipath, bootpath):
        """ Helper function for default options for iscsi

        :param options: command line options
        :type options: list.
        :param iscsipath: current iscsi path
        :type iscsipath: str.
        :param bootpath: current boot path
        :type bootpath: str.
        """
        self.selobj.selectfunction("HpBiosMapping.")
        pcisettingsmap = next(iter(self.getobj.getworkerfunction(\
                                    "BiosPciSettingsMappings", options, \
                        results=True, uselist=True)), None)

        devicealloc = list()
        for item in pcisettingsmap["BiosPciSettingsMappings"]:
            if "Associations" in item:
                if "EmbNicEnable" in item["Associations"] or "EmbNicConfig" in item["Associations"]:
                    _ = [devicealloc.append(x) for x in item["Subinstances"]]

                for assoc in item["Associations"]:
                    if re.match("FlexLom[0-9]Enable", str(assoc)) or \
                                    re.match("PciSlot[0-9]Enable", str(assoc)):
                        _ = [devicealloc.append(x) for x in item["Subinstances"]]

        if self.typepath.defs.isgen10:
            newpcilist = []
            self.selobj.selectfunction("HpeServerPciDeviceCollection")
            pcideviceslist = next(iter(self.getobj.getworkerfunction("Members", options, \
                                        results=True, uselist=False)), None)
            for device in pcideviceslist["Members"]:
                newpcilist.append(self._rdmc.app.get_handler(\
                                         device['@odata.id'], silent=True).dict)
            pcideviceslist = newpcilist
        else:
            self.selobj.selectfunction(["Collection."])
            pcideviceslist = next(iter(self.getobj.getworkerfunction("Items", options, \
                            results=True, uselist=False, filtervals=("MemberType", \
                                                        "HpServerPciDevice.*"))), None)["Items"]

        self.selobj.selectfunction(\
                               self.typepath.defs.hpiscsisoftwareinitiatortype)
        iscsiinitiatorname = next(iter(self.getobj.getworkerfunction(\
                                        "iSCSIInitiatorName", options, \
                            results=True, uselist=True)), None)

        disabledlist = self.pcidevicehelper(devicealloc, iscsipath, bootpath, pcideviceslist)

        self.print_out_iscsi_configuration(iscsiinitiatorname, devicealloc, pcideviceslist)

        if disabledlist:
            self.print_out_iscsi_configuration(iscsiinitiatorname, \
                                    disabledlist, pcideviceslist, disabled=True)

    def modifyoptionhelper(self, options, iscsisettingspath):
        """ Helper function to modify options for iscsi

        :param options: command line options
        :type options: list.
        :param iscsisettingspath: current iscsi settings path
        :type iscsisettingspath: str.
        """
        try:
            inputfile = open(options.modify, 'r')
            contentsholder = json.loads(inputfile.read())
        except Exception as excp:
            raise InvalidCommandLineError("%s" % excp)

        iscsibootsources = self.rawdatahandler(action="GET", silent=True, \
                           jsonflag=True, path=iscsisettingspath)

        count = 0
        resultsdict = list()

        for item in contentsholder:
            for entry in item.values():
                enteredsection = False

                for key, value in entry.items():
                    enteredsection = True
                    resultsdict.append(self.modifyfunctionhelper(key, value, \
                             iscsibootsources[self.typepath.defs.iscsisource]))

                if not enteredsection:
                    resultsdict.append(iscsibootsources[self.typepath.defs.iscsisource][count])

                count += 1

        contentsholder = {self.typepath.defs.iscsisource: resultsdict}

        self._rdmc.app.patch_handler(iscsisettingspath, contentsholder, \
                                        optionalpassword=options.biospassword)
        self._rdmc.app.get_handler(iscsisettingspath, silent=True)

    def modifyfunctionhelper(self, key, value, bootsources):
        """ Helper function to modify the entries for iscsi

        :param key: key to be used for attempt
        :type key: string.
        :param value: value to apply to attempt
        :type value: str.
        :param bootsources: current boot sources
        :type bootsources: list.
        """
        foundoption = False

        for bootsource in bootsources:
            if bootsource[self.typepath.defs.iscsiattemptinstance] == int(key[-1:]):
                foundoption = True
                break

        if foundoption:
            return value

    def pcidevicehelper(self, devicealloc, iscsipath, bootpath, pcideviceslist=None, options=None):
        """ Helper function to check for extra pci devices / identify disabled devices

        :param devicealloc: list of devices allocated
        :type devicealloc: list.
        :param iscsipath: current iscsi path
        :type iscsipath: str.
        :param bootpath: current boot path
        :type bootpath: str.
        :param pcideviceslist: current pci device list
        :type pcideviceslist: list.
        :param options: command line options
        :type options: list.
        """
        if not pcideviceslist:
            if self.typepath.defs.isgen10:
                newpcilist = []
                self.selobj.selectfunction("HpeServerPciDeviceCollection")
                pcideviceslist = next(iter(self.getobj.getworkerfunction("Members", \
                               options, results=True, uselist=False)), None)

                for device in pcideviceslist["Members"]:
                    newpcilist.append(self._rdmc.app.get_handler(\
                                         device['@odata.id'], silent=True).dict)

                pcideviceslist = newpcilist
            else:
                self.selobj.selectfunction(["Collection."])
                pcideviceslist = next(iter(self.getobj.getworkerfunction("Items", \
                       options, results=True, uselist=False, filtervals=("MemberType", \
                                                            "HpServerPciDevice.*"))), None)["Items"]
        try:
            self.rawdatahandler(action="GET", silent=True, \
                            jsonflag=True, path=iscsipath)['iSCSINicSources']
        except:
            raise NicMissingOrConfigurationError('No iSCSI nic sources available.')

        _ = [x['UEFIDevicePath'] for x in pcideviceslist]
        removal = list()

        bios = self.rawdatahandler(action="GET", silent=True, jsonflag=True, path=bootpath)

        for item in devicealloc:
            if item['Associations'] and item['Associations'][0] in bios.keys():
                if bios[item['Associations'][0]] == 'Disabled':
                    removal.append(item)

        _ = [devicealloc.remove(x) for x in removal]

        return removal

    def print_out_iscsi_configuration(self, iscsiinitiatorname, devicealloc, \
                                                pcideviceslist, disabled=False):
        """ Convert content to human readable and print out to std.out

        :param iscsiinitiatorname: iscsi initiator name
        :type iscsiinitiatorname: str.
        :param devicealloc: list of devices allocated
        :type devicealloc: list.
        :param pcideviceslist: current pci device list
        :type pcideviceslist: list.
        :param disabled: command line options
        :type disabled: boolean.
        """
        try:
            if iscsiinitiatorname is None:
                BootOrderMissingEntriesError('No entry found for the iscsi initiator name.\n\n')
            elif disabled:
                pass
            else:
                self.print_iscsi_config_helper(\
                                   iscsiinitiatorname["iSCSIInitiatorName"], \
                                                    "\nIscsi Initiator Name: ")
        except Exception as excp:
            raise excp

        try:
            if devicealloc and pcideviceslist:
                if disabled:
                    sys.stdout.write("\nDisabled iSCSI Boot Network Interfaces: \n")
                    count = 'Disabled'
                else:
                    sys.stdout.write("Available iSCSI Boot Network Interfaces: \n")
                    count = 1

                for item in devicealloc:
                    for pcidevice in pcideviceslist:
                        if item["CorrelatableID"] == \
                                                    pcidevice["UEFIDevicePath"]:
                            sys.stdout.write("[%s] %s %s Port %s : %s\n" % \
                                         (count, pcidevice["DeviceType"], \
                                          pcidevice["DeviceInstance"], \
                                          pcidevice["DeviceSubInstance"], pcidevice["Name"]))

                            if not disabled:
                                count += 1
            else:
                raise BootOrderMissingEntriesError('No entries found for' \
                                           ' iscsi configurations devices.\n')
        except Exception as excp:
            raise excp

    def print_iscsi_config_helper(self, content, outstring, indent=0):
        """ Print iscsi configuration helper

        :param content: current content to be output
        :type content: string.
        :param outstring: current output string
        :type outstring: str.
        :param indent: current iscsi settings path
        :type indent: str.
        """
        sys.stdout.write('\t' * indent + outstring)

        if content:
            sys.stdout.write(json.dumps(content, indent=2, cls=redfish.ris.JSONEncoder, \
                                                                                    sort_keys=True))
        else:
            sys.stdout.write('\t' * indent + "No entries currently configured.\n")

        sys.stdout.write('\n\n')

    def rawdatahandler(self, action="None", path=None, silent=True, jsonflag=False):
        """ Helper function to get and put the raw data

        :param action: current rest action
        :type action: list.
        :param path: current path
        :type path: str.
        :param silent: flag to determine silent mode
        :type silent: boolean.
        :param jsonflag: flag to determine json output
        :type jsonflag: boolean.
        """
        if action == "GET":
            rawdata = self._rdmc.app.get_handler(put_path=path, silent=silent)

        if jsonflag is True:
            rawdata = json.loads(rawdata.read)

        return rawdata

    def validateinput(self, deviceallocsize=None, options=None, deleteoption=False):
        """ Helper function to validate that the input is correct

        :param deviceallocsize: current device allocated size
        :type deviceallocsize: str.
        :param options: command line options
        :type options: list.
        :param deleteoption: flag to delete option
        :type deleteoption: boolean.
        """
        if deviceallocsize:
            try:
                if int(options.add[1:-1])-1 >= deviceallocsize:
                    raise NicMissingOrConfigurationError("Please verify the "\
                                     "given input value for configuring NIC.")
            except Exception:
                raise NicMissingOrConfigurationError("Please verify the "\
                                      "given input value for configuring NIC.")
        if deleteoption:
            try:
                if  int(options.delete) == 0:
                    raise NicMissingOrConfigurationError("Invalid input value."\
                             "Please give valid attempt for instance values.")
            except Exception:
                raise NicMissingOrConfigurationError("Invalid input value."\
                             "Please give valid attempt for instance values.")

    def iscsiconfigurationvalidation(self, options):
        """ iscsi configuration method validation function

        :param options: command line options
        :type options: list.
        """
        inputline = list()

        try:
            _ = self._rdmc.app.current_client
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

            self.lobobj.loginfunction(inputline)

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        add_login_arguments_group(customparser)

        customparser.add_argument(
            '-f',
            '--filename',
            dest='filename',
            help="Use this flag if you wish to use a different"\
            " filename than the default one. The default filename is" \
            " ilorest.json.",
            action="append",
            default=None,
        )
        customparser.add_argument(
            '--add',
            dest='add',
            help="Use this iSCSI configuration option to add an iSCSI"\
            " configuration option.",
            default=None,
        )
        customparser.add_argument(
            '--delete',
            dest='delete',
            help="Use this iSCSI configuration option to delete an iSCSI"\
            " configuration option.",
            default=None,
        )
        customparser.add_argument(
            '--modify',
            dest='modify',
            help="Use this iSCSI configuration option to modify an iSCSI"\
            " configuration option.",
            default=None,
        )
        customparser.add_argument(
            '--list',
            dest='list',
            action="store_true",
            help="Use this iSCSI configuration option to list the details"\
            " of the different iSCSI configurations.",
            default=None,
        )
        customparser.add_argument(
            '--biospassword',
            dest='biospassword',
            help="Select this flag to input a BIOS password. Include this"\
            " flag if second-level BIOS authentication is needed for the"\
            " command to execute. This option is only used on Gen 9 systems.",
            default=None,
        )
        customparser.add_argument(
            '--reboot',
            dest='reboot',
            help="Use this flag to perform a reboot command function after"\
            " completion of operations.  For help with parameters and"\
            " descriptions regarding the reboot flag, run help reboot.",
            default=None,
        )
