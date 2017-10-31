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

from Regions import RegionOperations
from Drives import Drive, DriveOperations
from rdmc_helper import NoChangesFoundOrMadeError

INITIALIZE = "Initialize"

class ScalablePersistentMemoryConfig(object):
    def __init__(self, restHelpers, validatorObject, chif_lib):
        self._restHelpers = restHelpers
        self._validatorObject = validatorObject
        self._chif_lib = chif_lib
        self._regions = None
        self._drives = None
        self._config = None
        self._pending_config = None

    def refresh(self):
        self._config = self._restHelpers.getConfigResource()
        self._pending_config = self._restHelpers.getPendingConfigResource()
        current_bios_settings = self._restHelpers.getCurrentBiosSettings()
        pending_bios_settings = self._restHelpers.getPendingBiosSettings()
        chassis = self._restHelpers.getChassis()
        drives_data = self._restHelpers.getChassisDrives(chassis)

        if not self._config or not self._pending_config or not current_bios_settings or not chassis or not drives_data:
            raise NoChangesFoundOrMadeError(u"Unable to retrieve Scalable Persistent Memory configuration.")

        self._drives = self._restHelpers.generateDriveConfiguration(self._config, current_bios_settings,
                                                                    pending_bios_settings, drives_data)
        if not self._drives:
            raise NoChangesFoundOrMadeError(u"Unable to retrieve backup storage device information.")

        self._regions = self._restHelpers.generateRegionConfiguration(self._config, self._pending_config, current_bios_settings)
        if not self._regions:
            raise NoChangesFoundOrMadeError(u"Unable to retrieve Scalable Persistent Memory information")

        if self._validatorObject and self._chif_lib:
            # update the config object's theoretical vales with validated ones
            maxPmemGiB = self._validatorObject.calculateMaxPmemGiB(self._chif_lib, self._config, self._drives.selectedDrives)
            self._regions.maxPmemGiB = maxPmemGiB

    @property
    def isConfiguredSystem(self):
        return len(self._drives.selectedDrives) > 0 or self.hasConfiguredRegions

    @property
    def hasConfiguredRegions(self):
        return self._regions.isConfigured

    @property
    def hasActiveConfiguredRegions(self):
        return self._regions.isActivelyConfigured

    @property
    def isEnabledByUser(self):
        return self._validatorObject.isScalablePmemEnabledByUser(self._config)

    def validateConfigurationPolicies(self):
        return self._validatorObject.checkAllLogicalNvdimmPolicies(self._pending_config)

    @property
    def isFeatureSupported(self):
        return self._validatorObject.isScalablePmemSupported(self._config)

    @property
    def isFunctionalityEnabled(self):
        return self._validatorObject.isScalablePmemFunctionalityEnabled(self._config)

    @property
    def regions(self):
        return self._regions

    @property
    def drives(self):
        return self._drives

    @property
    def config_resource(self):
        return self._config

    @property
    def pending_config_resource(self):
        return self._pending_config

    @property
    def max_pmem_supported_gib(self):
        if self._regions:
            return self._regions.maxPmemGiB
        else:
            return None

    @property
    def willInitialize(self):
        if self._restHelpers.isStorageInitializeEnabled(self._pending_config):
            return True
        if self._restHelpers.doesConfigurationRequireStorageInit(self._config) and self.areConfigurationOperationsPending:
            return True
        if self._drives.areRemoveOperationsPending:
            return True
        return False

    @property
    def doesConfigurationRequireStorageInit(self):
        return self._restHelpers.doesConfigurationRequireStorageInit(self._config)

    @property
    def isStorageInitializeEnabled(self):
        return self._restHelpers.isStorageInitializeEnabled(self._pending_config)

    @property
    def areConfigurationOperationsPending(self):
        return self._regions.areOperationsPending or self._drives.areOperationsPending

    def region_operation_description(self, region):
        result = RegionOperations.get_string(region.operation)
        if not region.isFree:
            if self.willInitialize:
                if region.operation not in [RegionOperations.CREATE, RegionOperations.REMOVE]:
                    result = INITIALIZE
        return result

    def drive_operation_description(self, drive):
        strings = [ ]
        operation_string = DriveOperations.get_string(drive.operation)
        if operation_string:
            strings.append(operation_string)
        if self.willInitialize:
            if drive.currentMode == Drive.MODE_NVDIMM or drive.pendingMode == Drive.MODE_NVDIMM:
                strings.append(INITIALIZE)
        return ",".join(strings)