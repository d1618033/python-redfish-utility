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
""" Replace Backup Device Command """

import sys
from optparse import OptionParser

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, \
                            InvalidCommandLineError, NoChangesFoundOrMadeError

from lib.Drives import Drive
from lib.Helpers import Helpers
from lib.RestHelpers import RestHelpers
from lib.LogicalNvdimmValidator import LogicalNvdimmValidator
from lib.ScalablePersistentMemoryConfig import ScalablePersistentMemoryConfig

class ReplaceBackupDeviceCommand(RdmcCommandBase):
    """ Main replacebackupdevice command class """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self, \
        name='replacebackupdevice', \
        usage="replacebackupdevice OLD-ID NEW-ID\n"\
            "\n\tReplace a Scalable Persistent Memory backup storage device.\n"\
            "\tSpecify devices by ID, e.g. '1@1' from the show backup device command.\n"\
            "\n\tThis operation initializes all backup storage devices."\
            "\n\tData on any existing logical NVDIMMs will be lost. Back up all data first.\n"\
            "\n\texample: replacebackupdevice 1@1 2@1", \
        summary='Replace a backup storage device.', \
        aliases=['spmem-replaced', 'spmreplaced'], \
        optparser=OptionParser())

        self._rdmc = rdmcObj
        self._helpers = Helpers()
        self._rest_helpers = RestHelpers(self._rdmc)
        self._validator = LogicalNvdimmValidator()
        self._chif_lib = self._helpers.gethprestchifhandle()

    def run(self, line):
        """ Runs the command.

        :param line: command line input
        :type line: string
        """
        try:
            (_, args) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        if not args or len(args) != 2:
            self.print_help()
            sys.stdout.write("\n")
            raise InvalidCommandLineError(u"OLD-ID and NEW-ID must be specified")

        if len(args) != len(set(args)):
            raise InvalidCommandLineError(u"Duplicate device IDs specified")

        if not self._chif_lib:
            self._helpers.failNoChifLibrary()

        scalable_pmem_config = ScalablePersistentMemoryConfig(self._rest_helpers,\
                                                 self._validator, self._chif_lib)
        scalable_pmem_config.refresh()

        # pre-validation
        self._helpers.validateFeatureIsSupported(scalable_pmem_config)
        self._helpers.validateFeatureEnabledByUser(scalable_pmem_config)

        try:
            old_drive, new_drive = scalable_pmem_config.drives.findDrives(args)
        except ValueError as excp:
            raise InvalidCommandLineError(u"Invalid device ID: {}".format(excp))

        self.replace_drive(scalable_pmem_config, old_drive, new_drive)

        scalable_pmem_config.refresh()
        self._helpers.displayDrivesConfiguration(scalable_pmem_config)

        return ReturnCodes.SUCCESS

    def replace_drive(self, scalable_pmem_config, old_drive, new_drive):
        """ Replaces a backup storage drive.

        :param scalable_pmem_config: the Scalable Persistent Memory configuration
        :param old_drive: the drive to be replaced
        :param new_drive: the replacement drive
        """
        backup_drives = scalable_pmem_config.drives.selectedDrives

        if old_drive not in backup_drives:
            raise NoChangesFoundOrMadeError(u"Device {} is not configured "\
                            "for backup storage".format(old_drive.generatedId))

        if new_drive in backup_drives:
            raise NoChangesFoundOrMadeError(u"Device {} is already configured " \
                            "for backup storage".format(new_drive.generatedId))

        backup_drives.remove(old_drive)
        backup_drives.append(new_drive)

        config_data = scalable_pmem_config.config_resource

        # new backup storage drives must adhere to the drive policy requirements
        is_valid, error_msg = self._validator.checkLogicalNvdimmDrivePolicies(\
                                                    config_data, backup_drives)
        if not is_valid:
            raise NoChangesFoundOrMadeError(error_msg)

        # new backup storage drives must support the current logical NVDIMM configuration
        max_pmem = self._validator.calculateMaxPmemGiB(self._chif_lib, \
                                                    config_data, backup_drives)
        allocated_pmem = scalable_pmem_config.regions.totalSizeGiB

        if allocated_pmem > max_pmem:
            raise NoChangesFoundOrMadeError(u"The new backup storage devices must support "
                                            u"the current logical NVDIMM configuration.")

        if old_drive.currentMode == Drive.MODE_NVDIMM and scalable_pmem_config.\
                                                    hasActiveConfiguredRegions:
            # actual drive replacement occurring with data at risk
            if self._rdmc.interactive:
                sys.stdout.write(u"\nAll backup storage devices will be initialized upon restart."
                                 u"\nData on any existing logical NVDIMMs will be lost.\n")

                uinput = raw_input(u"\nConfirm changes [y/N]? ")
                if uinput.lower() != 'y':
                    raise NoChangesFoundOrMadeError(u"No changes have been made")

        self._rest_helpers.setDrives(new_drives=[new_drive], old_drives=[old_drive])
