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

""" Logical NVDIMM Validation command """

import ctypes
from _ctypes import Structure
from ctypes import c_ulonglong, c_char_p, c_int
from jsonpointer import resolve_pointer

from Drives import Drive
from Health import *
from Helpers import Helpers
from State import *



class LogicalNvdimmValidator():
    """ LogicalNvdimmValidator  class """

    def __init__(self):
        pass


    def calculateMaxPmemGiB(self, chifLib, configResource, listOfDrives):
        """ calculateMaxPmemGiB Calculates the maximum available amount of persistent memory available,
        based on the system hardware and settings.

        :param chifLib: ilorest-chif DLL
        :type chifLib: library handle

        :param configResource: dictionary of Scalable PMEM configuration data
        :type configResource: dictionary

        :param listOfDrives: list of ALL drives to be backup storage
        :type listOfDrives: list of drive objects

        :returns: maximum available persistent memory (GiB).
        :rtype: long
        """
        (maxPmemGiB, backupBootSec) = self.calculateMaxPmemGiBAndBackupTime(chifLib, 0, configResource, listOfDrives)
        return maxPmemGiB
        
    def calculateMaxPmemGiBAndBackupTime(self, chifLib, configured_pmem_GiB, configResource, listOfDrives):
        """ calculateMaxPmemGiBAndBackupTime Calculates the maximum available amount of persistent memory available,
        based on the system hardware and settings. 
        Also estimates the backup boot time based on configured Scalable PMEM size and drives.

        :param chifLib: ilorest-chif DLL
        :type chifLib: library handle
        
        :param configured_pmem_GiB: amount of Scalable PMEM configured
        :type configured_pmem_GiB: number to be converted to ctypes.clonglong

        :param configResource: dictionary of Scalable PMEM configuration data
        :type configResource: dictionary

        :param listOfDrives: list of ALL drives to be backup storage
        :type listOfDrives: list of drive objects

        :returns: maximum available persistent memory (GiB).
        :rtype: long
        """
        maxPmemGiB = 0
        backupBootSec = 0

        # get the configuration data
        if configResource:
            configData = self.constructConfigData(configResource)
            selectedDriveCollection = self.createSelectedDriveCollection(listOfDrives)
            if configData and selectedDriveCollection.count > 0:
                # first, check the validation version
                isSupportedVersion = self.checkValidationVersion(chifLib, configData.validationVersion)
                if not isSupportedVersion:
                    print("Unsupported version of iLO CHIF library detected. Please get the latest version.\n")
                    Helpers.failNoChifLibrary()
                # then calculate maximum persistent memory, based on the configuration
                maxPmemGiB = self.calculateMaxPmemGiB_inner(chifLib, configData, selectedDriveCollection)
                backupBootSec = self.estimateBackupBootTimeSec_inner(chifLib, configured_pmem_GiB, configData, selectedDriveCollection)
            else:
                return (0, 0)
        else:
            return (0, 0)

        return (maxPmemGiB,  backupBootSec)

    def calculateMaxPmemGiB_inner(self, chifLib, configData, selectedDriveCollection):
        """ calls the function in the library given the structured inputs

        :param chifLib: ilorest-chif library
        :type chifLib: library handle

        :param configData: the configuration data.
        :type configData: LOGICALNVDIMMCONFIGDATA.

        :param selectedDriveCollection: the user selected backup drives.
        :type selectedDriveCollection: SELECTEDDRIVECOLLECTION.

        :returns: maximum available persistent memory (GiB).
        :rtype: long
        """
        maxPmemGiB = 0
        if chifLib:
            try:
                chifLib.calculateMaxPmemGiB.argtypes = [ctypes.POINTER(LOGICALNVDIMMCONFIGDATA), ctypes.POINTER(SELECTEDDRIVECOLLECTION)]
                chifLib.calculateMaxPmemGiB.restype = c_ulonglong
                if selectedDriveCollection != None and selectedDriveCollection.count > 0:
                    maxPmemGiB = chifLib.calculateMaxPmemGiB(ctypes.byref(configData), ctypes.byref(selectedDriveCollection))
            except AttributeError:
                print("Unsupported version of iLO CHIF library detected. Please get the latest version.\n")
                Helpers.failNoChifLibrary()

        return maxPmemGiB

    def checkValidationVersion(self, chifLib, versionToCheck):
        """
        Check if the validation version matched the chifLib's validation version

        :param chifLib: reference to the ilorest-chif library
        :type chifLib: library handle

        :param version: the Scalable PMEM validation version to check
        :type integer

        :returns: True if the version is supported by the CHIF library, False if not
        :type Boolean
        """
        isSupported = False
        if chifLib:
            try:
                chifLib.supportsPMEMValidationVersion.argtypes = [ctypes.c_int]
                chifLib.supportsPMEMValidationVersion.restype = ctypes.c_bool
                isSupported = chifLib.supportsPMEMValidationVersion(versionToCheck)
            except AttributeError:
                print("Old version of iLO CHIF library detected. Please get the latest version.\n")
                Helpers.failNoChifLibrary()

        return isSupported
    
    def estimateBackupBootTimeSec_inner(self, chifLib, configured_pmem_GiB, configData, selectedDriveCollection):
        """
        Estimate the backup boot time (sec)
        
        :param chifLib: reference to the ilorest-chif-library
        :type chifLib: library handle
        
        :param: configured_pmem_GiB: amount of Scalable PMEM configured
        :type configured_pmem_GiB: number to be casted to a ctypes.ulonglong
        
        :param configData: the configuration data.
        :type configData: LOGICALNVDIMMCONFIGDATA.

        :param selectedDriveCollection: the user selected backup drives.
        :type selectedDriveCollection: SELECTEDDRIVECOLLECTION.

        :returns: estimated backup boot time (sec)
        :rtype: long
        """
        backupBootSec = 0
        if chifLib:
            try:
                chifLib.estimatePMEMBackupBootTimeSec.argtypes = [c_ulonglong, ctypes.POINTER(LOGICALNVDIMMCONFIGDATA), ctypes.POINTER(SELECTEDDRIVECOLLECTION)]
                chifLib.estimatePMEMBackupBootTimeSec.restype = c_ulonglong
                if selectedDriveCollection != None and selectedDriveCollection.count > 0:
                    backupBootSec = chifLib.estimatePMEMBackupBootTimeSec(c_ulonglong(configured_pmem_GiB), ctypes.byref(configData), ctypes.byref(selectedDriveCollection))
            except AttributeError:
                print("Unsupported version of iLO CHIF library detected. Please get the latest version.\n")
                Helpers.failNoChifLibrary()

        return backupBootSec

    def isScalablePmemSupported(self, config):
        """
        Determine if Scalable PMEM is supported

        :param config: configuration data
        :type config: configuration data

        :returns: whether or not Scalable PMEM is supported and messages explaining issues if found
        :type (bool, string, string)
        """
        # construct the reason messages dictionary
        notSupportedReasonMessages = {
            "OemDisabled":u"Functionality is disabled by the OEM",
            "UnsupportedPlatform":u"Unsupported platform",
            "OtherNvdimmTechnologyEnabled":u"Another persistent memory technology is in use"
        }

        # Logical NVDIMM must be supported on this server
        if not resolve_pointer(config, "/Attributes/FeatureSupported", False):
            # determine the reason Logical NVDIMMs are not supported
            messageList = []
            reasons = resolve_pointer(config, "/Attributes/FeatureNotSupportedReasons", None)
            if reasons:
                for reasonId, value in reasons.items():
                    if value:
                        message = notSupportedReasonMessages.get(reasonId)
                        if message:
                            messageList.append(message)
            return (False, u"Scalable Persistent Memory is not supported on this system", messageList)

        return (True, None, None)



    def isScalablePmemEnabledByUser(self, config):
        """
        Determine if Scalable PMEM is enabled by user

        :param config: configuration data
        :type config: configuration data

        :returns: whether or not Scalable PMEM is enabled by the user and messages explaining issues if found
        :type (bool, string, string)
        """
        # Should not configure if the user has disabled the feature (potential data loss)
        if not resolve_pointer(config, "/Attributes/FeatureEnabled", False):
            return (False, u"The Scalable Persistent Memory feature is set to disabled",
                    [u"Enable the feature to continue with configuration"])
        return (True, None, None)

    def isScalablePmemFunctionalityEnabled(self, config):
        """
        Determine if Scalable PMEM functionality is enabled

        :param config: configuration data
        :type config: configuration data

        :returns: whether or not Scalable PMEM functionality is enabled and messages explaining issues if found
        :type (bool, string, string)
        """
        # construct functionality disabled reason messages dictionary
        functionalityDisabledMessages = {
            "PowerSubsystemProblem":u"Problem with backup power",
            "StorageSubsystemProblem":u"Problem with backup storage devices",
            "MemorySubsystemProblem":u"Problem with memory"
        }

        if not resolve_pointer(config, "/Attributes/FunctionalityEnabled", False):
            reasonMessages = []
            reasons = resolve_pointer(config, "/Attributes/FunctionalityDisabledReason", None)
            if reasons:
                for reasonId, value in reasons.items():
                    if value:
                        message = functionalityDisabledMessages.get(reasonId)
                        if message:
                            reasonMessages.append(message)
            return (False, u"Scalable Persistent Memory is disabled due to problems", reasonMessages)

        return (True, None, None)

    def checkAllLogicalNvdimmPolicies(self, config):
        """ checks that the configuration is valid, based on the configuration policies (no math)

        :returns: (isValid, Messages) isValid is True if configuration is valid, False if not. Messages includes detailed message(s) about the cause of the failures.
        :rtype: (bool, array of string)
        """

        # All of these must be true to configure the system:

        # is supported?
        isSupported, overall_message, messages = self.isScalablePmemSupported(config)
        if not isSupported:
            return (isSupported, overall_message, messages)

        # is functionality enabled by ROM?
        isFuncEnabled, overall_message, messages = self.isScalablePmemFunctionalityEnabled(config)
        if not isFuncEnabled:
            return (isFuncEnabled, overall_message, messages)

        # is enabled by user?
        isEnabled, overall_message, messages = self.isScalablePmemEnabledByUser(config)
        if not isEnabled:
            return (isEnabled, overall_message, messages)

        # pass if all these are True
        return (True, None, None)

    def checkLogicalNvdimmDrivePolicies(self, config, listOfDrives):
        """ checks that the backup drive configuration is valid, based on the configuration policies (no math)

        :param selectedDrives: list of Drives
        :type listOfDrives: list of Drive

        :returns: (isValid, Message) isValid is True if configuration is valid, False if not. Message contains description of failure to user
        :rtype: (bool, string)
        """

        # there must be drives selected
        if len(listOfDrives) == 0:
            return (False, u"No backup storage devices are selected")

        # cannot exceed the maximum number of drives
        maxDrives = resolve_pointer(config, "/Attributes/MaximumDriveCount", 0)
        if len(listOfDrives) > maxDrives:
            return (False, u"Number of backup storage devices exceeds maximum: {}".format(maxDrives))

        # drives must be enabled and healthy
        for drive in listOfDrives:
            if drive.health == Health.WARNING:
                return (False, u"Drive {} is in a degraded state".format(drive.generatedId))
            if drive.health == Health.CRITICAL:
                return (False, u"Drive {} is in a failed state".format(drive.generatedId))
            if not drive.enabled:
                return (False, u"Drive {} is not enabled".format(drive.generatedId))

        # get policies
        policies = resolve_pointer(config, "/Attributes/Policy", None)
        sameModel = False
        sameSize = False
        if policies:
            sameModel = policies.get("SameModelNVMe", False)
            sameSize = policies.get("SameSizeNVMe", False)

        # loop through each drive to check policies
        for drive in listOfDrives:
            # all drives must be in the supported drives list
            if not drive.isSupported:
                return (False, u"Drive {} is not supported".format(drive.generatedId))

            # same model requirement
            if sameModel:
                if drive.model != listOfDrives[0].model:
                    return (False, u"Selected backup storage devices must be the same model. Drive {} is model {}. Drive {} is model {}.".format(drive.generatedId, drive.model, listOfDrives[0].generatedId, listOfDrives[0].model))

            # same size requirements
            if sameSize:
                if drive.sizeBytes != listOfDrives[0].sizeBytes:
                    return (False, u"Selected backup storage devices must be the same size (capacity). Drive {} has different size than drive {}.".format(drive.generatedId, listOfDrives[0].generatedId))

        # if all passed, then return True
        return (True, u"")

    def constructConfigData(self, config):
        try:
            # get the supported drives list
            supportedDrives = resolve_pointer(config, "/Attributes/SupportedDrives", None)
            if supportedDrives is None:
                supportedDrivesCollection = (None, 0)
            else:
                supportedDrivesList = []
                for drive in supportedDrives:
                    supportedDrive = LOGICALNVDIMMSUPPORTEDDRIVE(drive["NVMeId"], drive["WP"], drive["DW"])
                    supportedDrivesList.append(supportedDrive)
                supportedDriveArray = (LOGICALNVDIMMSUPPORTEDDRIVE * len(supportedDrivesList))(*supportedDrivesList)
                pSupportedDriveArrayStart = ctypes.cast(supportedDriveArray, ctypes.POINTER(LOGICALNVDIMMSUPPORTEDDRIVE))
                supportedDrivesCollection = LOGICALNVDIMMSUPPORTEDDRIVECOLLECTION(pSupportedDriveArrayStart, len(supportedDrivesList))

            attributes = config["Attributes"]

            data = LOGICALNVDIMMCONFIGDATA(attributes["TheoreticalPMemMaxGiB"] * 1024,\
                                           attributes["CT1"],\
                                           attributes["CT2"],\
                                           attributes["CT3"],\
                                           attributes["CT4"],\
                                           attributes["T1"],\
                                           attributes["T2"],\
                                           attributes["T4"],\
                                           attributes["DT"],\
                                           attributes["PS"],\
                                           attributes["MW"],\
                                           attributes["PW"],\
                                           attributes["TW"],\
                                           supportedDrivesCollection,\
                                           attributes["DriveSizeOverheadMB"],\
                                           attributes["ValidationVersion"])
            return data
        except KeyError as err:
