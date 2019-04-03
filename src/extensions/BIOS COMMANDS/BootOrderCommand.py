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
import fnmatch

from functools import reduce
from optparse import OptionParser, SUPPRESS_HELP

import six

from rdmc_base_classes import RdmcCommandBase
from rdmc_helper import ReturnCodes, InvalidCommandLineError, Encryption, \
                    InvalidCommandLineErrorOPTS, BootOrderMissingEntriesError,\
                    InvalidOrNothingChangedSettingsError


class BootOrderCommand(RdmcCommandBase):
    """ Changes the boot order for the server that is currently logged in """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='bootorder',\
            usage='bootorder [BOOT ORDER] [OPTIONS]\n\n\tRun without arguments ' \
                'for current boot order and one time boot options.\n\texample: ' \
                'bootorder\n\n\tTo set the persistent boot order pick items ' \
                'from\n\tthe "Current Persistent Boot Order" section.\n\t' \
                'example: bootorder [5,4,3,2,1] --commit\n\n\tSetting partial' \
                ' boot order is also supported.\n\tMissing entries are ' \
                'concatenated at the end.\n\texample: bootorder [5] --commit\n\n\t' \
                'You can also set the boot order using parial string matching.\n\t' \
                'example: bootorder NIC.*v4 HD* Generic.USB.1.1 --commit\n\n\tThis will set ' \
                'All v4 NICs first, followed by all hard drives,\n\tfollowed by Generic.USB.1.1. ' \
                'Everything not listed will be\n\tadded to the end of the boot order.' \
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
                ' bootorder --securebootkeys=deletepk\n\tFor all possibilities'
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
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.getobj = rdmcObj.commands_dict["GetCommand"](rdmcObj)
        self.setobj = rdmcObj.commands_dict["SetCommand"](rdmcObj)
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)
        self.rebootobj = rdmcObj.commands_dict["RebootCommand"](rdmcObj)

    def run(self, line):
        """ Main boot order worker function """
        try:
            (options, args) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.bootordervalidation(options)

        if options.secureboot:
            self.secureboothelper(options.secureboot)

            if options.reboot:
                self.rebootobj.run(options.reboot)

            return ReturnCodes.SUCCESS

        bootoverride = None
        self.selobj.selectfunction("HpBios.")
        bootmode = self.getobj.getworkerfunction("BootMode", options, \
                                    results=True, uselist=True)

        self.selobj.selectfunction("ComputerSystem.")
        onetimebootsettings = next(iter(self.getobj.getworkerfunction(\
                ['Boot/'+self.typepath.defs.bootoverridetargettype], options, \
                results=True, uselist=True)), None)

        bootstatus = next(iter(self.getobj.getworkerfunction(\
                               ['Boot/BootSourceOverrideEnabled'], options, \
                               results=True, uselist=True)), None)

        targetstatus = next(iter(self.getobj.getworkerfunction(\
                                ['Boot/BootSourceOverrideTarget'], options, \
                                results=True, uselist=True)), None)

        uefitargetstatus = next(iter(self.getobj.getworkerfunction(\
                            ['Boot/UefiTargetBootSourceOverride'], options, \
                            results=True, uselist=True)), None)

        currentsettings = self._rdmc.app.get_handler(\
                                            self.typepath.defs.systempath, \
                                            verbose=self._rdmc.opts.verbose, \
                                            service=True, silent=True)
        bootsources = self._rdmc.app.get_handler(\
                                '/rest/v1/systems/1/bios/Boot', \
                                verbose=self._rdmc.opts.verbose,\
                                service=True, silent=True).dict['BootSources']

        if bootmode and any([boot.get("BootMode", None) == "Uefi" for boot in bootmode]):
            #Gen 9
            uefionetimebootsettings = next(iter(self.getobj.getworkerfunction(\
                  ['Boot/UefiTargetBootSourceOverrideSupported'], options, \
                  results=True, uselist=True)), None)
            if not uefionetimebootsettings:
                #Gen 10
                uefionetimebootsettings = next(iter(self.getobj.getworkerfunction(\
                  ['Boot/UefiTargetBootSourceOverride@Redfish.AllowableValues'], options, \
                  results=True, uselist=True)), None)['Boot']\
                                            ['UefiTargetBootSourceOverride@Redfish.AllowableValues']
                finaluefi = []
                for setting in uefionetimebootsettings:
                    for source in bootsources:
                        if 'UEFIDevicePath' in source and \
                                                        source['UEFIDevicePath'].endswith(setting):
                            finaluefi.append(source['StructuredBootString'])
                            continue
                uefionetimebootsettings = {"Boot": {"UefiTargetBootSourceOverrideSupported": \
                                                                                        finaluefi}}

        else:
            uefionetimebootsettings = None

        if options.onetimeboot is None and options.continuousboot is None and \
                                                                    not options.disablebootflag:
            self.selobj.selectfunction("HpServerBootSettings.")
            bootsettings = next(iter(self.getobj.getworkerfunction(\
                          "PersistentBootConfigOrder", options, results=True, \
                          uselist=True)), None)

            if not args:
                self.print_out_boot_order(bootsettings, onetimebootsettings, \
                  uefionetimebootsettings, bootmode, bootsources, bootstatus, \
                                                                targetstatus)
            elif len(args) == 1 and args[0][0] == '[':
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

                    for value, _ in enumerate(bootlist):
                        try:
                            newlist += currentlist[int(bootlist[value]) -1]
                        except:
                            raise InvalidCommandLineError("Invalid entry " \
                                  "number passed to bootorder. Please \n" \
                                  "       run bootorder without arguments" \
                                  " for possible boot \n       order numbers. ")

                        removallist.remove(currentlist[int(bootlist[value]) -1])

                        if removallist:
                            newlist += ","

                    if not removallist:
                        newlist += "]"
                    else:
                        for value, _ in enumerate(removallist):
                            newlist += removallist[value]

                            if not value == len(removallist) - 1:
                                newlist += ","

                        newlist += "]"

                    if options.biospassword:
                        newlist += " --biospassword " + options.biospassword

                    if options.reboot:
                        newlist += ' --commit --reboot ' + options.reboot
                    elif options.commit:
                        newlist += " --commit"

                    self.setobj.run("PersistentBootConfigOrder=" + newlist)
            else:
                currlist = bootsettings["PersistentBootConfigOrder"]
                if not isinstance(currlist, list):
                    templist = ast.literal_eval(currlist[1:-1])
                    currlist = [n.strip() for n in templist]
                remlist = copy.deepcopy(currlist)
                if len(args) > len(currlist):
                    raise InvalidCommandLineError("Number of entries is " \
                                  "greater than the current boot order length.")
                newlist = []
                for arg in args:
                    argmatch = [val for val in remlist if fnmatch.fnmatch(val, arg)]
                    if not argmatch and not options.ime:
                        raise InvalidCommandLineError("Invalid entry passed: "\
                            "{0}. Please run bootorder to check for possible "\
                            "values and reevaluate.\n".format(arg))
                    if argmatch:
                        newlist.extend(argmatch)
                        _ = [remlist.remove(val) for val in newlist if val in remlist]
                newlist.extend(remlist)
                strlist = '['
                concatlist = reduce((lambda x, y: x+','+ y), newlist)
                strlist = strlist + concatlist + ']'

                if options.biospassword:
                    strlist += " --biospassword " + options.biospassword
                if options.reboot:
                    strlist += ' --commit --reboot ' + options.reboot
                elif options.commit:
                    strlist += " --commit"
                self.setobj.run("PersistentBootConfigOrder=" + strlist)
        else:
            if not options.onetimeboot is None:
                entry = options.onetimeboot

                if not bootstatus['Boot']['BootSourceOverrideEnabled'] == 'Once':
                    bootoverride = " Boot/BootSourceOverrideEnabled=Once"
            elif not options.continuousboot is None:
                entry = options.continuousboot

                if not bootstatus['Boot']['BootSourceOverrideEnabled'] == 'Continuous':
                    bootoverride = " Boot/BootSourceOverrideEnabled=Continuous"
            else:
                entry = "JacksBootOption"
                if not bootstatus['Boot']['BootSourceOverrideEnabled'] == 'Disabled':
                    if currentsettings.dict['Boot']['BootSourceOverrideEnabled'] == 'Disabled':
                        bootoverride = "Boot/BootSourceOverrideTarget=None"\
                            " Boot/BootSourceOverrideEnabled=Disabled"
                    else:
                        bootoverride = "Boot/BootSourceOverrideTarget=None"

            newlist = ""

            if entry.lower() in (item.lower() for item in onetimebootsettings\
                        ["Boot"][self.typepath.defs.bootoverridetargettype]):

                if entry and isinstance(entry, six.string_types):
                    entry = entry.upper()

                entry = self.searchcasestring(entry, onetimebootsettings["Boot"]\
                                    [self.typepath.defs.bootoverridetargettype])

                if not entry == targetstatus['Boot']['BootSourceOverrideTarget']:
                    newlist += " Boot/BootSourceOverrideTarget=" + entry

                if bootoverride:
                    newlist += bootoverride

                if options.biospassword and newlist:
                    newlist += " --biospassword " + options.biospassword

                if options.reboot and newlist:
                    newlist += ' --commit --reboot ' + options.reboot
                elif options.commit and newlist:
                    newlist += " --commit"

                if newlist:
                    self.setobj.run(newlist)
                else:
                    raise InvalidOrNothingChangedSettingsError("Entry is the current boot setting.")
            elif uefionetimebootsettings and uefionetimebootsettings["Boot"]\
                    ["UefiTargetBootSourceOverrideSupported"] and entry in (item for \
                                    item in uefionetimebootsettings["Boot"]\
                                    ["UefiTargetBootSourceOverrideSupported"]):
                if entry and isinstance(entry, six.string_types):
                    entry = entry.upper()

                entry = self.searchcasestring(entry, uefionetimebootsettings\
                            ["Boot"]["UefiTargetBootSourceOverrideSupported"])
                try:
                    #gen10
                    allowable_vals = next(iter(self.getobj.getworkerfunction(\
                      ['Boot/UefiTargetBootSourceOverride@Redfish.AllowableValues'], options, \
                      results=True, uselist=True)), {})['Boot']\
                                        ['UefiTargetBootSourceOverride@Redfish.AllowableValues']
                    for source in bootsources:
                        if source['StructuredBootString'].upper() == entry.upper():
                            for val in allowable_vals:
                                if 'UEFIDevicePath' in source and \
                                                        source['UEFIDevicePath'].endswith(val):
                                    entry = val
                                    break
                except KeyError:
                    pass

                if not entry == uefitargetstatus['Boot']['UefiTargetBootSourceOverride']:
                    newlist += " Boot/UefiTargetBootSourceOverride=" + entry
                elif not targetstatus['Boot']['BootSourceOverrideTarget'] == 'UefiTarget':
                    newlist += " Boot/BootSourceOverrideTarget=UefiTarget"

                if bootoverride:
                    if self.typepath.defs.isgen9 and newlist:
                        if not bootoverride.split('=')[-1] == bootstatus['Boot']\
                                                                    ['BootSourceOverrideEnabled']:
                            #Preemptively set UefiTargetBootSourceOverride so iLO 4 doesn't complain
                            self._rdmc.app.patch_handler(self.typepath.defs.systempath, \
                                                {"Boot": {"UefiTargetBootSourceOverride": entry}},\
                                                silent=True, service=True)
                            self._rdmc.app.select(selector=self._rdmc.app.get_selector(), rel=True)
                            newlist = ""
                            newlist += bootoverride
                    else:
                        newlist += bootoverride

                if options.reboot and newlist:
                    newlist += ' --commit --reboot ' + options.reboot
                elif options.commit and newlist:
                    newlist += " --commit"

                if newlist:
                    try:
                        self.setobj.run(newlist)
                    except InvalidOrNothingChangedSettingsError:
                        if self.typepath.defs.isgen9:
                            pass
                        else:
                            raise
                else:
                    raise InvalidOrNothingChangedSettingsError("Entry is the " \
                                                    "current boot setting.\n")
            elif options.disablebootflag:

                if bootoverride:
                    newlist += bootoverride

                if options.reboot:
                    newlist += ' --commit --reboot ' + options.reboot
                elif options.commit and newlist:
                    newlist += " --commit"

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

        results = self._rdmc.app.select(selector=self.typepath.defs.hpsecureboot)

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
                sys.stderr.write("DeletePK option is not available on Gen9.\n")

    def print_out_boot_order(self, content, onetimecontent, uefionetimecontent,\
                              bootmode, bootsources, bootstatus, targetstatus):
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
        if content is None:
            raise BootOrderMissingEntriesError("No entries found in " \
                                                "current boot order.\n\n")
        else:
            self.print_boot_helper(content, "\nCurrent Persistent Boot "\
                                   "Order:", bootsources=bootsources)

        bootstatusval = bootstatus['Boot']['BootSourceOverrideEnabled']
        boottoval = targetstatus['Boot']['BootSourceOverrideTarget']
        if bootstatusval == 'Continuous':
            sys.stdout.write('Current continuous boot: {0}\n\n'.format(boottoval))
        elif bootstatusval == 'Once':
            sys.stdout.write('Current one time boot: {0}\n\n'.format(boottoval))

        if onetimecontent is None:
            raise BootOrderMissingEntriesError("No entries found for one" \
                                                " time boot options.\n\n")
        else:
            self.print_boot_helper(onetimecontent["Boot"], \
                                   "Continuous and one time boot options:")

        if bootmode and any([boot.get("BootMode", None)=="Uefi" for boot in bootmode]):
            if uefionetimecontent is None:
                sys.stdout.write("Continuous and one time boot uefi options:\n")
                sys.stdout.write("No entries found for one-time UEFI options or boot source mode "\
                                 "is not set to UEFI.")
            else:
                self.print_boot_helper(uefionetimecontent["Boot"], \
                           "Continuous and one time boot uefi options:",\
                           bootsources=bootsources)

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
        for _, value in content.items():
            sys.stdout.write('\t' * indent + outstring)

            if isinstance(value, list):
                count = 1

                for item in value:
                    sys.stdout.write('\n')

                    if not item:
                        item = str('null')

                    if isinstance(item, six.string_types):
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
                                sys.stdout.write('\t' * indent + str(count) + ". " + str(item))
                        except:
                            sys.stdout.write('\t' * indent + str(count) + ". " + str(item))

                        count += 1
                    else:
                        self.print_boot_helper(item, indent+1)

        sys.stdout.write('\n\n')

    def bootordervalidation(self, options):
        """ Boot order method validation function

        :param options: command line options
        :type options: list.
        """
        inputline = list()

        if self._rdmc.app.config._ac__commit.lower() == 'true':
            options.commit = True

        if options.encode and options.user and options.password:
            options.user = Encryption.decode_credentials(options.user)
            options.password = Encryption.decode_credentials(options.password)

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
                    inputline.extend(["-u", self._rdmc.app.config.get_username()])
                if self._rdmc.app.config.get_password():
                    inputline.extend(["-p", self._rdmc.app.config.get_password()])

        if inputline:
            self.lobobj.loginfunction(inputline)

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
            " command to execute. This option is only used on Gen 9 systems.",
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
        customparser.add_option(
            '--ignorematcherror',
            dest='ime',
            action="store_true",
            help="Use this flag when you want to run multiple matches and "\
            "not throw error in case there are no matches found for given "\
            "expression.",
            default=None,
        )
        customparser.add_option(
            '-e',
            '--enc',
            dest='encode',
            action='store_true',
            help=SUPPRESS_HELP,
            default=False,
        )
