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
""" Auto Select Backup Devices Command """

import sys
from optparse import OptionParser, OptionGroup

from jsonpointer import resolve_pointer

from lib.Helpers import Helpers
from lib.RestHelpers import RestHelpers
from lib.ScalablePersistentMemoryConfig import ScalablePersistentMemoryConfig
from lib.LogicalNvdimmValidator import LogicalNvdimmValidator

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, \
                        InvalidCommandLineError, NoChangesFoundOrMadeError, \
                        LOGGER

class AutoSelectBackupDevicesCommand(RdmcCommandBase):
    """ Main autoselectbackupdevices command class """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='autoselectbackupdevices', \
            usage='autoselectbackupdevices --size=SIZE [--confirm]\n\n'\
            '\tAutomatically select the devices for use as Scalable '\
            'Persistent Memory backup storage.\n\n'\
            "\tDevices selected for backup storage will be initialized.\n"\
            "\tBack up all data first.\n" \
            '\n\texample: autoselectbackupdevices --size=1024 --confirm\n', \
            summary='Automatically select backup storage devices.', \
            aliases=['spmem-autosetd', 'spmemautosetd'],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self._helpers = Helpers()
        self._restHelpers = RestHelpers(self._rdmc)
        self._validator = LogicalNvdimmValidator()
        self._chif_lib = self._helpers.gethprestchifhandle()

    def autoselectdrives(self, pmem_size_GiB, confirm):
        """ function to perform the automatic selection of backup drives

        :param pmem_size_GiB: requested scalable persistent memory size
        :type pmem_size_GiB: int

        :param confirm: whether or not to automatically confirm the selected drives
        :type confirm: Boolean
        """

        scalable_pmem_config = ScalablePersistentMemoryConfig(self._restHelpers,\
                                             self._validator, self._chif_lib)
        scalable_pmem_config.refresh()

        # pre-validation
        self._helpers.validateAllConfigurationPolicies(scalable_pmem_config)

        # make sure this is an un-configured system
        if scalable_pmem_config.isConfiguredSystem:
            raise InvalidCommandLineError(u"This operation is not supported on "\
                                                        "a configured system")

        # get policies
        policies = resolve_pointer(scalable_pmem_config.config_resource, \
                                                    "/Attributes/Policy", None)
        sameModel = False
        sameSize = False
        if policies:
            sameModel = policies.get("SameModelNVMe", False)
            sameSize = policies.get("SameSizeNVMe", False)

        # separate the supported drives into supported groups, based on model or size
        # if same model or size, then order doesn't matter; else the
        # drives should be sorted largest to smallest
        supported_drives_groups = self.sort_drives(sameModel, sameSize, \
                                    scalable_pmem_config.drives.supportedDrives)

        # loop through the group until a valid config is found or all drives
        # have been tested
        isValid = False
        i = 0
        num_groups = len(supported_drives_groups)
        while not isValid and i < num_groups:
            drive_group = supported_drives_groups[i]
            drivesToUse = []
            for drive in drive_group:
                drivesToUse.append(drive)
                # calculate the maximum supported by the new configuration,
                # which may be different from the requested capacity
                max_pmem_supported = self._validator.calculateMaxPmemGiB(\
                        self._chif_lib, scalable_pmem_config.config_resource, \
                        drivesToUse)
                if max_pmem_supported >= pmem_size_GiB:
                    # check drive policies
                    (isValidDrivePolicies, _) = self._validator.\
                            checkLogicalNvdimmDrivePolicies(scalable_pmem_config.\
                            config_resource, drivesToUse)
                    if isValidDrivePolicies:
                        isValid = True
                        break
            i += 1

        if not isValid:
            # TODO: more info? maybe build a list of reasons why certain drives will not work
            raise InvalidCommandLineError(u"Requested size of {} GiB is not "\
                                          "supported by the installed backup "\
                                          "devices".format(pmem_size_GiB))

        # get a list of the drives to show to the user
        summary_drive_list = ["{:15} ({} GB)".format(d.formattedLocation, \
                                                d.sizeGB) for d in drivesToUse]

        # Make sure the user confirms the changes
        sys.stdout.write(u"\nThe following backup devices have been "\
                                "automatically selected for Scalable PMEM:\n")
        self._helpers.printLimitedMessageList(summary_drive_list, 99)
        sys.stdout.write(u"\n")

        if not confirm:
            if self._rdmc.interactive:
                # TODO: timeout
                s = raw_input(u"\nConfirm changes? Y(y) to confirm. N(n) to cancel: ")
                if s == 'y' or s == 'Y':
                    confirm = True
                else:
                    raise NoChangesFoundOrMadeError(u"No changes have been made")
            else:
                raise NoChangesFoundOrMadeError(u"No changes have been made.  "\
                                    "To confirm the changes, specify --confirm")

        if confirm:
            # if all is valid, configure the related BIOS setting
            self._restHelpers.setDrives(new_drives=drivesToUse)
            #self._restHelpers.enableConfiguration()
            scalable_pmem_config.refresh()
            self._helpers.displayDrivesConfiguration(scalable_pmem_config)


    def sort_drives(self, sameModel, sameSize, supported_drives):
        """ sort drives into separate groups based on model or size.
        if same model or size, then order doesn't matter
        else the drives are sorted largest to smallest size

        :param sameModel: specifies if drives need to be the same model
        :type sameModel: Boolean

        :param sameSize: specifies is drives need to be the same size, model takes precedence
        :type sameSize: Boolean

        :param supported_drives: list of all supported drives
        :type supported_drives: list of Drives

        :returns: 2D list of supported drives, where a row is a group of """\
        """drives based on model or size
        :rtype: 2D list of Drive
        """
        supported_drives_groups = [] # 2D Array, row=model or size
        if sameModel:
            # separate drives by model
            # for each model, build a list of drives
            models = set([drive.model for drive in supported_drives])
            for model_to_find in models:
                drive_model_group = [drive for drive in supported_drives if \
                                                    drive.model == model_to_find]
                supported_drives_groups.append(drive_model_group)

        elif sameSize:
            # separate drives by size
            sizes = set([drive.sizeMB for drive in supported_drives])
            for size_to_find in sizes:
                drive_size_group = [drive for drive in supported_drives if \
                                                    drive.sizeMB == size_to_find]
                supported_drives_groups.append(drive_size_group)
        else:
            # contains one list of all supported drives, regardless of size or model
            # sort by the size, descending from largest to smallest
            sorted_supported_drives = sorted(supported_drives, key=lambda d: d.sizeMB,\
                                                                 reverse=True)
            supported_drives_groups.append(sorted_supported_drives)

        return supported_drives_groups

    def run(self, line):
        """ Wrapper function for new command main function

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

        if options.size <= 0:
            self.parser.print_help()
            raise InvalidCommandLineError("Invalid value for --size")

        self.autoselectdrives(options.size, options.confirm)

        #Return code
        return ReturnCodes.SUCCESS

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """

        customparser.add_option(
            '--size',
            '-s',
            dest='size',
            default=-1,
            action="store",
            help="Amount (in GiB) of Scalable Persistent Memory to be supported"\
                            " by the new backup storage device configuration.",
            type="int"
        )

        groupDanger = OptionGroup(customparser, "Dangerous Options", \
            "Use of these options will alter the Scalable Persistent Memory " \
            "configuration\nand will cause data loss.  Back up all data first.")

        groupDanger.add_option(
            '--confirm',
            action="store_true",
            default=False,
            dest="confirm",
            help="Confirm the configuration of the automatically selected backup"\
                            " devices. If not specified, no changes will occur."
        )

        customparser.add_option_group(groupDanger)
