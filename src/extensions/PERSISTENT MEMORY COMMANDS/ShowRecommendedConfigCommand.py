###
# Copyright 2019 Hewlett Packard Enterprise, Inc. All rights reserved.
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
"""Command to show recommended configurations"""
from __future__ import absolute_import, division
import sys

from collections import OrderedDict
from optparse import OptionParser

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
    NoContentsFoundForOperationError, LOGGER

from .lib.DisplayHelpers import DisplayHelpers, OutputFormats
from .lib.Mapper import Mapper
from .lib.MapperRenderers import MappingTable
from .lib.PmemHelpers import PmemHelpers
from .lib.RestHelpers import RestHelpers


class ShowRecommendedConfigCommand(RdmcCommandBase):
    """ Show recommended configurations"""

    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,
                                 name="showrecommendedpmmconfig",
                                 usage="showrecommendedpmmconfig [-h|--help]\n\n" \
                                       "\tShow recommended configurations\n" \
                                       "\texample: showrecommendedpmmconfig",
                                 summary="Show Recommended Configuration",
                                 aliases=["showrecommendedpmmconfig"],
                                 optparser=OptionParser())
        self._rdmc = rdmcObj
        self._rest_helpers = RestHelpers(rdmcObject=self._rdmc)
        self._display_helpers = DisplayHelpers()
        self._mapper = Mapper()
        self._pmem_helpers = PmemHelpers()

    def run(self, line):
        """
        Wrapper function for new command main function
        :param line: command line input
        :type line: string.
        """
        LOGGER.info("Show Recommended Configuration: %s", self.name)
        try:
            (options, args) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineError("Failed to parse options")
        if args:
            raise InvalidCommandLineError("Chosen command doesn't expect additional arguments")
        # Raise exception if server is in POST
        if self._rest_helpers.in_post():
            raise NoContentsFoundForOperationError("Unable to retrieve resources - "\
                                                   "server might be in POST or powered off")
        self.show_recommended_config()

        return ReturnCodes.SUCCESS

    def show_recommended_config(self):
        """
        Show recommended pmm configuration
        """
        members = self._rest_helpers.retrieve_memory_resources().get("Members")

        if not members:
            raise NoContentsFoundForOperationError("Failed to retrieve memory resources")

        #retreving aep dimms
        aep_members = self._pmem_helpers.get_pmem_members(members)[0]

        if not aep_members:
            raise NoContentsFoundForOperationError("No Persistent Memory Modules found")

        #retreving dram dimms
        dram_members = self._pmem_helpers.get_non_aep_members(members)[0]

        if not dram_members:
            raise NoContentsFoundForOperationError("No DRAM DIMMs found")

        # retrieving Total Capacity of PMEM dimms
        aep_size = self._mapper.get_single_attribute(aep_members, "TotalCapacity",
                                                     MappingTable.summary.value, True)
        aep_size = aep_size.get("TotalCapacity", {}).get("Value", 0)

        # retrieving Total Capacity of DRAM dimms
        dram_size = self._mapper.get_single_attribute(dram_members, "TotalCapacity",
                                                      MappingTable.summary.value, True)
        dram_size = dram_size.get("TotalCapacity", {}).get("Value", 0)

        display_output = list()
        recommended_config = list()

        temp_dict = OrderedDict()

        #Adding deafult option 100% App Direct and 0% Volatile
        temp_dict["MemoryModeTotalSize"] = 0
        temp_dict["PmemTotalSize"] = aep_size
        temp_dict["CacheRatio"] = None
        recommended_config.append(temp_dict)

        stepsize = 32
        aep_direct_size = 0
        step = 0
        while aep_direct_size < aep_size:
            aep_direct_size = step * stepsize * len(aep_members)
            memorymode_total_size = aep_size - aep_direct_size
            cache_ratio = memorymode_total_size / dram_size
            temp_dict = OrderedDict()
            if 2 <= cache_ratio <= 16:
                temp_dict["MemoryModeTotalSize"] = memorymode_total_size
                temp_dict["PmemTotalSize"] = aep_direct_size
                temp_dict["CacheRatio"] = cache_ratio
                recommended_config.append(temp_dict)
            step += 1

        #sorting based on MemoryModeTotalSize
        recommended_config = sorted(recommended_config, key=lambda x: x["MemoryModeTotalSize"])

        #Adding units and formating cache ratio
        for output in recommended_config:
            output["MemoryModeTotalSize"] = "%d GB" % output["MemoryModeTotalSize"]
            output["PmemTotalSize"] = "%d GB" % output["PmemTotalSize"]
            if output["CacheRatio"] is None:
                output["CacheRatio"] = "N/A"
            else:
                output["CacheRatio"] = "1:%.1f" % output["CacheRatio"]
            display_output.append(self._pmem_helpers.json_to_text(output)[0])

        #display output in table format
        self._display_helpers.display_data(display_output, OutputFormats.table)
