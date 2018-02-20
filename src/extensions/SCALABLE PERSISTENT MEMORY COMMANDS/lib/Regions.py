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

import math
from collections import OrderedDict

class RegionOperations:
    UNKNOWN = -1
    NOCHANGE = 0
    CREATE = 1
    REMOVE = 2

    @staticmethod
    def get_string(value):
        mapping = {
            RegionOperations.UNKNOWN : "Unknown",
            RegionOperations.NOCHANGE : "",
            RegionOperations.CREATE : "Create",
            RegionOperations.REMOVE : "Remove"
        }

        if value in mapping:
            return mapping[value]
        else:
            return mapping[RegionOperations.UNKNOWN]


class RegionBase(object):
    def __init__(self, parent, regionIndex):
        self._parent = parent
        self._regionIndex = regionIndex
        self._currentSizeGiB = 0
        self._pendingSizeGiB = 0

    @property
    def isFree(self):
        return self._pendingSizeGiB == 0 and self._currentSizeGiB == 0

    @property
    def isConfigured(self):
        '''Returns True if the region is configured.'''
        return self._pendingSizeGiB > 0

    @property
    def isActivelyConfigured(self):
        '''Returns True if the region is actively configured on the system.'''
        return self._currentSizeGiB > 0

    @property
    def parent(self):
        '''The owner of the region'''
        return self._parent

    @property
    def regionIndex(self):
        '''The index of the region'''
        return self._regionIndex

    @property
    def currentSizeGiB(self):
        '''Current (active) size of the region'''
        return self._currentSizeGiB

    @property
    def pendingSizeGiB(self):
        '''Pending (not rebooted yet) size of the region'''
        return self._pendingSizeGiB

    @currentSizeGiB.setter
    def currentSizeGiB(self, value):
        '''Current (active) size of the region'''
        self._currentSizeGiB = value

    @pendingSizeGiB.setter
    def pendingSizeGiB(self, value):
        '''Pending (not rebooted yet) size of the region'''
        self._pendingSizeGiB = value

    @property
    def operation(self):
        '''An integer (RegionOperations) describing the operation that will be performed, based on the current and pending size'''
        result = RegionOperations.UNKNOWN

        if self.currentSizeGiB == 0:
            if self.pendingSizeGiB == 0:
                result = RegionOperations.NOCHANGE
            else:
                result = RegionOperations.CREATE
        else:
            if self.pendingSizeGiB == 0:
                result = RegionOperations.REMOVE
            else:
                result = RegionOperations.NOCHANGE
        return result

    @property
    def settingName(self):
        raise NotImplementedError()   # pragma: no cover

    @property
    def locationDescription(self):
        raise NotImplementedError()   # pragma: no cover



class NumaRegion(RegionBase):
    '''Represents a region on a single NUMA domain / processor'''

    @property
    def parentSocket(self):
        '''The socket that contains the region'''
        return self.parent

    @property
    def settingName(self):
        '''Name of the setting attribute that configures this region'''
        return "Processor{}LogicalNvdimm{}SizeGiB".format(self.parentSocket.processorIndex, self.regionIndex)

    @property
    def locationDescription(self):
        '''A string describing the location of the logical NVDIMM'''
        return "Processor {}, Index {}".format(self.parentSocket.processorIndex, self.regionIndex)



class NonNumaRegion(RegionBase):
    '''Represents a region that spans multiple NUMA domains'''

    @property
    def parentSocketPair(self):
        '''Represents the socket pair that contains the region'''
        return self.parent

    @property
    def settingName(self):
        '''Name of the setting attribute that configures this region'''
        return "SpannedLogicalNvdimm{}SizeGiB".format(self.regionIndex)

    @property
    def locationDescription(self):
        '''A string describing the location of the logical NVDIMM'''
        return "Processors {}".format(self.parentSocketPair.labelString)



