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

""" Enable Scalable Persistent Memory Command """

import sys

from optparse import OptionParser

from lib.Helpers import Helpers
from lib.RestHelpers import RestHelpers
from lib.LogicalNvdimmValidator import LogicalNvdimmValidator
from lib.ScalablePersistentMemoryConfig import ScalablePersistentMemoryConfig

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineErrorOPTS, \
                        LOGGER, InvalidCommandLineError

class EnableScalablePmemCommand(RdmcCommandBase):
    """ Enable Scalable Pmem command """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self, \
            name='enablescalablepmem', \
            usage='enablescalablepmem [OPTIONS]\n\n' \
                '\tEnables or disables the Scalable Persistent Memory feature.\n'\
                '\n\texample: enablescalablepmem', \
            summary='Enable or disable the Scalable Persistent Memory feature.', \
            aliases=['spmem-enable', 'spmemen'], \
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self._helpers = Helpers()
        self._restHelpers = RestHelpers(self._rdmc)
        self._chif_lib = self._helpers.gethprestchifhandle()

    def enableOrDisableFeature(self, enable):
        """ Enables or disables the feature

        :param enable: a flag whether to enable or disable the feature
        :type enable: boolean
        """

        validator = LogicalNvdimmValidator()

        scalable_pmem_config = ScalablePersistentMemoryConfig(self._restHelpers,\
                                                     validator, self._chif_lib)
        scalable_pmem_config.refresh()

        # pre-validation
        self._helpers.validateFeatureIsSupported(scalable_pmem_config)
        self._helpers.validateFunctionalityIsEnabled(scalable_pmem_config)

        if enable is False:
            # If user disables Scalable PMEM, revert any pending changes to
            # prevent data or configuration loss
            if self._rdmc.interactive:
                message = u"Warning: disabling Scalable Persistent Memory will "\
                                    "revert any pending configuration changes.\n"
                self._helpers.confirmChanges(message=message)
            self._restHelpers.revertSettings()

        patchAttributes = {
            "FeatureEnabled" : enable
        }
        _ = self._restHelpers.patchScalablePmemSettingAttributes(patchAttributes)

        sys.stdout.write(u"\nThe Scalable Persistent Memory feature has been "\
                    "set to: {}\n".format("Enabled" if enable else "Disabled"))

        self._helpers.noticeRestartRequired(scalable_pmem_config)

        sys.stdout.write("\n\n")

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

        if len(args):
            InvalidCommandLineError("This command takes no parameters.")

        LOGGER.info("Options: {}".format(options))

        if not self._chif_lib:
            self._helpers.failNoChifLibrary()

        enable = True
        if options.enableFeature is False:
            enable = False

        self.enableOrDisableFeature(enable)

        #Return code
        return ReturnCodes.SUCCESS

    def definearguments(self, customparser):
        """ Define arguments for the command

        :param customparser: command line input
        :type customparser: parser.
        """

        customparser.add_option(
            '--disable',
            action="store_false",
            dest="enableFeature",
            help="Disable the Scalable Persistent Memory feature. Warning: "\
                                "any pending configuration changes will be lost."
        )
