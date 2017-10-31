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

from Health import *
from State import *

class DriveOperations:
    UNKNOWN = -1
    NONE = 0
    ENABLED = 1
    ADD = 2
    REMOVE = 3

    @staticmethod
    def get_string(value):
        mapping = {
            DriveOperations.UNKNOWN : "Unknown",
            DriveOperations.NONE : None,
            DriveOperations.ENABLED : None,
            DriveOperations.ADD : "Add",
            DriveOperations.REMOVE : "Remove"
        }

        if value in mapping:
            return mapping[value]
        else:
            return mapping[DriveOperations.UNKNOWN]



class Drive(object):
    '''Defines a drive'''

    MODE_NVDIMM = "ScalablePMEM"
    MODE_NVME = "Nvme"

    def __init__(self):
        self._locInfo = None
        self._locFormat = None
        self._driveType = None
        self._protocol = None
        self._sizeBytes = None
        self._model = None
        self._correlationId = None
        self._partNumber = None
        self._serialNumber = None
        self._enabled = None
        self._settingName = None
        self._pendingMode = None
        self._currentMode = None
        self._isBiosSupported = False
        self._config = None
        self._dw = None
        self._wp = None
        self._health = None
        self._status = None
        self._failurePredicted = False
        self._predictedMediaLifeLeftPercent = None

    @property
    def sizeGB(self):
        return self._sizeBytes / 1000000000

    @property
    def sizeMB(self):
        return self._sizeBytes / 1000000

    @property
    def sizeBytes(self):
        return self._sizeBytes

    @sizeBytes.setter
    def sizeBytes(self, value):
        self._sizeBytes = value

    @property
    def formattedLocation(self):
        result = "Unknown"
        if self._locInfo and self._locFormat:
            if self._locFormat == "Box:Bay":
                splitLoc = self._locInfo.split(":")
                result = "Box {} Bay {}".format(splitLoc[0], splitLoc[1])
            else:
                result = self.originalLocation
        return result

    @property
    def originalLocation(self):
        return "{} ({})".format(self._locInfo, self._locFormat)

    @property
    def generatedId(self):
        result = "?"
        if self._locInfo and self._locFormat:
            if self._locFormat == "Box:Bay":
                splitLoc = self._locInfo.split(":")
                result = "{}@{}".format(splitLoc[0], splitLoc[1])
        return result

    @property
    def formattedType(self):
        return "{} ({})".format(self._driveType, self._protocol)

    @property
    def locInfo(self):
        return self._locInfo

    @property
    def locFormat(self):
        return self._locFormat

    def setLoc(self, info, fmt):
        self._locInfo = info
        self._locFormat = fmt

    @property
    def driveType(self):
        return self._driveType

    @driveType.setter
    def driveType(self, value):
        self._driveType = value

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        self._protocol = value

    @property
    def model(self):
        return self._model

    @property
    def dw(self):
        return self._dw

    @dw.setter
    def dw(self, value):
        self._dw = value

    @property
    def wp(self):
        return self._wp

    @wp.setter
    def wp(self, value):
        self._wp = value

    @model.setter
    def model(self, value):
        self._model = value

    @property
    def correlationId(self):
        return self._correlationId

    @correlationId.setter
    def correlationId(self, value):
        self._correlationId = value

    @property
    def partNumber(self):
        return self._partNumber

    @partNumber.setter
    def partNumber(self, value):
        self._partNumber = value

    @property
    def serialNumber(self):
        return self._serialNumber

    @serialNumber.setter
    def serialNumber(self, value):
        self._serialNumber = value

    @property
    def enabled(self):
        return self._state == State.ENABLED

    @property
    def settingName(self):
        return self._settingName

    @settingName.setter
    def settingName(self, value):
        self._settingName = value

    @property
    def pendingMode(self):
        return self._pendingMode

    @pendingMode.setter
    def pendingMode(self, value):
        self._pendingMode = value

    @property
    def currentMode(self):
        return self._currentMode

    @currentMode.setter
    def currentMode(self, value):
        self._currentMode = value

    def mode_to_string(self, mode):
        if mode == Drive.MODE_NVME:
            return "NVMe"
        elif mode == Drive.MODE_NVDIMM:
            return "Scalable PMEM"
        else:
            return "Unknown"

    @property
    def currentModeDisplayString(self):
        return self.mode_to_string(self._currentMode)

    @property
    def pendingModeDisplayString(self):
        return self.mode_to_string(self._pendingMode)

    @property
    def isSupported(self):
        valid_modes = [Drive.MODE_NVDIMM, Drive.MODE_NVME]
        is_mode_ok = self._pendingMode in valid_modes and self._currentMode in valid_modes
        return self._isBiosSupported and is_mode_ok

    @property
    def isBiosSupported(self):
        return self._isBiosSupported

    @isBiosSupported.setter
    def isBiosSupported(self, value):
        self._isBiosSupported = value

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    @property
    def operation(self):
        '''An integer (DriveOperations) describing the operation that will be performed, based on the current and pending modes'''
        result = DriveOperations.UNKNOWN
        if self.currentMode == Drive.MODE_NVDIMM:
            if self.pendingMode <> self.currentMode:
                result = DriveOperations.REMOVE
            else:
                result = DriveOperations.ENABLED
        elif self.currentMode == Drive.MODE_NVME:
            if self.pendingMode <> self.currentMode:
                result = DriveOperations.ADD
            else:
                result = DriveOperations.NONE
        return result

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        self._health = value

    @property
    def predictedMediaLifeLeftPercent(self):
        return self._predictedMediaLifeLeftPercent

    @predictedMediaLifeLeftPercent.setter
    def predictedMediaLifeLeftPercent(self, value):
        self._predictedMediaLifeLeftPercent = value

    @property
    def failurePredicted(self):
        return self._failurePredicted

    @failurePredicted.setter
    def failurePredicted(self, value):
        self._failurePredicted = value

    @property
    def healthDisplayString(self):
        ''' returns a single string rolling up data from health, state, predicted media failure '''
        result = None
        if self._state <> State.ENABLED:
            result = self._state
        else:
            result = self._health
        return result