class Socket(object):
    def __init__(self, parent, socketIndex, maxPmemGiB, maxRegions):
        self._socketIndex = socketIndex
        self._parentRegions = parent
        self._maxRegions = maxRegions
        self._maxPmemGiB = maxPmemGiB
        self._socketPair = None
        self._reportedAvailablePmemMemoryGiB = 0
        # create the # of region entries based on the max possible, initializing sizes to 0
        self._numaRegions = OrderedDict()
        for regionIndex in range(1, self._maxRegions + 1):
            self._numaRegions[regionIndex] = NumaRegion(self, regionIndex)

    @property
    def parentRegions(self):
        return self._parentRegions

    @property
    def socketPair(self):
        return self._socketPair

    @socketPair.setter
    def socketPair(self, socketPair):
        self._socketPair = socketPair

    @property
    def socketIndex(self):
        return self._socketIndex

    @property
    def processorIndex(self):
        return self._socketIndex + 1

    @property
    def maxRegions(self):
        return self._maxRegions

    @property
    def maxPmemGiB(self):
        return self._maxPmemGiB

    @property
    def reportedAvailablePmemMemoryGiB(self):
        return self._reportedAvailablePmemMemoryGiB

    @reportedAvailablePmemMemoryGiB.setter
    def reportedAvailablePmemMemoryGiB(self, value):
        self._reportedAvailablePmemMemoryGiB = value

    @property
    def numaRegions(self):
        return self._numaRegions

    @property
    def firstZeroSizeRegion(self):
        match = None
        for _, region in self._numaRegions.items():
            if region.isFree:
                match = region
                break
        return match

    @property
    def totalNumaSizeGiB(self):
        totalSize = 0
        for _, region in self._numaRegions.items():
            totalSize += region.pendingSizeGiB
        return totalSize

    @property
    def availableSizeGiB(self):
        return self.maxPmemGiB - self.totalNumaSizeGiB

    @property
    def labelString(self):
        return "{}".format(self.processorIndex)

    @property
    def availableSizeGiBHint(self):
        isSlotAvailable = True
        if not self.firstZeroSizeRegion:
            isSlotAvailable = False

        return min(self.availableSizeGiB, self._socketPair.availableSizeGiB, self._parentRegions.availableSizeGiB), isSlotAvailable



class SocketPair(object):
    def __init__(self, parent, index, lowSocket, highSocket):
        self._sockets = []
        self._parentRegions = parent
        self._pairIndex = index
        self._nonNumaRegion = NonNumaRegion(self, index)
        lowSocket.socketPair = self
        highSocket.socketPair = self
        self._sockets.append(lowSocket)
        self._sockets.append(highSocket)

    @property
    def parentRegions(self):
        return self._parentRegions

    @property
    def labelString(self):
        return "{},{}".format(self._sockets[0].processorIndex, self._sockets[1].processorIndex)

    @property
    def sockets(self):
        return self._sockets

    @property
    def pairIndex(self):
        return self._pairIndex

    @property
    def nonNumaRegion(self):
        return self._nonNumaRegion

    @property
    def maxPmemGiB(self):
        maxPmem = 0
        for s in self._sockets:
            maxPmem += s.maxPmemGiB
        return maxPmem

    @property
    def totalNumaSizeGiB(self):
        totalSize = 0
        for s in self._sockets:
            totalSize += s.totalNumaSizeGiB
        return totalSize

    @property
    def totalNonNumaSizeGiB(self):
        return self._nonNumaRegion.pendingSizeGiB

    @property
    def totalSizeGiB(self):
        totalSize = self.totalNumaSizeGiB
        totalSize += self._nonNumaRegion.pendingSizeGiB
        return totalSize

    @property
    def availableSizeGiB(self):
        return self.maxPmemGiB - self.totalSizeGiB

    @property
    def availableSizeGiBHint(self):
        isSlotAvailable = True
        if not self._nonNumaRegion.isFree:
            isSlotAvailable = False
        
        if self._parentRegions.availableSizeGiB < self._parentRegions.minSpannedRegionSizeGiB:
            return 0, isSlotAvailable

        for socket in self.sockets:
            if socket.availableSizeGiB < self._parentRegions.allocationUnitSizeGiB:
                return 0, isSlotAvailable

        return min(self.availableSizeGiB, self._parentRegions.availableSizeGiB), isSlotAvailable



