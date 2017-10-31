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

""" Revert Scalable Persistent Memory Configuration Command """

import sys
from optparse import OptionParser
from lib.Helpers import Helpers
from lib.RestHelpers import RestHelpers
from lib.LogicalNvdimmValidator import LogicalNvdimmValidator
from lib.ScalablePersistentMemoryConfig import ScalablePersistentMemoryConfig
from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, LOGGER

class RevertScalablePmemConfigurationCommand(RdmcCommandBase):
    """ Main revertscalablepmemconfig command class """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self, \
            name='revertscalablepmemconfig', \
            usage='revertscalablepmemconfig\n\n'\
                '\tDiscards any pending Scalable Persistent Memory configuration '\
                'changes.\n\n\texample: revertscalablepmemconfig', \
            summary='Discard pending Scalable Persistent Memory configuration changes.',\
            aliases=['spmem-revertcfg', 'spmem-undocfg', 'spmemrc'], \
            optparser=OptionParser())

        self._rdmc = rdmcObj
        self._helpers = Helpers()
        self._restHelpers = RestHelpers(self._rdmc)
        self._validator = LogicalNvdimmValidator()
        self._chif_lib = self._helpers.gethprestchifhandle()

    def revertPendingChanges(self):
        """ Reverts any pending changes """

        scalable_pmem_config = ScalablePersistentMemoryConfig(self._restHelpers,\
                                             self._validator, self._chif_lib)
        scalable_pmem_config.refresh()

        self._restHelpers.revertSettings()

        scalable_pmem_config.refresh()

        self._helpers.writeHeader2(u"Logical NVDIMMs")
        self._helpers.displayRegionConfiguration(scalable_pmem_config)
        self._helpers.writeHeader2(u"Scalable Persistent Memory Backup Storage Devices")
        self._helpers.displayDrivesConfiguration(scalable_pmem_config)

        sys.stdout.write("\n\n")

    def run(self, line):
        """ Wrapper function for the revert configuration command

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

        self.revertPendingChanges()

        #Return code
        return ReturnCodes.SUCCESS
