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

""" Show Scalable Persistent Memory Configuration Command """

import sys

from optparse import OptionParser

from lib.Helpers import Helpers
from lib.RestHelpers import RestHelpers
from lib.LogicalNvdimmValidator import LogicalNvdimmValidator
from lib.ScalablePersistentMemoryConfig import ScalablePersistentMemoryConfig

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, LOGGER

class ShowLogicalNVDIMMConfigurationCommand(RdmcCommandBase):
    """ Main showscalablepmemconfig command class """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='showscalablepmemconfig', \
            usage='showscalablepmemconfig [--available] [--json]\n\n'\
                '\tDisplay the Scalable Persistent Memory configuration.\n\n'\
                '\texample: showscalablepmemconfig', \
            summary='Display the Scalable Persistent Memory configuration.', \
            aliases=['spmem-showcfg', 'spmemsc'], \
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self._helpers = Helpers()
        self._chif_lib = self._helpers.gethprestchifhandle()
        self._restHelpers = RestHelpers(rdmcObject=self._rdmc)
        self._options = None

    def showLogicalNvdimmConfig(self, options):
        """ Main showlogicalnvdimmconfig command worker function

        :param options: command options
        :type options: options.
        """

        if self._rdmc.app.config._ac__format.lower() == 'json':
            options.json = True         #pragma: no cover

        validator = LogicalNvdimmValidator()

        scalable_pmem_config = ScalablePersistentMemoryConfig(self._restHelpers,\
                                                     validator, self._chif_lib)
        scalable_pmem_config.refresh()

        # overall config status
        self._helpers.validateAllConfigurationPolicies(scalable_pmem_config, \
                                                    output_as_json=options.json)

        if options.available:
            if not options.json:
                self._helpers.writeHeader2(u"Available Scalable Persistent Memory")
                sys.stdout.write("Available capacity to create logical NVDIMMs "\
                                 "is constrained by the system hardware, including"\
                                 " the number of backup storage devices selected.")

            self._helpers.displayAvailableCapacity(scalable_pmem_config, \
                                                   output_as_json=options.json)
        else:
            if not options.json:
                # overall config enabled and capacity graph
                self._helpers.writeHeader2(u"Overall Allocated Scalable Persistent Memory")
                sys.stdout.write(u"\n")
                self._helpers.displayOverallCapacityBarGraph(scalable_pmem_config, 60)
                if len(scalable_pmem_config.drives.selectedDrives) == 0:
                    sys.stdout.write("* No backup storage devices have been selected")
                sys.stdout.write(u"\n")
                # allocated logical nvdimms
                self._helpers.writeHeader2(u"Logical NVDIMMs")
            self._helpers.displayRegionConfiguration(scalable_pmem_config, \
                                                     output_as_json=options.json)

        sys.stdout.write(u"\n\n")



    def run(self, line):
        """ Wrapper function for showlogicalnvdimmconfiguration command main function

        :param line: command line input
        :type line: string.
        """

        LOGGER.info("Scalable PMEM: {}".format(self.name))

        try:
            (options, _) = self._parse_arglist(line)
            if options:
                self._options = options
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        LOGGER.info("Options: {}".format(options))

        if not self._chif_lib:
            self._helpers.failNoChifLibrary()

        self.showLogicalNvdimmConfig(options)

        #Return code
        return ReturnCodes.SUCCESS


    def definearguments(self, customparser):
        """ Defines argument for the command

        :param customparser: command line input
        :type customparser: parser.
        """

        customparser.add_option(
            '-a',
            '--available',
            action="store_true",
            dest="available",
            help="Show available capacity per processor or processor pair"
        )

        customparser.add_option(
            '-j',
            '--json',
            action="store_true",
            dest="json",
            help="Optionally include this flag to change the output to JSON format.",
            default=False
        )
