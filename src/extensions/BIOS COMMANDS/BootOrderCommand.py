###
# Copyright 2017 Hewlett Packard Enterprise, Inc. All rights reserved.
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
""" BootOrder Command for rdmc """

import sys
import ast
import copy

from optparse import OptionParser
from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
                    InvalidCommandLineErrorOPTS, BootOrderMissingEntriesError,\
                    InvalidOrNothingChangedSettingsError

class BootOrderCommand(RdmcCommandBase):
    """ Changes the boot order for the server that is currently logged in """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='bootorder',\
            usage='bootorder [BOOT ORDER]\n\n\tRun without arguments for ' \
                'current boot order and one time boot options.\n\texample: ' \
                'bootorder\n\n\tTo set the persistent boot order pick items ' \
                'from\n\tthe "Current Persistent Boot Order" section.\n\t' \
                'example: bootorder [5,4,3,2,1] --commit\n\n\tSetting partial' \
                ' boot order is also supported.\n\tMissing entries are ' \
                'concatenated at the end.\n\texample: bootorder [5] --commit' \
                '\n\n\tTo set one time boot entry pick items from the\n\t"' \
                'Continuous and one time boot uefi options" section.\n\t' \
                'example: bootorder --onetimeboot=Hdd\n\n\tTo set continuous' \
                ' boot entry pick items from the\n\t"Continuous and one time ' \
                'boot uefi options" section.\n\texample: bootorder --' \
                'continuousboot=Utilities --commit\n\n\tDisable either ' \
                'continuous or one time boot options.\n\texample: bootorder ' \
                '--disablebootflag --commit\n\n\t'\
                'Changing Secure Boot Keys:\n\tTo manage secure boot keys use'\
                ' the --securebootkeys flag.\n\tTo delete all keys.\n\n\texample:'\
                ' bootorder --securebootkeys=deletepk\n\tFor all posibilities'
                ' see the --securebootkeys flag \n\tin the options list.\n\n\t'\
                'NOTE: pick ONETIMEBOOT and ' \
                'CONTINUOUS items from "Continuous\n\tand one time boot ' \
                'options" section. Items in this list represent\n\ta ' \
                '"clustered" view of the "Continuous and one time boot uefi' \
                '\n\toptions" section. Example: choosing Pxe will try to Pxe' \
                ' boot\n\tcapable devices in the order found in the "' \
                'Continuous and one\n\ttime boot options".\n\n\t',\
            summary='Displays and sets the current boot order.',\
            aliases=['bootorder'],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.lobobj = rdmcObj.commandsDict["LoginCommand"](rdmcObj)
        self.getobj = rdmcObj.commandsDict["GetCommand"](rdmcObj)
        self.setobj = rdmcObj.commandsDict["SetCommand"](rdmcObj)
        self.selobj = rdmcObj.commandsDict["SelectCommand"](rdmcObj)
        self.rebootobj = rdmcObj.commandsDict["RebootCommand"](rdmcObj)

    def run(self, line):
        """ Main boot order worker function """
        try:
            (options, args) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        if len(args) < 2:
            self.bootordervalidation(options)
        else:
            raise InvalidCommandLineError("Invalid number of parameters." \
                                      " Reboot takes a maximum of 1 parameter.")

        if options.secureboot:
            self.secureboothelper(options.secureboot)

            if options.reboot:
                self.rebootobj.run(options.reboot)

            return ReturnCodes.SUCCESS

        bootoverride = None
        self.selobj.selectfunction("HpBios.")
        bootmode = self.getobj.getworkerfunction("BootMode", options, \
                                                    "BootMode", results=True)

        self.selobj.selectfunction("ComputerSystem.")
        onetimebootsettings = self.getobj.getworkerfunction("Boot", options, \
                ['Boot/'+self.typepath.defs.bootoverridetargettype], \
                newargs=['Boot', self.typepath.defs.bootoverridetargettype], \
                results=True)

        bootstatus = self.getobj.getworkerfunction("Boot", options, \
                               ['Boot/BootSourceOverrideEnabled'], \
                               newargs=['Boot', 'BootSourceOverrideEnabled'], \
                               results=True)

        targetstatus = self.getobj.getworkerfunction("Boot", options, \
                                ['Boot/BootSourceOverrideTarget'], \
                                newargs=['Boot', 'BootSourceOverrideTarget'], \
                                results=True)

        uefitargetstatus = self.getobj.getworkerfunction("Boot", options, \
                            ['Boot/UefiTargetBootSourceOverride'], \
                            newargs=['Boot', 'UefiTargetBootSourceOverride'], \
                            results=True)

        currentsettings = self._rdmc.app.get_handler(\
                                            self.typepath.defs.systempath, \
                                            verbose=self._rdmc.opts.verbose, \
                                            service=True, silent=True)

        if bootmode and bootmode["BootMode"] == "Uefi":
            uefionetimebootsettings = self.getobj.getworkerfunction("Boot", \
                  options, ['Boot/UefiTargetBootSourceOverrideSupported'], \
                  newargs=['Boot', 'UefiTargetBootSourceOverrideSupported'], \
                  results=True)
        else:
            uefionetimebootsettings = None

        if options.onetimeboot is None and options.continuousboot is None and \
                                                    not options.disablebootflag:
            self.selobj.selectfunction("HpServerBootSettings.")
            bootsettings = \
                    self.getobj.getworkerfunction("PersistentBootConfigOrder", \
                          options, "PersistentBootConfigOrder", results=True)

            bootsources = self._rdmc.app.get_handler(\
                                '/rest/v1/systems/1/bios/Boot', \
                                verbose=self._rdmc.opts.verbose,\
                                service=True, silent=True).dict['BootSources']

            if not args:
                self.print_out_boot_order(bootsettings, onetimebootsettings, \
                              uefionetimebootsettings, bootmode, bootsources)
            elif len(args) == 1:
                bootlist = args[0][1:-1].split(",")
                currentlist = bootsettings["PersistentBootConfigOrder"]

                if not isinstance(currentlist, list):
                    templist = ast.literal_eval(currentlist[1:-1])
                    currentlist = [n.strip() for n in templist]

                removallist = copy.deepcopy(currentlist)

                if len(bootlist) > len(currentlist):
                    raise InvalidCommandLineError("Number of entries is " \
                                  "greater than the current boot order length.")
                else:
                    newlist = "["

                    for value in range(0, len(bootlist)):
                        try:
                            newlist += currentlist[int(bootlist[value]) -1]
                        except:
                            raise InvalidCommandLineError("Invalid entry " \
                                  "number passed to bootorder. Please \n" \
                                  "       run bootorder without arguments" \
                                  " for possible boot \n       order numbers. ")

                        removallist.remove(currentlist[int(bootlist[value]) -1])

                        if not len(removallist) == 0:
                            newlist += ","

                    if len(removallist) == 0:
                        newlist += "]"
                    else:
                        for value in range(0, len(removallist)):
                            newlist += removallist[value]

                            if not value == len(removallist) - 1:
                                newlist += ","

                        newlist += "]"

                    if options.commit:
                        newlist += " --commit"

                    if options.biospassword:
                        newlist += " --biospassword " + options.biospassword

                    if options.reboot:
                        newlist += ' --reboot ' + options.reboot

                    self.setobj.run("PersistentBootConfigOrder=" + newlist)
            else:
                raise InvalidCommandLineError("Invalid number of parameters." \
                                  " Boot order takes a maximum of 1 parameter.")
        else:
            if not options.onetimeboot is None:
                entry = options.onetimeboot

                if not bootstatus['Boot'][u'BootSourceOverrideEnabled'] == \
                                                                        'Once':
                    bootoverride = " Boot/BootSourceOverrideEnabled=Once"
            elif not options.continuousboot is None:
                entry = options.continuousboot

                if not bootstatus['Boot'][u'BootSourceOverrideEnabled'] == \
                                                                'Continuous':
                    bootoverride = " Boot/BootSourceOverrideEnabled=Continuous"
            else:
                entry = "JacksBootOption"
                if not bootstatus['Boot'][u'BootSourceOverrideEnabled'] == \
                                                                    'Disabled':
                    if currentsettings.dict[u'Boot']\
                                [u'BootSourceOverrideEnabled'] == 'Disabled':
                        bootoverride = "Boot/BootSourceOverrideTarget=None"\
                            " Boot/BootSourceOverrideEnabled=Disabled"
                    else:
                        bootoverride = "Boot/BootSourceOverrideTarget=None"

            newlist = ""

            if entry.lower() in (item.lower() for item in onetimebootsettings\
                        ["Boot"][self.typepath.defs.bootoverridetargettype]):

                if entry and isinstance(entry, basestring):
                    entry = entry.upper()

                entry = self.searchcasestring(entry, \
                                    onetimebootsettings["Boot"]\
                                    [self.typepath.defs.bootoverridetargettype])

                if not entry == targetstatus['Boot']\
                                                [u'BootSourceOverrideTarget']:
                    newlist += " Boot/BootSourceOverrideTarget=" + entry

                if bootoverride:
                    newlist += bootoverride

                if options.commit and newlist:
                    newlist += " --commit"

                if options.biospassword and newlist:
                    newlist += " --biospassword " + options.biospassword

                if options.reboot:
                    newlist += ' --reboot ' + options.reboot

                if newlist:
                    self.setobj.run(newlist)
                else:
                    raise InvalidOrNothingChangedSettingsError("Entry is the "\
                                                    "current boot setting.")
            elif uefionetimebootsettings and entry in (item for \
                                    item in uefionetimebootsettings["Boot"]\
                                    ["UefiTargetBootSourceOverrideSupported"]):
                if entry and isinstance(entry, basestring):
                    entry = entry.upper()

                entry = self.searchcasestring(entry, uefionetimebootsettings\
                            ["Boot"]["UefiTargetBootSourceOverrideSupported"])

                if not targetstatus['Boot'][u'BootSourceOverrideTarget'] == \
                                                                'UefiTarget':
                    newlist += " Boot/BootSourceOverrideTarget=UefiTarget"

                if not entry == uefitargetstatus['Boot']\
                                            [u'UefiTargetBootSourceOverride']:
                    newlist += " Boot/UefiTargetBootSourceOverride=" + entry

                if bootoverride:
                    newlist += bootoverride

                if options.reboot:
                    newlist += ' --reboot ' + options.reboot

                if newlist:
                    self.setobj.run(newlist)
                else:
                    raise InvalidOrNothingChangedSettingsError("Entry is the " \
                                                    "current boot setting.\n")
            elif options.disablebootflag:

                if bootoverride:
                    newlist += bootoverride

                if options.commit and newlist:
                    newlist += " --commit"

                if options.reboot:
                    newlist += ' --reboot ' + options.reboot

                if newlist:
                    self.setobj.run(newlist)
                else:
                    raise InvalidOrNothingChangedSettingsError("Entry is the " \
                                                    "current boot setting.\n")
            else:
                raise InvalidCommandLineError("Invalid entry passed for one"\
                          " time boot. Please run boot \n       order without"\
                          " arguments to view available options.\n")

        #Return code
        return ReturnCodes.SUCCESS

    def searchcasestring(self, entry, content):
        """ Helper function for retrieving correct case for value

        :param entry: entry to correlate case
        :type entry: string.
        :param content: list of items
        :type content: list.
        """
        for item in content:
            if entry.upper() == item.upper():
                return item

    def secureboothelper(self, securebootoption):
        """ Helper function for secure boot function

        :param securebootoption: option passed in for secure boot
        :type securebootoption: string.
        """
        actionlist = ['defaultkeys', 'deletekeys', 'deletepk']

        if not securebootoption.lower() in actionlist:
            raise InvalidCommandLineError('%s is not a valid option for '\
                                  'the securebootkeys flag.' % securebootoption)

        if securebootoption == actionlist[0]:
            action = 'ResetAllKeysToDefault'
        elif securebootoption == actionlist[1]:
            action = 'DeleteAllKeys'
        elif securebootoption == actionlist[2]:
            action = 'DeletePK'

        results = self._rdmc.app.filter(self.typepath.defs.hpsecureboot, None, \
                                                                        None)

        try:
            results = results[0]
        except:
            pass

        if results:
            path = results.resp.request.path
            results = results.resp.dict

        try:
            for item in results['Actions']:
                if 'ResetKeys' in item:
                    path = results['Actions'][item]['target']
                    break

            body = {"ResetKeysType": action}
            self._rdmc.app.post_handler(path, body)
        except:
            if securebootoption == actionlist[0]:
                self.selobj.selectfunction(self.typepath.defs.hpsecureboot)
                self.setobj.run('ResetToDefaultKeys=True --commit')
            elif securebootoption == actionlist[1]:
                self.selobj.selectfunction(self.typepath.defs.hpsecureboot)
                self.setobj.run('ResetAllKeys=True --commit')
            else:
                sys.stderr.write("DeletePK option is not available on rest.\n")

    def bootordervalidation(self, options):
        """ Boot order method validation function

        :param options: command line options
        :type options: list.
        """
        inputline = list()

        if self._rdmc.app.config._ac__commit.lower() == 'true':
            options.commit = True

        try:
            client = self._rdmc.app.get_current_client()
            if options.user and options.password:
                if not client.get_username():
                    client.set_username(options.user)
                if not client.get_password():
                    client.set_password(options.password)

            if options.biospassword:
                self._rdmc.app.update_bios_password(options.biospassword)
        except:
            if options.user or options.password or options.url:
                if options.url:
                    inputline.extend([options.url])
                if options.user:
                    inputline.extend(["-u", options.user])
                if options.password:
                    inputline.extend(["-p", options.password])
            else:
                if self._rdmc.app.config.get_url():
                    inputline.extend([self._rdmc.app.config.get_url()])
                if self._rdmc.app.config.get_username():
                    inputline.extend(["-u", \
                                  self._rdmc.app.config.get_username()])
                if self._rdmc.app.config.get_password():
                    inputline.extend(["-p", \
                                  self._rdmc.app.config.get_password()])

        if len(inputline):
            self.lobobj.loginfunction(inputline)

    def print_out_boot_order(self, content, onetimecontent, uefionetimecontent,\
                              bootmode, bootsources):
        """ Convert content to human readable and print out to std.out

        :param content: current content
        :type content: string.
        :param onetimecontent: list of one time boot entries
        :type onetimecontent: list.
        :param uefionetimecontent: list of uefi one time boot entries
        :type uefionetimecontent: list.
        :param bootmode: current system boot mode
        :type bootmode: string.
        :param bootsources: current systems boot sources
        :type bootsources: list.
        """
        try:
            if content is None:
                raise BootOrderMissingEntriesError(u"No entries found in " \
                                                    "current boot order.\n\n")
            else:
                self.print_boot_helper(content, "\nCurrent Persistent Boot "\
                                       "Order:", bootsources=bootsources)

            if onetimecontent is None:
                raise BootOrderMissingEntriesError(u"No entries found for one" \
                                                    " time boot options.\n\n")
            else:
                self.print_boot_helper(onetimecontent["Boot"], \
                                       "Continuous and one time boot options:")

            if bootmode and bootmode["BootMode"] == "Uefi":
                if uefionetimecontent is None:
                    raise BootOrderMissingEntriesError(u"No entries found for" \
                                                   " one-time UEFI options.")
                else:
                    self.print_boot_helper(uefionetimecontent["Boot"], \
                               "Continuous and one time boot uefi options:",\
                               bootsources=bootsources)
        except Exception, excp:
            raise excp

    def print_boot_helper(self, content, outstring, indent=0, bootsources=None):
        """ Print boot helper

        :param content: current content
        :type content: string.
        :param outstring: output string
        :type outstring: string.
        :param indent: indent format
        :type indent: string.
        :param bootsources: current systems boot sources
        :type bootsources: list.
        """
        for _, value in content.iteritems():
            sys.stdout.write('\t' * indent + outstring)

            if isinstance(value, list):
                count = 1

                for item in value:
                    sys.stdout.write('\n')

                    if not item:
                        item = unicode('null')

                    if isinstance(item, unicode):
                        bootstring = False
                        try:
                            for source in bootsources:
                                if item == source['StructuredBootString']:
                                    sys.stdout.write('\t' * indent + \
                                         str(count) + ". " + str(item) + \
                                         ' (' + str(source['BootString']) + ')')
                                    bootstring = True
                                    break

                            if not bootstring:
                                sys.stdout.write('\t' * indent + str(count) \
                                                            + ". " + str(item))
                        except:
                            sys.stdout.write('\t' * indent + str(count) + \
                                                            ". " + str(item))

                        count += 1
                    else:
                        self.print_boot_helper(item, indent+1)

        sys.stdout.write('\n\n')

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        customparser.add_option(
            '--url',
            dest='url',
            help="Use the provided iLO URL to login.",
            default=None,
        )
        customparser.add_option(
            '-u',
            '--user',
            dest='user',
            help="If you are not logged in yet, including this flag along"\
            " with the password and URL flags can be used to log into a"\
            " server in the same command.""",
            default=None,
        )
        customparser.add_option(
            '-p',
            '--password',
            dest='password',
            help="""Use the provided iLO password to log in.""",
            default=None,
        )
        customparser.add_option(
            '--biospassword',
            dest='biospassword',
            help="Select this flag to input a BIOS password. Include this"\
            " flag if second-level BIOS authentication is needed for the"\
            " command to execute.",
            default=None,
        )
        customparser.add_option(
            '--onetimeboot',
            dest='onetimeboot',
            help="Use this flag to configure a one-time boot option."\
            " Using this flag will prioritize the provided boot source"\
            " only on the very next time the server is booted.",
            default=None,
        )
        customparser.add_option(
            '--continuousboot',
            dest='continuousboot',
            help="Use this flag to enable a continuous boot option. Using"\
            " this flag will cause the system to boot to the selected"\
            " device every time the system boots.",
            default=None,
        )
        customparser.add_option(
            '--disablebootflag',
            dest='disablebootflag',
            action="store_true",
            help="Use this to disable either continuous or"\
            " one-time boot modes.",
            default=None,
        )
        customparser.add_option(
            '--securebootkeys',
            dest='secureboot',
            help="Use this flag to perform actions on secure boot keys."\
            "Possible values include defaultkeys: resets all keys to default,"\
            "deletekeys: deletes all keys, deletepk: deletes all product keys.",
            default=False,
        )
        customparser.add_option(
            '--commit',
            dest='commit',
            action="store_true",
            help="Use this flag when you are ready to commit all the"\
            " changes for the current selection. Including the commit"\
            " flag will log you out of the server after the command is"\
            " run. Note that some changes made in this way will be updated"\
            " instantly, while others will be reflected the next time the"\
            " server is started.",
            default=None,
        )
        customparser.add_option(
            '--reboot',
            dest='reboot',
            help="Use this flag to perform a reboot command function after"\
            " completion of operations.  For help with parameters and"\
            " descriptions regarding the reboot flag, run help reboot.",
            default=None,
        )