#            sys.stdout.write("error: {0}".format(err)) # DEBUG
            return None

    def createSelectedDriveCollection(self, drivesToUse):
        selectedDrives = []
        for drive in drivesToUse:
            selectedDrives.append(SELECTEDDRIVE(drive.correlationId, drive.sizeMB))
        selectedDrivesArray = (SELECTEDDRIVE * len(selectedDrives))(*selectedDrives)
        pSelectedDrivesStart = ctypes.cast(selectedDrivesArray, ctypes.POINTER(SELECTEDDRIVE))
        return SELECTEDDRIVECOLLECTION(pSelectedDrivesStart, len(selectedDrives))                

# The classes below are created to pass C struct data to the cdll call

class LOGICALNVDIMMSUPPORTEDDRIVE(Structure):
    """ LOGICALNVDIMMSUPPORTEDDRIVE class for C struct"""
    _fields_ = [("NVMeId", c_char_p),
                ("WP", c_ulonglong),
                ("DW", c_ulonglong)]

class LOGICALNVDIMMSUPPORTEDDRIVECOLLECTION(Structure):
    """ LOGICALNVDIMMSUPPORTEDDRIVECOLLECTION for C struct """
    _fields_ = [("pSupportedDriveArray", ctypes.POINTER(LOGICALNVDIMMSUPPORTEDDRIVE)),
                ("count", c_int)]