class Drives(object):
    '''Defines a collection of drives'''

    def __init__(self, drive_list):
        self._driveList = drive_list

    @property
    def allDrives(self):
        return self._driveList

    @property
    def supportedDrives(self):
        supported_drives = [drive for drive in self._driveList if drive.isSupported]
        return supported_drives

    def findDrive(self, id_string):
        matching_drive = next((x for x in self._driveList if x.generatedId == id_string), None)
        return matching_drive

    def findDrives(self, id_strings):
        found_drives = []

        for id_string in id_strings:
            matching_drive = self.findDrive(id_string)
            if not matching_drive:
                raise ValueError(id_string)

            found_drives.append(matching_drive)

        return found_drives

    @property
    def selectedDrives(self):
        '''All drives that have pending mode = NVDIMM'''
        selected_drives = [drive for drive in self._driveList if drive.pendingMode == Drive.MODE_NVDIMM]
        return selected_drives

    @property
    def areOperationsPending(self):
        '''Indicates whether there are pending operations (mode changes) for any drives'''
        pending_operation_drives = [drive for drive in self._driveList if (drive.pendingMode <> drive.currentMode) and (drive.pendingMode == Drive.MODE_NVDIMM or drive.currentMode == Drive.MODE_NVDIMM)]
        return len(pending_operation_drives) > 0

    @property
    def areRemoveOperationsPending(self):
        '''Indicates whether there are pending remove operations for any drives'''
        pending_operation_drives = [drive for drive in self._driveList if drive.operation == DriveOperations.REMOVE]
        return len(pending_operation_drives) > 0
