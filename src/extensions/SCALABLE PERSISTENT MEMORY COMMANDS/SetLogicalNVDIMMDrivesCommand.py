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

""" Set Backup Devices Command """

import sys

from optparse import OptionParser, OptionGroup

from lib.Helpers import Helpers
from lib.RestHelpers import RestHelpers
from lib.LogicalNvdimmValidator import LogicalNvdimmValidator
from lib.ScalablePersistentMemoryConfig import ScalablePersistentMemoryConfig

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, \
                    InvalidCommandLineError, NoChangesFoundOrMadeError, LOGGER

class SetLogicalNVDIMMDrivesCommand(RdmcCommandBase):
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self, \
            name='setbackupdevices', \
            usage='setbackupdevices (--device=ID... | --remove-all)\n\n'\
                '\tSelect the devices to use for Scalable Persistent Memory '\
                'backup storage.\n\n\texample: setbackupdevices --device=1@1 '\
                '--device=1@2', \
            summary='Set backup storage devices.', \
            aliases=['spmem-setdrives', 'spmsetd', 'setbackupdrives'], \
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self._helpers = Helpers()
        self._restHelpers = RestHelpers(self._rdmc)
        self._validator = LogicalNvdimmValidator()
        self._chif_lib = self._helpers.gethprestchifhandle()

    def common_setup(self):
        """ function to get the config setup """
        scalable_pmem_config = ScalablePersistentMemoryConfig(self._restHelpers, \
                                                 self._validator, self._chif_lib)
        scalable_pmem_config.refresh()

        # pre-validation
        self._helpers.validateAllConfigurationPolicies(scalable_pmem_config)

        return scalable_pmem_config

    def removeAllDrives(self):
        """ setlogicalnvdimmdrives command worker function """

        scalable_pmem_config = self.common_setup()

        if scalable_pmem_config.hasConfiguredRegions:
            raise NoChangesFoundOrMadeError(u"Backup drives cannot be removed "\
                                        "while logical NVDIMMs are configured")

        self._restHelpers.setDrives(old_drives=scalable_pmem_config.drives.selectedDrives)
        #self._restHelpers.enableConfiguration()

        scalable_pmem_config.refresh()
        self._helpers.displayDrivesConfiguration(scalable_pmem_config)

        return ReturnCodes.SUCCESS



    def setDrives(self, options=None):
        """ Main setlogicalnvdimmdrives command worker function

        :param options: command options
        :type options: options.
        """

        drivesToUse = []

        if not options.driveId:
            raise InvalidCommandLineError(u"No device IDs specified")

        if len(options.driveId) > len(set(options.driveId)):
            raise InvalidCommandLineError(u"Duplicate device IDs specified")

        scalable_pmem_config = self.common_setup()

        for userProvidedId in options.driveId:
            matchingDrive = scalable_pmem_config.drives.findDrive(userProvidedId)
            if not matchingDrive:
                raise InvalidCommandLineError(u"Invalid device ID: {}".format(userProvidedId))
            drivesToUse.append(matchingDrive)

        if scalable_pmem_config.hasConfiguredRegions:
            # allow drives to be added but not removed
            if not set(scalable_pmem_config.drives.selectedDrives).issubset(drivesToUse):
                raise NoChangesFoundOrMadeError(u"Backup devices cannot be "\
                                "removed while logical NVDIMMs are configured")

        # check the configuration policies
        (isValidDrivePolicies, drivePoliciesMessage) = self._validator.\
                checkLogicalNvdimmDrivePolicies(scalable_pmem_config.config_resource,\
                                                                    drivesToUse)
        if not isValidDrivePolicies:
            sys.stdout.write(u"\nThe set of devices specified is not a valid configuration:\n")
            sys.stdout.write(drivePoliciesMessage)
            sys.stdout.write(u"\n\n")
            raise NoChangesFoundOrMadeError(u"Unable to continue")

        # calculate maximum persistent memory supported
        maxPmem = self._validator.calculateMaxPmemGiB(self._chif_lib, scalable_pmem_config.\
                                                      config_resource, drivesToUse)
        # compare this to the TOTAL of the pmem regions in the current/pending settings
        totalPmemAllocated = scalable_pmem_config.regions.totalSizeGiB
        if totalPmemAllocated != 0 and maxPmem < totalPmemAllocated:
            sys.stdout.write(u"\nThe set of devices specified is not a valid configuration:\n")
            sys.stdout.write(
                u"\nScalable Persistent Memory supported by requested configuration: {} GiB" \
                            u"\nAllocated Scalable Persistent Memory: {} GiB.".\
                                            format(maxPmem, totalPmemAllocated))
            sys.stdout.write(u"\n\n")
            raise NoChangesFoundOrMadeError(u"Unable to continue")

        # if all is valid, configure the related BIOS setting
        if self._rdmc.interactive:
            self._helpers.confirmBeforeConfigCausesDataLoss(scalable_pmem_config)

        self._restHelpers.setDrives(new_drives=drivesToUse, old_drives=scalable_pmem_config.\
                                                            drives.selectedDrives)

        scalable_pmem_config.refresh()
        self._helpers.displayDrivesConfiguration(scalable_pmem_config)

        return ReturnCodes.SUCCESS



    def run(self, line):
        """ Wrapper function for setbackupdrives command main function

        :param line: command line input
        :type line: string.
        """
        LOGGER.info("Scalable PMEM: {}".format(self.name))
        try:
            (options, _) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        LOGGER.info("Options: {}".format(options))

        if not self._chif_lib:
            self._helpers.failNoChifLibrary()

        if options.removeAll and options.driveId:
            raise InvalidCommandLineError(u"--device and --remove-all may not "\
                                                        "be used at the same time")
        if options.removeAll:
            return self.removeAllDrives()
        else:
            return self.setDrives(options)

    def definearguments(self, customparser):
        """ Define arguments for the command

        :param customparser: command line input
        :type customparser: parser.
        """

        groupDanger = OptionGroup(customparser, "Dangerous Options", \
            "Use of these options will alter the backup storage devices configured\n" \
            "for use with Scalable Persistent Memory and could cause data loss. " \
            " Back up all\ndata first.")

        groupDanger.add_option(
            '--device',
            '--drive',
            action="append",
            dest="driveId",
            metavar="ID",
            help="ID of the backup device to set, e.g. '1@1'"
        )

        groupDanger.add_option(
            '--remove-all',
            action="store_true",
            dest="removeAll",
            help="Remove all currently-configured backup devices"
        )

        customparser.add_option_group(groupDanger)