class SELECTEDDRIVE(Structure):
    """ SELECTEDDRIVE for C struct """
    _fields_ = [("nvmeId", c_char_p),
                ("driveSizeMB", c_ulonglong)]

class SELECTEDDRIVECOLLECTION(Structure):
    """ SELECTEDDRIVECOLLECTION for C struct """
    _fields_ = [("pSelectedDriveArray", ctypes.POINTER(SELECTEDDRIVE)),
                ("count", c_int)]

class LOGICALNVDIMMCONFIGDATA(Structure):
    """ LOGICALNVDIMMCONFIGDATA for C struct """
    _fields_ = [("scalablePmemTheoreticalMaxMiB", c_ulonglong),
                ("CT1", c_ulonglong),
                ("CT2", c_ulonglong),
                ("CT3", c_ulonglong),
                ("CT4", c_ulonglong),
                ("T1", c_ulonglong),
                ("T2", c_ulonglong),
                ("T4", c_ulonglong),
                ("DT", c_ulonglong),
                ("PS", c_ulonglong),
                ("MW", c_ulonglong),
                ("PW", c_ulonglong),
                ("TW", c_ulonglong),
                ("supportedDrives", LOGICALNVDIMMSUPPORTEDDRIVECOLLECTION),
                ("driveSizeOverheadMB", c_ulonglong),
                ("validationVersion", ctypes.c_int)]