class Regions(object):
    def __init__(self):
        self._sockets = OrderedDict()
        self._socketPairs = OrderedDict()
        self._maxPmemGiB = 0
        self._backupBootSec = 0
        self._reportedAvailablePmemMemory = 0
        self._maxRegionsPerSocket = 2
        self._maxNonNumaRegions = 2
        self._allocationUnitSizeGiB = 1
        self._minRegionSizeGiB = self._allocationUnitSizeGiB
        self._minSpannedRegionSizeGiB = self._allocationUnitSizeGiB * 2
        self._subNumaClusteringEnabled = False

    @property
    def isValidConfiguration(self):
        """
        Checks to see if the pending configuration is valid, based on constraints
        """
        isValid = True
        msg = None

        #
        # 1. make sure all regions are >= minimum size and a multiple of the allocation unit size
        #

        # single-proc regions
        for _, socket in self._sockets.items():
            for _, region in socket.numaRegions.items():
                if region.pendingSizeGiB != 0:
                    if region.pendingSizeGiB < self._minRegionSizeGiB:
                        isValid = False
                        msg = "{}: The requested size is less than the minimum required size of {} GiB".format(
                            region.locationDescription, self._minRegionSizeGiB)
                        break
                    if region.pendingSizeGiB % self._allocationUnitSizeGiB <> 0:
                        isValid = False
                        msg = "{}: The requested size must be a multiple of {} GiB".format(
                            region.locationDescription, self._allocationUnitSizeGiB)
                        break
        if not isValid:
            return (isValid, msg)

        # spanned regions
        for _, pair in self._socketPairs.items():
            region = pair.nonNumaRegion
            if region.pendingSizeGiB != 0:
                if region.pendingSizeGiB < self._minSpannedRegionSizeGiB:
                    isValid = False
                    msg = "{}: The requested size is less than the minimum required size of {} GiB".format(
                        region.locationDescription, self._minSpannedRegionSizeGiB)
                    break
                if region.pendingSizeGiB % self._allocationUnitSizeGiB <> 0:
                        isValid = False
                        msg = "{}: The requested size must be a multiple of {} GiB".format(
                            region.locationDescription, self._allocationUnitSizeGiB)
                        break
        if not isValid:
            return (isValid, msg)

        #
        # 2. make sure total sizes do not exceed known limits
        #    a. Overall total
        #    b. Total combined per socket pair
        #    c. Total NUMA per socket
        #

        # (a)
        if self.totalSizeGiB > self._maxPmemGiB:
            isValid = False
            msg = "The total requested size ({}GiB) exceeds the supported size ({} GiB)".format(
                self.totalSizeGiB, self._maxPmemGiB)
        if not isValid:
            return (isValid, msg)

        # (b)
        for _, pair in self._socketPairs.items():
            if pair.totalSizeGiB > pair.maxPmemGiB:
                isValid = False
                msg = "Processors {}: The total requested size ({} GiB) exceeds the supported size ({} GiB)".format(
                    pair.labelString, pair.totalSizeGiB, pair.maxPmemGiB)

        # (c)
        for _, socket in self._sockets.items():
            if socket.totalNumaSizeGiB > socket.maxPmemGiB:
                isValid = False
                msg = "Processor {}: The total requested size ({} GiB) exceeds the supported size ({} GiB)".format(
                    socket.labelString, socket.totalNumaSizeGiB, socket.maxPmemGiB)
                break
        if not isValid:
            return (isValid, msg)

        #
        # 3. make sure that a spanned region has room for at least 1 allocation unit to reside on each socket in the pair
        #

        for _, pair in self._socketPairs.items():
            if pair.totalNonNumaSizeGiB > 0:
                for socket in pair.sockets:
                    if socket.availableSizeGiB < self._allocationUnitSizeGiB:
                        isValid = False
                        msg = "Processors {}: The logical NVDIMMs allocated do not allow room for a spanned logical NVDIMM".format(
                            pair.labelString)

        return (isValid, msg)

    @property
    def subNumaClusteringEnabled(self):
        return self._subNumaClusteringEnabled

    @subNumaClusteringEnabled.setter
    def subNumaClusteringEnabled(self, value):
        self._subNumaClusteringEnabled = value

    @property
    def maxRegionsPerSocket(self):
        return self._maxRegionsPerSocket

    @maxRegionsPerSocket.setter
    def maxRegionsPerSocket(self, value):
        """
        Set the maximum # of regions allowed per socket
        NOTE: this must be called before calling addSocket() or the nubmer of
              region slots that are automatically added for the socket will
              be incorrecct
        """
        self._maxRegionsPerSocket = value

    def addSocket(self, socketIndex, maxPmemGiB):
        """Add a new socket to the model
        NOTE: each time this is called, the socket pairs and non-numa regions structures
              are re-calculated, so addSocket() should only be called once at initialization
              to add the detected sockets.
        """
        # add a socket
        s = Socket(self, socketIndex, maxPmemGiB, self._maxRegionsPerSocket)
        self._sockets[socketIndex] = s
        # now, (re-)define socket pairs
        self._defineSocketPairs()
        return s

    def _defineSocketPairs(self):
        """Helper for addSocket() -- not to be called directly"""
        validPairs = [ # current valid pairs for 4P system
            {"regionId": 1, "sockets": [0, 1]},
            {"regionId": 2, "sockets": [2, 3]}
        ]
        self._socketPairs.clear()
        # first, generate socket pairs based on valid socket
        # combinations and available sockets
        for pair in validPairs:
            socket0 = self._sockets.get(pair["sockets"][0])
            socket1 = self._sockets.get(pair["sockets"][1])
            if socket0 and socket1:
                self._socketPairs[pair["regionId"]] = SocketPair(self, pair["regionId"], socket0, socket1)

    @property
    def sockets(self):
        return self._sockets

    @property
    def socketPairs(self):
        return self._socketPairs

    @property
    def maxPmemGiB(self):
        return self._maxPmemGiB

    @maxPmemGiB.setter
    def maxPmemGiB(self, value):
        self._maxPmemGiB = value

    @property
    def backupBootSec(self):
        return self._backupBootSec

    @backupBootSec.setter
    def backupBootSec(self, value):
        self._backupBootSec = value

    @property
    def reportedAvailablePmemMemory(self):
        return self._reportedAvailablePmemMemory

    @property
    def maxNonNumaRegions(self):
        return self._maxNonNumaRegions

    @maxNonNumaRegions.setter
    def maxNonNumaRegions(self, value):
        self._maxNonNumaRegions = value

    @property
    def minRegionSizeGiB(self):
        return self._minRegionSizeGiB

    @minRegionSizeGiB.setter
    def minRegionSizeGiB(self, value):
        self._minRegionSizeGiB = value

    @property
    def minSpannedRegionSizeGiB(self):
        return self._minSpannedRegionSizeGiB

    @minSpannedRegionSizeGiB.setter
    def minSpannedRegionSizeGiB(self, value):
        self._minSpannedRegionSizeGiB = value

    @property
    def allocationUnitSizeGiB(self):
        return self._allocationUnitSizeGiB

    @allocationUnitSizeGiB.setter
    def allocationUnitSizeGiB(self, value):
        self._allocationUnitSizeGiB = value

    @property
    def totalSizeGiB(self):
        totalSize = 0
        for _, pair in self._socketPairs.items():
            totalSize += pair.totalSizeGiB
        return totalSize

    @property
    def availableSizeGiB(self):
        return self.maxPmemGiB - self.totalSizeGiB

    @property
    def firstZeroSizeRegion(self):
        matchingSocket = None
        matchingRegion = None
        for _, socket in self._sockets.items():
            matchingRegion = socket.firstZeroSizeRegion
            if matchingRegion:
                matchingSocket = socket
                break
        return (matchingSocket, matchingRegion)

    @property
    def firstZeroSizeNonNumaRegion(self):
        matchingRegion = None
        for _, pair in self._socketPairs.items():
            region = pair.nonNumaRegion
            if region.isFree:
                matchingRegion = region
                break
        return matchingRegion

    @property
    def allRegions(self):
        all_regions = []
        for _, pair in self._socketPairs.items():
            all_regions.append(pair.nonNumaRegion)
        for _, socket in self._sockets.items():
            for _, region in socket.numaRegions.items():
                all_regions.append(region)
        return all_regions

    @property
    def isActivelyConfigured(self):
        return any(region.isActivelyConfigured for region in self.allRegions)

    @property
    def isConfigured(self):
        return any(region.isConfigured for region in self.allRegions)

    @property
    def areOperationsPending(self):
        '''Indicates whether there are pending operations for any regions'''
        all_regions = self.allRegions
        pending_operation_regions = [region for region in all_regions if region.currentSizeGiB <> region.pendingSizeGiB]
        return len(pending_operation_regions) > 0

