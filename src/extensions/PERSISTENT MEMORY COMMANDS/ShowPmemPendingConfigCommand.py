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
"""Command to show the pending configuration for PMM"""

from __future__ import absolute_import
import sys

from optparse import OptionParser

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
    LOGGER, NoContentsFoundForOperationError

from .lib.DisplayHelpers import DisplayHelpers, OutputFormats
from .lib.Mapper import Mapper
from .lib.MapperRenderers import MappingTable
from .lib.PmemHelpers import PmemHelpers
from .lib.RestHelpers import RestHelpers


class ShowPmemPendingConfigCommand(RdmcCommandBase):
    """
    Command to show the pending configuration for PMM
    """

    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,
                                 name="showpmmpendingconfig",
                                 usage="showpmm [-h | --help] [-j | --json]\n\n" \
                                       "\tShows the pending tasks for configuring PMM\n" \
                                       "\texample: showpmmpendingconfig --json",
                                 summary="Shows the pending configuration for PMM.",
                                 aliases=["showpmmpendingconfig"],
                                 optparser=OptionParser())
        self.define_arguments(self.parser)
        self._rdmc = rdmcObj
        self._rest_helpers = RestHelpers(rdmcObject=self._rdmc)
        self._display_helpers = DisplayHelpers()
        self._mapper = Mapper()
        self._pmem_helpers = PmemHelpers()

    @staticmethod
    def define_arguments(customparser):
        """
        Wrapper function for new command main function
        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        customparser.add_option(
            "-j",
            "--json",
            action="store_true",
            dest="json",
            help="Optionally include this flag to change the output to JSON format.",
            default=False
        )

    def run(self, line):
        """
        Wrapper function for new command main function
        :param line: command line input
        :type line: string.
        """
        LOGGER.info("PMM Pending Configuration: %s", self.name)
        try:
            (options, args) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineError("Failed to parse options")
        if args:
            raise InvalidCommandLineError(
                "Chosen command or flag doesn't expect additional arguments")
        # Raise exception if server is in POST
        if self._rest_helpers.in_post():
            raise NoContentsFoundForOperationError("Unable to retrieve resources - "\
                                                   "server might be in POST or powered off")
        self.show_pending_config(options)

        return ReturnCodes.SUCCESS

    def show_pending_config(self, options):
        """
        Command to display information about pending Persistent Memory Configuration
        :param options: command options
        :type options: options.
        """
        # retrieving task members
        task_members = self._rest_helpers.retrieve_task_members()

        # filtering task members
        filtered_task_members = self._rest_helpers.filter_task_members(task_members)
        if not filtered_task_members:
            sys.stdout.write("\nNo pending configuration tasks found.\n\n")
            return None

        # retrieving memory members
        memory = self._rest_helpers.retrieve_memory_resources()
        if memory:
            memory_members = memory.get("Members")
        else:
            raise NoContentsFoundForOperationError("Failed to retrieve Memory Resources")

        attributes = ["Operation", "PmemSize", "VolatileSize", "DimmIds"]
        display_output = list()
        for task in filtered_task_members:
            # finding operation of task
            operation = self._mapper.get_single_attribute(task, "Operation",
                                                          MappingTable.tasks.value, True)
            # displaying existing configuration for DELETE operation
            if operation.get("Operation", "") == "DELETE":
                target_uri = task.get("Payload").get("TargetUri")
                data = self._rest_helpers.get_resource(target_uri)
                table = MappingTable.delete_task.value
            else:
                task_type = self._mapper.get_single_attribute(task, "Type",
                                                              MappingTable.tasks.value, True)
                task_type = task_type.get("Type", "")
                if task_type != "PMEM":
                    sys.stdout.write("Unsupported interleave set type found: " + task_type)
                    continue
                data = task
                table = MappingTable.tasks.value

            task_output = self._mapper.get_multiple_attributes(data, attributes, table,
                                                               output_as_json=options.json,
                                                               memory=memory_members)
            display_output.append(task_output)

        if options.json:
            self._display_helpers.display_data(display_output, OutputFormats.json)
        else:
            self._display_helpers.display_data(display_output, OutputFormats.table)
