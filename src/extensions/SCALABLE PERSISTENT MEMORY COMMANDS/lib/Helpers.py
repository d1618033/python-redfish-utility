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

import sys
from redfish.hpilo.risblobstore2 import BlobStore2
from Regions import NumaRegion, RegionOperations
from Drives import DriveOperations
from rdmc_helper import NoChangesFoundOrMadeError, UI


class Helpers(object):
    """ Helpers for the Scalable PMEM commands """
    UNKNOWN = "Unknown"

    def __init__(self):
        pass


    @staticmethod
    def failNoChifLibrary():
        sys.stdout.write(u"""

------------------------------------------------------------------------------

 Scalable Persistent Memory configuration requires the CHIF library, which is
 not available as open-source.

 For full functionality, please obtain the latest version from the Hewlett
 Packard Enterprise product support site:

 hpe.com/us/en/product-catalog/detail/pip.restful-interface-tool.7630408.html

------------------------------------------------------------------------------

""")
        raise NoChangesFoundOrMadeError("Unable to continue")

    def noticeRestartRequired(self, scalable_pmem_config):
        if not scalable_pmem_config.areConfigurationOperationsPending:
            return

        if scalable_pmem_config.willInitialize and scalable_pmem_config.hasActiveConfiguredRegions:
            sys.stdout.write("""\n\n
*** WARNING ***

The pending configuration operations require a restart to take effect.

All backup storage devices will be initialized upon restart.
Data on any existing logical NVDIMMs will be lost.

The pending configuration changes can be discarded by running:

     revertscalablepmemconfig

*** Any data that needs to be preserved should be backed up before restarting ***""")
            return

        sys.stdout.write("\n\n\n*** The pending configuration operations require a restart to take effect ***")

    def confirmBeforeConfigCausesDataLoss(self, scalable_pmem_config):
        
        message = u"\nConfiguration changes require all backup storage "\
                         u"devices to be initialized upon restart.\n"\
                         u"Data on any existing logical NVDIMMs will be lost.\n"
        
        if scalable_pmem_config.doesConfigurationRequireStorageInit and scalable_pmem_config.hasActiveConfiguredRegions:
            self.confirmChanges(message)

    def confirmChanges(self, message):
        sys.stdout.write(message)
        s = raw_input(u"\nConfirm changes [y/N]? ")
        if s.lower() != 'y':
            raise NoChangesFoundOrMadeError(u"No changes have been made")

    def displayDrivesConfiguration(self, scalable_pmem_config):
        '''Display formatted backup storage device configuration'''
        # table header
        self.writeTableHeader(
            u"{:6} {:15} {:12} {:10} {:7} {:8} {:4} {:9} {:20}".format(
                "ID", "Location", "Model", "Type", "Size", "Status", "Life", "PMEM Use", "Operation"))

        drives = scalable_pmem_config.drives
        regions = scalable_pmem_config.regions

        for entry in drives.allDrives:
            if not entry.isSupported:
                continue

            sys.stdout.write(u"\n{:6} {:15} {:12} {:10} {:7} {:8} {:4} {:9} {:20}".format(
                self.truncateLengthy(entry.generatedId, 6),
                self.truncateLengthy(entry.formattedLocation, 15),
                self.truncateLengthy(entry.model, 12),
                self.truncateLengthy(entry.formattedType, 10),
                self.truncateLengthy("{} GB".format(entry.sizeGB), 7),
                self.truncateLengthy(entry.healthDisplayString if entry.healthDisplayString <> None else self.UNKNOWN, 8),
                self.truncateLengthy("{}%".format(entry.predictedMediaLifeLeftPercent) if entry.predictedMediaLifeLeftPercent <> None else "", 4),
                self.truncateLengthy("  Yes" if entry.operation == DriveOperations.ENABLED else "", 8),
                self.truncateLengthy(scalable_pmem_config.drive_operation_description(entry), 20)))

        sys.stdout.write("\n\nScalable Persistent Memory supported: {} GiB".format(regions.maxPmemGiB))
        self.printBackupBootTimeMessage(scalable_pmem_config)

        self.noticeRestartRequired(scalable_pmem_config)
        sys.stdout.write(u"\n\n")


    def displayRegionConfiguration(self, scalable_pmem_config, output_as_json=False, print_backup_time_message=True):
        if output_as_json:
            data = {
                "TotalSupported" : scalable_pmem_config.regions.maxPmemGiB,
                "TotalAvailable" : scalable_pmem_config.regions.availableSizeGiB,
                "EstimatedBackupBootTimeSec" : scalable_pmem_config.regions.backupBootSec,
                "LogicalNVDIMMs" : {
                    "SingleProcessor" : [],
                    "Spanned" : []
                }
            }
            for region in scalable_pmem_config.regions.allRegions:
                if region.isFree:
                    continue
                region_data = {
                    'Index' : region.regionIndex,
                    'CurrentSize' : region.currentSizeGiB,
                    'PendingSize' : region.pendingSizeGiB,
                    'Operation' : scalable_pmem_config.region_operation_description(region)
                }
                if isinstance(region, NumaRegion):
                    region_data["Processor"] = region.parentSocket.labelString
                else:
                    region_data["Processors"] = region.parentSocketPair.labelString
                data["LogicalNVDIMMs"]["SingleProcessor" if isinstance(region, NumaRegion) else "Spanned"].append(region_data)
            UI().print_out_json(data)
        else:
            self.writeTableHeader(
                u"{:9}   {:18} {:22}  {:13}".format("Size", "Type", "Location", "Operation"))

            totalCount = 0
            for region in scalable_pmem_config.regions.allRegions:
                if region.isFree:
                    continue
                totalCount += 1
                sys.stdout.write(u"\n{:>9}   {:18} {:22}  {:13}".format(
                    "{} GiB".format(region.currentSizeGiB if region.operation == RegionOperations.REMOVE else region.pendingSizeGiB),
                    "Single Processor" if isinstance(region, NumaRegion) else "Spanned",
                    region.locationDescription,
                    scalable_pmem_config.region_operation_description(region)))
            if totalCount == 0:
                sys.stdout.write(u"\nNo logical NVDIMMs have been created\n")

            sys.stdout.write(u"\n")
            if print_backup_time_message:
                self.printBackupBootTimeMessage(scalable_pmem_config)
            self.noticeRestartRequired(scalable_pmem_config)
            sys.stdout.write(u"\n")



    def displayAvailableCapacity(self, scalable_pmem_config, output_as_json=False):
        if output_as_json:
            data = {
                "TotalSupported" : scalable_pmem_config.regions.maxPmemGiB,
                "TotalAvailable" : scalable_pmem_config.regions.availableSizeGiB,
                "Processor" : {},
                "ProcessorPair" : {}
            }
            for _, socket in scalable_pmem_config.regions.sockets.items():
                availableSize, isSlotAvailable = socket.availableSizeGiBHint
                data["Processor"][socket.labelString] = {
                    'AvailableSize' : availableSize,
                    'MaxLogicalNvdimmsCreated' : not isSlotAvailable,
                    'MaximumLogicalNvdimms' : socket.maxRegions
                }
            for _, pair in scalable_pmem_config.regions.socketPairs.items():
                availableSize, isSlotAvailable = pair.availableSizeGiBHint
                data["ProcessorPair"][pair.labelString] = {
                    'AvailableSize' : availableSize,
                    'MaxLogicalNvdimmsCreated' : not isSlotAvailable
                }
            UI().print_out_json(data)
        else:
            self.writeHeader3("By Processor (for single processor logical NVDIMMs):")
            self.writeTableHeader(
                u"{:12} {:40}".format("Processor", "Available For Scalable PMEM"))
            for _, socket in scalable_pmem_config.regions.sockets.items():
                availableSize, isSlotAvailable = socket.availableSizeGiBHint
                sys.stdout.write(u"\n  {:12} {}".format(
                    socket.labelString, "{:4} GiB {}".format(availableSize,
                    "(Max logical NVDIMMs created)" if not isSlotAvailable else "")))

            sys.stdout.write(u"\n")
            self.writeHeader3("By Processor Pair (for spanned logical NVDIMMs):")
            self.writeTableHeader(
                u"{:12} {:40}".format("Processors", "Available For Scalable PMEM"))
            for _, pair in scalable_pmem_config.regions.socketPairs.items():
                availableSize, isSlotAvailable = pair.availableSizeGiBHint
                sys.stdout.write(u"\n  {:12} {}".format(
                    pair.labelString, "{:4} GiB {}".format(availableSize,
                    "(Max logical NVDIMMs created)" if not isSlotAvailable else "")))

            self.noticeRestartRequired(scalable_pmem_config)
            sys.stdout.write(u"\n")



    def validateFeatureIsSupported(self, scalable_pmem_config, output_as_json=False):
        (isSupported, overallMessage, messages) = scalable_pmem_config.isFeatureSupported
        if not isSupported:
            if output_as_json:
                UI().print_out_json({
                    "IsSupported" : isSupported,
                    "OverallMessage" : overallMessage,
                    "Messages" : messages
                })
                raise NoChangesFoundOrMadeError(u"")
            else:
                sys.stdout.write(u"\n\n{}:\n".format(overallMessage))
                self.printLimitedMessageList(messages, 3)
                sys.stdout.write(u"\n\n")
                raise NoChangesFoundOrMadeError(u"Unable to continue")

    def validateFunctionalityIsEnabled(self, scalable_pmem_config, output_as_json=False):
        (isFuncEnabled, overallMessage, messages) = scalable_pmem_config.isFunctionalityEnabled
        if not isFuncEnabled:
            if output_as_json:
                UI().print_out_json({
                    "IsFunctionalityEnabled" : isFuncEnabled,
                    "OverallMessage" : overallMessage,
                    "Messages" : messages
                })
                raise NoChangesFoundOrMadeError(u"")
            else:
                sys.stdout.write(u"\n\n{}:\n".format(overallMessage))
                self.printLimitedMessageList(messages, 3)
                sys.stdout.write(u"\n\n")
                raise NoChangesFoundOrMadeError(u"Unable to continue")

    def validateFeatureEnabledByUser(self, scalable_pmem_config, output_as_json=False):
        (isEnabled, overallMessage, messages) = scalable_pmem_config.isEnabledByUser
        if not isEnabled:
            if output_as_json:
                UI().print_out_json({
                    "IsEnabled" : isEnabled,
                    "OverallMessage" : overallMessage,
                    "Messages" : messages
                })
                raise NoChangesFoundOrMadeError(u"")
            else:
                sys.stdout.write(u"\n\n{}:\n".format(overallMessage))
                self.printLimitedMessageList(messages, 3)
                sys.stdout.write(u"\n\n")
                raise NoChangesFoundOrMadeError(u"Unable to continue")



    def validateAllConfigurationPolicies(self, scalable_pmem_config, output_as_json=False):
        (isValid, overallMessage, messages) = scalable_pmem_config.validateConfigurationPolicies()
        if not isValid:
            if output_as_json:
                UI().print_out_json({
                    "IsValid" : isValid,
                    "OverallMessage" : overallMessage,
                    "Messages" : messages
                })
                raise NoChangesFoundOrMadeError(u"")
            else:
                sys.stdout.write(u"\n\n{}:\n".format(overallMessage))
                self.printLimitedMessageList(messages, 3)
                sys.stdout.write(u"\n\n")
                raise NoChangesFoundOrMadeError(u"Unable to continue")



    def displayOverallCapacityBarGraph(self, scalable_pmem_config, maxWidth):
        total = scalable_pmem_config.regions.maxPmemGiB
        available = scalable_pmem_config.regions.availableSizeGiB
        caption = u"{} GiB of {} GiB allocated ({} GiB available)".format(total - available, total, available)
        self.displayBarGraph(part=(total - available), total=total, caption=caption, max_width_chars=maxWidth)

    def printBackupBootTimeMessage(self, scalable_pmem_config):
        # only print if Logical NVDIMMs exist
        if scalable_pmem_config.hasConfiguredRegions:
            backupBootTime = scalable_pmem_config.regions.backupBootSec
            minutes, seconds = divmod(backupBootTime, 60)
            sys.stdout.write(u"\nEstimated total backup boot time for this configuration:")
            if minutes > 0:
                sys.stdout.write(u" {}m".format(minutes))
            sys.stdout.write(u" {}s".format(int(seconds)))
            sys.stdout.write(u"\n")

    def truncateLengthy(self, s, max_length):
        if s:
            if len(s) > max_length:
                return s[:(max_length - 2)] + ".."
            else:
                return s
        else:
            return ""



    def writeHeader1(self, s):
        sys.stdout.write(u"\n")
        sys.stdout.write(u"-" * len(s))
        sys.stdout.write(u"\n")
        sys.stdout.write(s)
        sys.stdout.write(u"\n")
        sys.stdout.write(u"-" * len(s))
        sys.stdout.write(u"\n\n")



    def writeHeader2(self, s):
        sys.stdout.write(u"\n")
        sys.stdout.write(s)
        sys.stdout.write(u"\n")
        sys.stdout.write(u"-" * len(s))
        sys.stdout.write(u"\n")



    def writeHeader3(self, s):
        sys.stdout.write(u"\n")
        sys.stdout.write(s)
        sys.stdout.write(u"\n")



    def writeTableHeader(self, s):
        self.writeHeader3(s)
        sys.stdout.write(u"-" * len(s))



    def displayBarGraph(self, part, total, caption, max_width_chars):
        if part > total:
            part = total
        if total == 0:
            filled = 0
        else:
            filled = (part / float(total))
        total_bar_width = int((max_width_chars - 2) * filled)
        sys.stdout.write(u".")
        sys.stdout.write(u"-" * (max_width_chars - 2))
        sys.stdout.write(u".\n")
        sys.stdout.write(u"|")
        sys.stdout.write(u"|" * total_bar_width)
        sys.stdout.write(u" " * (max_width_chars - total_bar_width - 2))
        sys.stdout.write(u"|\n")
        sys.stdout.write(u"'")
        sys.stdout.write(u"-" * (max_width_chars - 2))
        sys.stdout.write(u"'\n")
        sys.stdout.write(u"{caption}\n".format(caption=caption))



    def printLimitedMessageList(self, messages, limit):
        excessCount = len(messages) - limit
        current = 0
        for message in messages:
            current += 1
            sys.stdout.write(u"[{}] {}\n".format(current, message))
            if current >= limit:
                break
        if excessCount > 0:
            sys.stdout.write(u"({} more)\n".format(excessCount))



    def gethprestchifhandle(self):
        """ Load the chif hprest library
        """
        try:
            lib = BlobStore2.gethprestchifhandle()
        except Exception as excp:
            lib = None
        return lib



    def unloadchifhandle(self, lib):
        """Release a handle on the chif hprest library

        :param lib: The library handle provided by loading the chif library.
        :type lib: library handle.
        """
        BlobStore2.unloadchifhandle(lib)
