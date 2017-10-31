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

""" Remove Logical NVDIMM Command """

import sys

from optparse import OptionParser, OptionGroup

from lib.Helpers import Helpers
from lib.RestHelpers import RestHelpers
from lib.LogicalNvdimmValidator import LogicalNvdimmValidator
from lib.ScalablePersistentMemoryConfig import ScalablePersistentMemoryConfig

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
                InvalidCommandLineErrorOPTS, LOGGER

class RemoveLogicalNVDIMMRegionCommand(RdmcCommandBase):
    """ Main removelogicalnvdimm command class """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self, \
            name='removelogicalnvdimm', \
            usage='removelogicalnvdimm (--processor=NUMBER --index=INDEX | '\
            '--pair=PAIR)\n\n\tRemove a logical NVDIMM. All data will be lost.\n'\
            '\n\texample: removelogicalnvdimm --processor=1 --index=1'\
            '\n\texample: removelogicalnvdimm --processors=1,2', \
            summary='Remove an existing logical NVDIMM.', \
            aliases=['lnvdimm-remove', 'lnr'], \
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self._helpers = Helpers()
        self._restHelpers = RestHelpers(self._rdmc)
        self._chif_lib = self._helpers.gethprestchifhandle()

    def removeRegion(self, options):
        """ Removes the Logical NVDIMM specified

        :param socketIdx: the socket of the NUMA region, or None for Non-NUMA
        :type socketIdx: string or int

        :param regionIdx: the index of the region
        :type regionIdx: string or int
        """

        validator = LogicalNvdimmValidator()

        scalable_pmem_config = ScalablePersistentMemoryConfig(self._restHelpers,\
                                                     validator, self._chif_lib)
        scalable_pmem_config.refresh()

        # pre-validation
        self._helpers.validateAllConfigurationPolicies(scalable_pmem_config)

        matchingRegion = None
        if options.processorPair:
            matchingPair = next((p for _, p in scalable_pmem_config.regions.\
                                 socketPairs.items() if p.labelString == options.\
                                                            processorPair), None)
            if matchingPair:
                matchingRegion = matchingPair.nonNumaRegion
        else:
            matchingSocket = next((s for _, s in scalable_pmem_config.regions.\
                                   sockets.items() if s.labelString == options.\
                                                        processorNumber), None)
            if matchingSocket:
                matchingRegion = matchingSocket.numaRegions.get(options.index)

        if matchingRegion and matchingRegion.isConfigured:
            if self._rdmc.interactive:
                if matchingRegion.isActivelyConfigured:
                    self._helpers.confirmBeforeConfigCausesDataLoss(scalable_pmem_config)

            patchAttributes = {
                matchingRegion.settingName : 0
            }
            _ = self._restHelpers.patchScalablePmemSettingAttributes(patchAttributes)
        else:
            self._helpers.displayRegionConfiguration(scalable_pmem_config)
            raise InvalidCommandLineError(u"Unable to identify an existing logical NVDIMM")

        # display the new state
        scalable_pmem_config.refresh()
        self._helpers.displayRegionConfiguration(scalable_pmem_config)
        sys.stdout.write(u"\n")



    def run(self, line):
        """ Wrapper function for the Remove logical NVDIMM command

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

        if not options.processorNumber and not options.processorPair:
            self.parser.print_help()
            raise InvalidCommandLineError(u"One of --processor or --processors"\
                                                                " is required")

        if options.processorNumber and options.processorPair:
            self.parser.print_help()
            raise InvalidCommandLineError(u"--processor and --processors may not"\
                                                        " be used at the same time")

        if options.processorNumber:
            if options.index is None:
                self.parser.print_help()
                raise InvalidCommandLineError(u"--index must be specified with "\
                                                                    "--processor")
            self.removeRegion(options)

        if options.processorPair:
            if not options.index is None:
                self.parser.print_help()
                raise InvalidCommandLineError(u"--index is not a valid option to"\
                                                        " use with --processors")
            self.removeRegion(options)

        #Return code
        return ReturnCodes.SUCCESS

    def definearguments(self, customparser):
        """ Define the arguments in the remove region function

        :param customparser: command line input
        :type customparser: parser.
        """

        groupDanger = OptionGroup(customparser, "Dangerous Options", \
            "Use of these options will alter the backup storage devices configured\n" \
            "for use with Scalable Persistent Memory and could cause data loss.  "\
            "Back up all\ndata first.")

        groupDanger.add_option(
            '--proc',
            '--processor',
            action="store",
            type="string",
            default=None,
            dest="processorNumber",
            metavar="NUMBER",
            help="Specify the processor number of the logical NVDIMM to remove (1, 2)"
        )

        groupDanger.add_option(
            '-i',
            '--index',
            type="int",
            default=None,
            dest="index",
            help="Specify the index of the logical NVDIMM to remove (use with --processor)")

        groupDanger.add_option(
            '--pair',
            '--processors',
            action="store",
            type="string",
            default=None,
            dest="processorPair",
            metavar="PAIR",
            help="Specify the pair of processors of the spanned logical NVDIMM to remove (1,2)"
            )

        customparser.add_option_group(groupDanger)
