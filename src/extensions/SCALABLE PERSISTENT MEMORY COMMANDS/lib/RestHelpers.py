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

from jsonpointer import resolve_pointer
from Drives import Drives, Drive
from Regions import Regions
from Health import *
from State import *


class RestHelpers(object):

    def __init__(self, rdmcObject):
        self._rdmc = rdmcObject



    def getResource(self, url):
        resp = self._rdmc.app.get_handler(url, \
                    verbose=self._rdmc.opts.verbose, service=True, silent=True, response=True)

        if resp and resp.status == 200 and resp.dict:
            return resp
        else:
            return None


    def enableConfiguration(self):
        return self.patchBiosSettingAttributes(
            { "ConfigurationEnabled" : "Enabled"}
        )



    def patchBiosSettingAttributes(self, attributes):
        patchData = {"Attributes":{
            # put any required settings here
        }}
        patchData["Attributes"].update(attributes)
        response = self.patchResource("/redfish/v1/Systems/1/bios/Settings/", patchData)
        return response



    def patchScalablePmemSettingAttributes(self, attributes):
        patchData = {"Attributes":{
            # put any required settings here
        }}
        patchData["Attributes"].update(attributes)
        response = self.patchResource("/redfish/v1/Systems/1/bios/HpeScalablePmem/Settings/", patchData)
        return response



    def patchResource(self, url, data):
        resp = self._rdmc.app.patch_handler(url, data, \
                    verbose=self._rdmc.opts.verbose, service=True, silent=True, response=True)

        if resp and resp.status == 200 and resp.dict:
            return resp
        else:
            return None



    def getLinkedResources(self, data, pointer):
        combinedResponses = []

        matchingData = resolve_pointer(data, pointer, None)
        if matchingData:
            for item in matchingData:
                itemUri = item["@odata.id"]

                resp = self._rdmc.app.get_handler(itemUri, \
                    verbose=self._rdmc.opts.verbose, service=True, silent=True)

                if resp and resp.status == 200 and resp.dict:
                    combinedResponses.append(resp.dict)

        return combinedResponses



    def generateRegionConfiguration(self, config, pending_config, current_bios_settings):
        """ Generate a data structure describing the region configuration """
        result = Regions()

        subNumaClusteringSetting = resolve_pointer(current_bios_settings, "/Attributes/SubNumaClustering", "Disabled")
        result.subNumaClusteringEnabled = True if (subNumaClusteringSetting == "Enabled") else False

        maximumOverallPmemGiB = resolve_pointer(config, "/Attributes/TheoreticalPMemMaxGiB", 0)
        result.maxPmemGiB = maximumOverallPmemGiB

        maximumNonNumaRegions = resolve_pointer(config, "/Attributes/MaximumNumberOfSpannedLogicalNvdimmRegions", 0)
        result.maxNonNumaRegions = maximumNonNumaRegions

        maximumNumaRegionsPerDomain = resolve_pointer(config, "/Attributes/MaximumRegionsPerDomain", 0)
        result.maxRegionsPerSocket = maximumNumaRegionsPerDomain

        minRegionSizeGiB = resolve_pointer(config, "/Attributes/MinimumRegionSizeGiB", 1)
        result.minRegionSizeGiB = minRegionSizeGiB

        allocationUnitSizeGiB = resolve_pointer(config, "/Attributes/AllocationUnitSizeGiB", 1)
        result.allocationUnitSizeGiB = allocationUnitSizeGiB

        # populate sockets and non-numa regions
        domainMaximums = resolve_pointer(config, "/Attributes/TheoreticalPmemMaxPerDomainGiB", {})
        for i in range(0, 64):
            domainMax = resolve_pointer(domainMaximums, "/Processor{}".format(i + 1), 0)
            if domainMax > 0:
                # this domain has a max > 0, so add a socket for it
                socket = result.addSocket(i, domainMax)
                for _, region in socket.numaRegions.items():
                    region.currentSizeGiB = resolve_pointer(config,
                                                            "/Attributes/{}".format(region.settingName), 0)
                    region.pendingSizeGiB = resolve_pointer(pending_config,
                                                            "/Attributes/{}".format(region.settingName), 0)

        for _, pair in result.socketPairs.items():
            nonNumaRegion = pair.nonNumaRegion
            nonNumaRegion.currentSizeGiB = resolve_pointer(config,
                                                           "/Attributes/{}".format(nonNumaRegion.settingName), 0)
            nonNumaRegion.pendingSizeGiB = resolve_pointer(pending_config,
                                                           "/Attributes/{}".format(nonNumaRegion.settingName), 0)

        return result



    def generateDriveConfiguration(self, config, current_bios_settings, pending_bios_settings, drives):
        result = []

        for drive in drives:
            new_drive_entry = Drive()
            new_drive_entry.driveType = resolve_pointer(drive, "/MediaType", None)
            new_drive_entry.protocol = resolve_pointer(drive, "/Protocol", None)
            new_drive_entry.model = resolve_pointer(drive, "/Model", None)
            new_drive_entry.sizeBytes = resolve_pointer(drive, "/CapacityBytes", 0)
            new_drive_entry.correlationId = resolve_pointer(drive, "/Oem/Hpe/NVMeId", None)
            new_drive_entry.partNumber = resolve_pointer(drive, "/PartNumber", None)
            new_drive_entry.serialNumber = resolve_pointer(drive, "/SerialNumber", None)
            new_drive_entry.health = resolve_pointer(drive, "/Status/Health", None)
            new_drive_entry.state = resolve_pointer(drive, "/Status/State", None)
            new_drive_entry.failurePredicted = resolve_pointer(drive, "/FailurePredicted", False)
            new_drive_entry.predictedMediaLifeLeftPercent = resolve_pointer(drive, "/PredictedMediaLifeLeftPercent", None)

            for location in resolve_pointer(drive, "/Location", []):
                loc_info = resolve_pointer(location, "/Info", None)
                loc_format = resolve_pointer(location, "/InfoFormat", None)
                if loc_format == "Box:Bay":
                    new_drive_entry.setLoc(loc_info, loc_format)
                    break

            if new_drive_entry.state == State.ABSENT:
                # drive not installed
                continue

            supportedDrives = resolve_pointer(config, "/Attributes/SupportedDrives", [])
            matchingSupportedDrive = next((x for x in supportedDrives if x["NVMeId"] == new_drive_entry.correlationId), None)
            new_drive_entry.config = matchingSupportedDrive
            if matchingSupportedDrive:
                new_drive_entry.isBiosSupported = True
                new_drive_entry.wp = resolve_pointer(matchingSupportedDrive, "/WP", 0)
                new_drive_entry.dw = resolve_pointer(matchingSupportedDrive, "/DW", 0)
                new_drive_entry.settingName = resolve_pointer(matchingSupportedDrive, "/SettingName", None)

            if new_drive_entry.settingName:
                if pending_bios_settings:
                    new_drive_entry.pendingMode = resolve_pointer(pending_bios_settings,
                        "/Attributes/{}".format(new_drive_entry.settingName))

                if current_bios_settings:
                    new_drive_entry.currentMode = resolve_pointer(current_bios_settings,
                        "/Attributes/{}".format(new_drive_entry.settingName))

            result.append(new_drive_entry)

        return Drives(result)



    def getConfigResource(self):
        """ get configuration data
        """
        resp = self.getResource("/redfish/v1/Systems/1/Bios/hpescalablepmem/")

        if resp and resp.status == 200 and resp.dict:
            return resp.dict
        else:
            return None

    def getPendingConfigResource(self):
        """ get configuration data
        """
        resp = self.getResource("/redfish/v1/Systems/1/Bios/hpescalablepmem/settings/")

        if resp and resp.status == 200 and resp.dict:
            return resp.dict
        else:
            return None

    def getCurrentBiosSettings(self):
        """ get current BIOS settings
        """

        resp = self.getResource("/redfish/v1/Systems/1/Bios/")

        if resp and resp.status == 200 and resp.dict:
            return resp.dict
        else:
            return None

    def getPendingBiosSettings(self):
        """ get current BIOS settings
        """

        resp = self.getResource("/redfish/v1/Systems/1/Bios/Settings/")

        if resp and resp.status == 200 and resp.dict:
            return resp.dict
        else:
            return None

    def getChassis(self):
        """ get the Chassis resource
        """

        resp = self.getResource("/redfish/v1/Chassis/1/")

        if resp and resp.status == 200 and resp.dict:
            return resp.dict
        else:
            return None

    def getChassisDrives(self, chassis):
        """ get the linked Drives from the chassis
        """

        if not chassis:
            return None

        resp = self.getLinkedResources(chassis, "/Links/Drives")
        return resp

    def setDrives(self, new_drives=None, old_drives=None):
        attributes = {}

        if old_drives:
            for drive in old_drives:
                attributes[drive.settingName] = Drive.MODE_NVME

        if new_drives:
            for drive in new_drives:
                attributes[drive.settingName] = Drive.MODE_NVDIMM

        return self.patchBiosSettingAttributes(attributes)

    def doesConfigurationRequireStorageInit(self, config):
        return resolve_pointer(config, "/Attributes/Policy/ConfigRequiresStorageInit", False)

    def isStorageInitializeEnabled(self, pending_config):
        return resolve_pointer(pending_config, "/Attributes/StorageInitialize", False)

    def revertSettings(self):
        currentBiosSettings = self.getCurrentBiosSettings();
        pendingBiosSettings = self.getPendingBiosSettings();
        currentConfigResource = self.getConfigResource();
        pendingConfigResource = self.getPendingConfigResource();

        # config resource
        
        config_attributes_to_revert = [
            "FeatureEnabled",
            "ConfigurationRestoration",
            "StorageInitialize",
            "Processor1LogicalNvdimm1SizeGiB",
            "Processor1LogicalNvdimm2SizeGiB",
            "Processor2LogicalNvdimm1SizeGiB",
            "Processor2LogicalNvdimm2SizeGiB",
            "Processor3LogicalNvdimm1SizeGiB",
            "Processor3LogicalNvdimm2SizeGiB",
            "Processor4LogicalNvdimm1SizeGiB",
            "Processor4LogicalNvdimm2SizeGiB",
            "SpannedLogicalNvdimm1SizeGiB",
            "SpannedLogicalNvdimm2SizeGiB"
        ]

        patch_data = { }
        for attribute_name in config_attributes_to_revert:
            if attribute_name in currentConfigResource["Attributes"]:
                current_value = currentConfigResource["Attributes"][attribute_name]
                pending_value = pendingConfigResource["Attributes"][attribute_name]
                if current_value <> pending_value:
                    #sys.stdout.write("\n{} current={}, pending={}".format(attribute_name, current_value, pending_value))
                    patch_data[attribute_name] = current_value
        self.patchScalablePmemSettingAttributes(patch_data)

        # bios drives

        patch_data = { }
        for attribute_name, value in currentBiosSettings["Attributes"].items():
            if attribute_name.startswith("NVMeDrive"):
                current_value = currentBiosSettings["Attributes"][attribute_name]
                pending_value = pendingBiosSettings["Attributes"][attribute_name]
                if current_value <> pending_value:
                    if current_value == Drive.MODE_NVDIMM or pending_value == Drive.MODE_NVDIMM:
                        #sys.stdout.write("\n{} current={}, pending={}".format(attribute_name, current_value, pending_value))
                        patch_data[attribute_name] = current_value
        self.patchBiosSettingAttributes(patch_data)
