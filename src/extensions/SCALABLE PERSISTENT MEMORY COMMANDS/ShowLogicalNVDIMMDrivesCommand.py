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

""" Show Backup Devices Command """

import sys

from optparse import OptionParser

from lib.Helpers import Helpers
from lib.RestHelpers import RestHelpers
from lib.LogicalNvdimmValidator import LogicalNvdimmValidator
from lib.ScalablePersistentMemoryConfig import ScalablePersistentMemoryConfig

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, \
                                                InvalidCommandLineError, LOGGER

class ShowLogicalNVDIMMDrivesCommand(RdmcCommandBase):
    """ Main showbackupdevices command class """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self, \
            name='showbackupdevices', \
            usage='showbackupdevices\n\n\tDisplay the devices supported for use '\
            'as Scalable Persistent Memory\n\tbackup storage.\n\n\texample: '\
            'showbackupdevices', \
            summary='Display backup storage devices.', \
            aliases=['spmem-showdrives', 'spmemsd', 'showscalablepmemdrives'], \
            optparser=OptionParser())
        self._rdmc = rdmcObj
        self._helpers = Helpers()
        self._chif_lib = self._helpers.gethprestchifhandle()

    def showDriveData(self):
        """ Main showlogicalnvdimmdrives command worker function

        :param options: command options
        :type options: options.
        """

        helpers = Helpers()
        restHelpers = RestHelpers(self._rdmc)
        validator = LogicalNvdimmValidator()

        scalable_pmem_config = ScalablePersistentMemoryConfig(restHelpers, \
                                                    validator, self._chif_lib)
        scalable_pmem_config.refresh()

        # pre-validation
        self._helpers.validateFeatureIsSupported(scalable_pmem_config)

        helpers.writeHeader2(u"Scalable Persistent Memory Backup Storage Devices")
        helpers.displayDrivesConfiguration(scalable_pmem_config)
        sys.stdout.write(u"\n")

    def run(self, line):
        """ Wrapper function for showlogicalnvdimmdrives command main function

        :param line: command line input
        :type line: string.
        """
        LOGGER.info("Scalable PMEM: {}".format(self.name))
        try:
            (options, args) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        if args:
            raise InvalidCommandLineError("No argument is required.")

        LOGGER.info("Options: {}".format(options))

        if not self._chif_lib:
            self._helpers.failNoChifLibrary()

        self.showDriveData()

        #Return code
        return ReturnCodes.SUCCESS
