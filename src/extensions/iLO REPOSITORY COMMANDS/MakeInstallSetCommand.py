# ##
# Copyright 2020 Hewlett Packard Enterprise, Inc. All rights reserved.
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
# ##

# -*- coding: utf-8 -*-
""" Install Set Command for rdmc """

import os
import sys
import json

from six.moves import input
from argparse import ArgumentParser

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group, logout_routine

from rdmc_helper import IncompatibleiLOVersionError, ReturnCodes,\
                        InvalidCommandLineErrorOPTS, InvalidCommandLineError

class MakeInstallSetCommand(RdmcCommandBase):
    """ Command class to create installset payload"""
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self, \
            name='makeinstallset', \
            usage='makeinstallset \n\n\tRun to enter a guided shell for making ' \
            'install sets. If not currently\n\tlogged into a server will perform '\
            'basic guidance on making an installset,\n\tif logged into a server '\
            'will provide guidance based on the current\n\tcomponents on the system. '\
            'If you wish to use this command on a logged in\n\tserver upload the '\
            'components before running for best results.',\
            summary='Creates install sets for iLO.',\
            aliases=['MInstallset'], \
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)
        self.defaultprops = {"UpdatableBy":["Bmc"], "Command":\
                    "ApplyUpdate", "WaitTimeSeconds":0, "Filename":""}
        self.helptext = {"Command": "Possible Commands: ApplyUpdate, ResetServer, "\
                       "ResetBmc, Wait", "UpdatableBy": "Possible Update parameter(s)"\
                       ":\nBmc: Updatable by iLO\nUefi: Updatable by Uefi\n"\
                       "RuntimeAgent: Updatable by runtime agent such as SUM/SUT", \
                       "WaitTimeSeconds": "Number of seconds to pause in Wait "\
                       "command.", "Filename": "Unique filename of component on "\
                       "iLO repository"}
        self.loggedin = None
        self.comps = None

    def run(self, line):
        """ Main installset worker function

        :param line: string of arguments passed in
        :type line: str.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.loggedin = None
        self.comps = None
        self.loggedin = self.minstallsetvalidation()

        if self.loggedin and self.typepath.defs.isgen9:
            raise IncompatibleiLOVersionError('iLO Repository commands are ' \
                                                    'only available on iLO 5.')

        sys.stdout.write("Warning: This command will run in interactive mode.\n")
        if args:
            raise InvalidCommandLineError("makeinstallset command takes no arguments.")

        self.minstallsetworker(options)

        logout_routine(self, options)
        #Return code
        return ReturnCodes.SUCCESS

    def minstallsetworker(self, options):
        """Main installset creation worker

        :param options: command line options
        :type options: list.
        """
        comps = {}
        totcomps = []
        count = -1
        totcount = 0
        sys.stdout.write("Entering new shell, type backout to leave!\n")
        if self.loggedin:
            sys.stdout.write("Running in logged in mode.")
            self.comps = self._rdmc.app.getcollectionmembers(\
                            '/redfish/v1/UpdateService/ComponentRepository/')
        else:
            sys.stdout.write("Running in basic guidance mode.")
        while True:
            comps = {}
            count = -1
            reqdprops = ["Command"]
            while True:
                if len(reqdprops) <= count:
                    break
                if count == -1:
                    line = input("\nEnter a name for this command: ")
                else:
                    sys.stdout.write('\n'+self.helptext[reqdprops[count]] + "\n")
                    if self.loggedin and reqdprops[count].lower() == 'filename':
                        filenm, updateby = self.checkfiles()
                        comps['Filename'] = filenm
                        comps['UpdatableBy'] = updateby
                        break
                    else:
                        line = input('Enter '+ reqdprops[count] + " for " + comps["Name"] + ": ")
                if line.endswith(os.linesep):
                    line.rstrip(os.linesep)
                if line == "backout":
                    break
                elif line == "" and not count == -1:
                    line = self.defaultprops[reqdprops[count]]
                if count == -1:
                    comps["Name"] = line
                else:
                    while True:
                        validated = self.validatepropvalue(reqdprops[count], line, reqdprops)
                        if not validated:
                            if line == "backout":
                                break
                            line = input("Input %s is not a valid property " \
                                            "for %s. Try again: " % (line, reqdprops[count]))
                        else:
                            comps[reqdprops[count]] = validated
                            break
                count = count + 1
            if line == "backout":
                break
            else:
                totcomps.append(comps)
                totcount = totcount + 1

        if not totcount:
            sys.stdout.write("No sequences created. Exiting without creating an installset.\n")
        else:
            while True:
                isrecovery = input("Is this a recovery installset? ")
                isrecovery = True if str(isrecovery).lower() in \
                                            ['true', 't', 'yes'] else isrecovery
                isrecovery = False if str(isrecovery).lower() in \
                                            ['false', 'f', 'no'] else isrecovery
                if not isinstance(isrecovery, bool):
                    sys.stdout.write("Isrecovery should be either true or false.\n")
                    continue
                else:
                    break

            if isrecovery:
                installsetname = "System Recovery Set"
            else:
                while True:
                    installsetname = input("Enter installset name: ")
                    if not installsetname:
                        sys.stdout.write("Install set must have a name.\n")
                    else:
                        break

            description = input("Enter description for the installset: ")

            body = {"Name":installsetname, "Description":description, \
                    "IsRecovery":isrecovery, "Sequence":totcomps}

            sys.stdout.write(str(json.dumps(body, indent=2, sort_keys=True))+'\n')

            if options.filename:
                filename = options.filename
            else:
                filename = 'myinstallset.json'
            with open(filename, 'w') as outfile:
                json.dump(body, outfile, indent=2, sort_keys=True)

            sys.stdout.write("installset saved to %s\n" % filename)

    def validatepropvalue(self, propvalue, givenvalue, reqdprops):
        """Validates a string returning the correct type

        :param propvalue: property to validate
        :type propvalue: string.
        :param givenvalue: value to validate
        :type givenvalue: string.
        :param reqdprops: the required property list
        :type reqdprops: list.
        """
        validated_property = None
        if propvalue == "WaitTimeSeconds":
            validated_property = int(givenvalue)
        elif propvalue == "UpdatableBy":
            if isinstance(givenvalue, list):
                validated_property = givenvalue
            value = [x.strip() for x in givenvalue.split(',')]
            for ind, item in enumerate(value):
                if item.lower() == "runtimeagent":
                    value[ind] = "RuntimeAgent"
                elif item.lower() == "uefi":
                    value[ind] = "Uefi"
                elif item.lower() == "bmc":
                    value[ind] = "Bmc"
            validated_property = value
        elif propvalue == "Command":
            if givenvalue.lower() == "applyupdate":
                if self.loggedin and not self.comps:
                    sys.stdout.write("All components on the system are already "\
                                     "added to the installset.\n")
                else:
                    reqdprops.append("Filename")
                    reqdprops.append("UpdatableBy")
                    validated_property = "ApplyUpdate"
            elif givenvalue.lower() == "resetserver":
                validated_property = "ResetServer"
            elif givenvalue.lower() == "resetbmc":
                validated_property = "ResetBmc"
            elif givenvalue.lower() == "wait":
                reqdprops.append("WaitTimeSeconds")
                validated_property = "Wait"
        elif propvalue == "Filename":
            if givenvalue:
                validated_property = givenvalue

        return validated_property

    def checkfiles(self):
        count = 0
        sys.stdout.write("Components currently in the repository that have not "\
                         "been added to the installset:\n")
        for comp in self.comps:
            count += 1
            sys.stdout.write("[%d] %s\n" % (count, comp['Name'].encode("ascii", "ignore")))
        while True:
            userinput = input("Select the number of the component you want to add to "\
                             "the install set: ")
            try:
                userinput = int(userinput)
                if userinput > count or userinput == 0:
                    raise
                break
            except:
                sys.stdout.write("Input is not a valid number.\n")
        filename = self.comps[userinput-1]["Filename"]
        updatableby = self.comps[userinput-1]["UpdatableBy"]
        del self.comps[userinput-1]
        return filename, updatableby

    def minstallsetvalidation(self):
        """ makeinstallset validation function"""

        try:
            _ = self._rdmc.app.current_client
            loggedin = True
        except:
            loggedin = False

        return loggedin

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        add_login_arguments_group(customparser)

        customparser.add_argument(
            '-f',
            '--filename',
            dest='filename',
            help="Use this flag if you wish to use a different"\
            " filename than the default one. The default filename is" \
            " myinstallset.json",
            action="append",
            default=None
        )
