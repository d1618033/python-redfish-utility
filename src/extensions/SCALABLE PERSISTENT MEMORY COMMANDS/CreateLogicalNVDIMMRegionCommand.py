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

""" Create Logical NVDIMM Command """

import sys
from optparse import OptionParser, OptionGroup

from lib.Helpers import Helpers
from lib.ScalablePersistentMemoryConfig import ScalablePersistentMemoryConfig
from lib.RestHelpers import RestHelpers
from lib.LogicalNvdimmValidator import LogicalNvdimmValidator

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, \
                    InvalidCommandLineError, NoChangesFoundOrMadeError, LOGGER

class CreateLogicalNVDIMMRegionCommand(RdmcCommandBase):
    """ Main createlogicalnvdimm command class """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self, \
            name='createlogicalnvdimm', \
            usage='createlogicalnvdimm --size=SIZE [--processor=NUMBER | '\
            '--pair=PAIR]\n\n\tCreate a logical NVDIMM.\n\n' \
            '\texample: createlogicalnvdimm --processor=auto --size=100', \
            summary='Create a logical NVDIMM.', \
            aliases=['lnvdimm-create', 'lnc'], \
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self._helpers = Helpers()
        self._restHelpers = RestHelpers(self._rdmc)
        self._validator = LogicalNvdimmValidator()
        self._chif_lib = self._helpers.gethprestchifhandle()

    def common_setup(self):
        """ function to get the config setup """
        scalable_pmem_config = ScalablePersistentMemoryConfig(self._restHelpers,\
                                                 self._validator, self._chif_lib)
        scalable_pmem_config.refresh()

        # pre-validation
        self._helpers.validateAllConfigurationPolicies(scalable_pmem_config)

        return scalable_pmem_config

    def createAutoRegion(self, options=None):
        """ function to auto create region

        :param options: list of options
        :type options: list.
        """
        scalable_pmem_config = self.common_setup()

        # try NUMA first
        selectedSocket = None
        matchingRegion = None
        for _, socket in scalable_pmem_config.regions.sockets.items():
            firstRegion = socket.firstZeroSizeRegion
            if firstRegion and socket.availableSizeGiB >= options.size:
                selectedSocket = socket
                matchingRegion = firstRegion
                break
        if matchingRegion:
            sys.stdout.write(u"Creating a {} GiB logical NVDIMM...\n".format(\
                                                                    options.size))
            options.processorNumber = selectedSocket.labelString
            return self.createNumaRegion(options)

        # try non-NUMA
        selectedSocketPair = None
        for _, socketPair in scalable_pmem_config.regions.socketPairs.items():
            if socketPair.nonNumaRegion.pendingSizeGiB == 0 and socketPair.\
                                                availableSizeGiB >= options.size:
                selectedSocketPair = socketPair
                break
        if selectedSocketPair:
            sys.stdout.write(u"Creating a {} GiB spanned logical NVDIMM...\n".\
                                                            format(options.size))
            options.processorPair = selectedSocketPair.labelString
            return self.createNonNumaRegion(options)

        raise NoChangesFoundOrMadeError(u"No space is available to create a "\
                                        "logical NVDIMM of the requested size.")

    def createNumaRegion(self, options=None):
        """ function to create logical NVDIMM

        :param options: list of options
        :type options: list.
        """
        scalable_pmem_config = self.common_setup()

        matchingSocket = None
        matchingRegion = None
        if options.processorNumber == "auto":
            # find first 0 size
            matchingSocket, matchingRegion = scalable_pmem_config.regions.\
                                                            firstZeroSizeRegion
        else:
            # find the first 0 size for the specified processor
            matchingSocket = next((s for _, s in scalable_pmem_config.regions.\
                sockets.items() if s.labelString == options.processorNumber), None)
            if matchingSocket:
                matchingRegion = matchingSocket.firstZeroSizeRegion

        if not matchingRegion:
            self._helpers.displayRegionConfiguration(scalable_pmem_config)
            sys.stdout.write(u"\n\n")
            raise NoChangesFoundOrMadeError(u"\n\nNo available entries remain "\
                                            "to create the logical NVDIMM")

        # insert the test data
        matchingRegion.pendingSizeGiB = options.size

        isValid, validationMessage = scalable_pmem_config.regions.isValidConfiguration

        if isValid:
            if self._rdmc.interactive:
                self._helpers.confirmBeforeConfigCausesDataLoss(scalable_pmem_config)

            patchAttributes = {
                matchingRegion.settingName : options.size
            }
            response = self._restHelpers.patchScalablePmemSettingAttributes(patchAttributes)
            #self._restHelpers.enableConfiguration()
        else:
            sys.stdout.write(u"\nThe logical NVDIMM requested is not a valid configuration:\n")
            sys.stdout.write(validationMessage)
            sys.stdout.write(u"\n")
            raise NoChangesFoundOrMadeError("No changes made")

        # display the new state
        scalable_pmem_config.refresh()
        self._helpers.displayRegionConfiguration(scalable_pmem_config)

        sys.stdout.write(u"\n\n")

    def createNonNumaRegion(self, options=None):
        """ function to create spanned logical NVDIMM

        :param options: list of options
        :type options: list.
        """

        scalable_pmem_config = self.common_setup()

        matchingRegion = None
        if options.processorPair == "auto":
            # find first 0 size
            matchingRegion = scalable_pmem_config.regions.firstZeroSizeNonNumaRegion
        else:
            # find the region for the specified socket-pair
            socketPair = next((p for _, p in scalable_pmem_config.regions.\
                               socketPairs.items() if p.labelString == options.\
                                                            processorPair), None)
            if socketPair:
                matchingRegion = socketPair.nonNumaRegion
                if matchingRegion.isFree:
                    pass
                else:
                    matchingRegion = None

        if not matchingRegion:
            self._helpers.displayRegionConfiguration(scalable_pmem_config)
            sys.stdout.write(u"\n\n")
            raise NoChangesFoundOrMadeError("No available entries remain to "\
                                            "create the spanned logical NVDIMM")

        # insert the test data
        matchingRegion.pendingSizeGiB = options.size

        isValid, validationMessage = scalable_pmem_config.regions.isValidConfiguration

        if isValid:
            if self._rdmc.interactive:
                self._helpers.confirmBeforeConfigCausesDataLoss(scalable_pmem_config)

            patchAttributes = {
                matchingRegion.settingName : options.size
            }
            _ = self._restHelpers.patchScalablePmemSettingAttributes(patchAttributes)
        else:
            sys.stdout.write(u"\nThe logical NVDIMM requested is not a valid configuration:\n")
            sys.stdout.write(validationMessage)
            sys.stdout.write(u"\n")
            raise NoChangesFoundOrMadeError("No changes made")

        # display the new state
        scalable_pmem_config.refresh()
        self._helpers.displayRegionConfiguration(scalable_pmem_config)

        sys.stdout.write(u"\n\n")

    def run(self, line):
        """ Wrapper function for createlogicalnvdimm command main function

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

        if options.size is None:
            self.parser.print_help()
            sys.stdout.write(u"\n")
            raise InvalidCommandLineError(u"--size is required")

        if options.size < 1:
            self.parser.print_help()
            sys.stdout.write(u"\n")
            raise InvalidCommandLineError(u"Invalid value for --size")

        if options.processorNumber and options.processorPair:
            self.parser.print_help()
            sys.stdout.write(u"\n")
            raise InvalidCommandLineError(u"--processor and --processors may "\
                                          "not be used at the same time")

        if options.processorNumber:
            if options.processorNumber not in ["auto", "1", "2", "3", "4"]:
                self.parser.print_help()
                sys.stdout.write(u"\n")
                raise InvalidCommandLineError(u"Invalid value for --processor")

        if options.processorPair:
            if options.processorPair not in ["auto", "1,2", "3,4"]:
                self.parser.print_help()
                sys.stdout.write(u"\n")
                raise InvalidCommandLineError(u"Invalid value for --processors")

        if options.processorNumber:
            self.createNumaRegion(options)
        elif options.processorPair:
            self.createNonNumaRegion(options)
        else:
            self.createAutoRegion(options)

        return ReturnCodes.SUCCESS

    def definearguments(self, customparser):
        """ Defines argument for the command

        :param customparser: command line input
        :type customparser: parser.
        """

        groupDanger = OptionGroup(customparser, "Dangerous Options",\
            "Use of these options will alter the backup storage devices configured\n" \
            "for use with Scalable Persistent Memory and could cause data loss.  Back up all\n" \
            "data first.")

        groupDanger.add_option(
            '--size',
            type="int",
            action="store",
            dest="size",
            help="Specify the size (GiB) of the logical NVDIMM to create."
        )

        groupDanger.add_option(
            '--proc',
            '--processor',
            action="store",
            type="string",
            default=None,
            dest="processorNumber",
            metavar="NUMBER",
            help="Use to create a logical NVDIMM. Specify the processor (auto, 1, 2)."
        )

        groupDanger.add_option(
            '--pair',
            '--processors',
            action="store",
            type="string",
            default=None,
            dest="processorPair",
            metavar="PAIR",
            help="Use to create a spanned logical NVDIMM.  Specify the pair of "\
                                                        "processors (auto or 1,2)."
        )

        customparser.add_option_group(groupDanger)
