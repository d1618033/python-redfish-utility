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
""" Create Logical Drive Command for rdmc """

import sys

from argparse import ArgumentParser

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group
from rdmc_helper import ReturnCodes, InvalidCommandLineError, InvalidCommandLineErrorOPTS, \
                        Encryption

class CreateLogicalDriveCommand(RdmcCommandBase):
    """ Create logical drive command """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='createlogicaldrive',\
            usage='createlogicaldrive [OPTIONS]\n\n\tTo create a quick ' \
                'logical drive.\n\texample: createlogicaldrive quickdrive ' \
                '<raid-level> <num-drives> <media-type> <interface-type> ' \
                '<drive-location> --controller=1\n\n\tTo create a custom ' \
                'logical drive.\n\texample: createlogicaldrive customdrive ' \
                '<raid-level> <physicaldriveindex(s)> --controller=1 '\
                '--name=drivename ' \
                '--spare-drives=3,4 --spare-type=Dedicated --capacityGiB=10 ' \
                '--accelerator-type=None\n\n\tOPTIONS:\n\traid-level:\t\t' \
                'Raid0, Raid1, Raid1ADM, Raid10, Raid10ADM, Raid5, Raid50, ' \
                'Raid6, Raid60\n\tphysicaldriveindex(s):\tIndex, Drive-name\n\t' \
                'media-type:\t\tSSD,HDD\n\tinterface-type:' \
                '\t\tSAS, SATA\n\tdrive-location:\t\tInternal, External\n\t' \
                '--spare-type:\t\tDedicated, Roaming\n\t--accelerator-type:\t' \
                'ControllerCache, IOBypass, None\n\t--paritytype:\t\tDefault, Rapid' \
                '\n\t--capacityGiB:\t\t-1 (for Max Size)\n\t--capacityBlocks:\t' \
                '-1 (for Max Size)\n\n\t' \
                'NOTE: When you select multiple physicaldrives you can select by both\n\t'\
                'physical drive name and by the index at the same time.\n\t' \
                'You can also select controllers by slot number as well as index.',\
            summary='Creates a new logical drive on the selected controller.',\
            aliases=['createlogicaldrive'],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)

    def run(self, line):
        """ Main disk inventory worker function

        :param line: command line input
        :type line: string.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.createlogicaldrivevalidation(options)

        self.selobj.selectfunction("SmartStorageConfig.")
        content = self._rdmc.app.getprops()
        if not options.controller:
            raise InvalidCommandLineError('You must include a controller to select.')
        controllist = []
        if not args:
            raise InvalidCommandLineError('Please choose customdrive or quickdrive creation.')
        elif args[0].lower() == 'customdrive' and not len(args) == 3:
            raise InvalidCommandLineError('customdrive takes 2 arguments')
        elif args[0].lower() == 'quickdrive' and not len(args) == 6:
            raise InvalidCommandLineError('quickdrive takes 5 arguments')
        elif not args[0] in ['quickdrive', 'customdrive']:
            raise InvalidCommandLineError('Please choose customdrive or quickdrive creation.')

        try:
            if options.controller.isdigit():
                if int(options.controller) > 0:
                    controllist.append(content[int(options.controller) - 1])
            else:
                slotcontrol = options.controller.lower().strip('\"').split('slot')[-1].lstrip()
                for control in content:
                    if slotcontrol.lower() == control["Location"].lower().split('slot')[-1].\
                                                                                        lstrip():
                        controllist.append(control)
            if not controllist:
                raise InvalidCommandLineError("")
        except InvalidCommandLineError:
            raise InvalidCommandLineError("Selected controller not found in the current inventory "\
                                          "list.")
        for controller in controllist:
            if self.createlogicaldrive(args[0], args[1:], options, controller):
                controller['DataGuard'] = "Disabled"

                self._rdmc.app.put_handler(controller["@odata.id"], \
                        controller, headers={'If-Match': self.getetag(controller['@odata.id'])})
                self._rdmc.app.download_path([controller["@odata.id"]], rel=True, \
                                             crawl=False)
        #Return code
        return ReturnCodes.SUCCESS

    def createlogicaldrive(self, drivetype, args, options, controller):
        """ Create logical drive """
        raidlvllist = ['Raid0', 'Raid1', 'Raid1ADM', 'Raid10', 'Raid10ADM',\
                                        'Raid5', 'Raid50', 'Raid6', 'Raid60']
        interfacetypelist = ['SAS', 'SATA']
        mediatypelist = ['SSD', 'HDD']
        sparetypelist = ['Dedicated', 'Roaming']
        acceltypelist = ['ControllerCache', 'IOBypass', 'None']
        locationtypelist = ['Internal', 'External']
        legacylist = ['Primary', 'Secondary', 'All', 'None']
        paritylist = ['Default', 'Rapid']

        sparedrives = []
        newdrive = {}

        changes = False
        itemadded = False

        for item in raidlvllist:
            if args[0].lower() == item.lower():
                if drivetype == 'customdrive':
                    drivecount = len(args[1].replace(', ', ',').split(','))
                else:
                    try:
                        drivecount = int(args[1])
                    except ValueError:
                        raise InvalidCommandLineError('Number of drives is not an integer.')
                if self.raidvalidation(item.lower(), drivecount, options):
                    itemadded = True
                    newdrive["Raid"] = item
                break

        if not itemadded:
            raise InvalidCommandLineError('Invalid raid type or configuration.')
        else:
            itemadded = False

        if drivetype == 'customdrive':
            if options.sparedrives:
                sparedrives = options.sparedrives.replace(', ', ',').split(',')
                newdrive["SpareDrives"] = []
                newdrive["SpareRebuildMode"] = 'Dedicated'

            drives = args[1].replace(', ', ',').split(',')
            newdrive["DataDrives"] = []

            for idx, pdrive in enumerate(controller['PhysicalDrives']):
                for drive in drives:
                    if drive == str(idx+1) or drive == str(pdrive["Location"]):
                        newdrive["DataDrives"].append(pdrive["Location"])

                for drive in sparedrives:
                    if drive == str(idx+1):
                        newdrive["SpareDrives"].append(pdrive["Location"])

            if drivecount > len(newdrive["DataDrives"]):
                raise InvalidCommandLineError("Not all of the selected drives could " \
                                                  "be found in the specified locations.")

            if options.sparetype:
                itemadded = False
                for item in sparetypelist:
                    if options.sparetype.lower() == item.lower():
                        newdrive["SpareRebuildMode"] = item
                        itemadded = True
                        break

                if not itemadded:
                    raise InvalidCommandLineError('Invalid spare drive type.')

            if options.drivename:
                newdrive["LogicalDriveName"] = options.drivename

            if options.capacitygib:
                try:
                    capacitygib = int(options.capacitygib)
                except ValueError:
                    raise InvalidCommandLineError('Capacity is not an integer.')
                newdrive["CapacityGiB"] = capacitygib

            if options.acceleratortype:
                itemadded = False
                for item in acceltypelist:
                    if options.acceleratortype.lower() == item.lower():
                        newdrive["Accelerator"] = item
                        itemadded = True
                        break

                if not itemadded:
                    raise InvalidCommandLineError('Invalid accelerator type.')

            if options.legacyboot:
                itemadded = False
                for item in legacylist:
                    if options.legacyboot.lower() in item.lower():
                        newdrive["LegacyBootPriority"] = item
                        itemadded = True
                        break

                if not itemadded:
                    raise InvalidCommandLineError('Invalid legacy boot priority.')

            if options.capacityblocks:
                try:
                    capacityblocks = int(options.capacityblocks)
                except ValueError:
                    raise InvalidCommandLineError('Capacity is not an integer.')

                newdrive["CapacityBlocks"] = capacityblocks

            if options.paritygroup:
                try:
                    paritygroup = int(options.paritygroup)
                except ValueError:
                    raise InvalidCommandLineError('Parity group is not an integer.')

                newdrive["ParityGroupCount"] = paritygroup

            if options.paritytype:
                itemadded = False
                for item in paritylist:
                    if options.paritytype.lower() == item.lower():
                        newdrive["ParityInitializationType"] = item
                        itemadded = True
                        break

                if not itemadded:
                    raise InvalidCommandLineError("Invalid parity type")

            if options.blocksize:
                try:
                    blocksize = int(options.blocksize)
                except ValueError:
                    raise InvalidCommandLineError('Block size is not an integer.')

                newdrive["BlockSizeBytes"] = blocksize

            if options.stripsize:
                try:
                    stripsize = int(options.stripsize)
                except ValueError:
                    raise InvalidCommandLineError('Strip size is not an integer.')

                newdrive["StripSizeBytes"] = stripsize

            if options.stripesize:
                try:
                    stripesize = int(options.stripesize)
                except ValueError:
                    raise InvalidCommandLineError('Stripe size is not an integer.')

                newdrive["StripeSizeBytes"] = stripesize
        elif drivetype == 'quickdrive':
            try:
                numdrives = int(args[1])
            except ValueError:
                raise InvalidCommandLineError('Number of drives is not an integer.')

            newdrive["DataDrives"] = {"DataDriveCount": numdrives, "DataDriveMinimumSizeGiB": 0}
            for item in mediatypelist:
                if args[2].lower() == item.lower():
                    newdrive["DataDrives"]["DataDriveMediaType"] = item
                    itemadded = True
                    break
            if not itemadded:
                raise InvalidCommandLineError('Invalid media type.')
            else:
                itemadded = False
            for item in interfacetypelist:
                if args[3].lower() == item.lower():
                    newdrive["DataDrives"]["DataDriveInterfaceType"] = item
                    itemadded = True
                    break
            if not itemadded:
                raise InvalidCommandLineError('Invalid interface type.')
            else:
                itemadded = False
            for item in locationtypelist:
                if args[4].lower() == item.lower():
                    newdrive["DataDrives"]["DataDriveLocation"] = item
                    itemadded = True
                    break
            if not itemadded:
                raise InvalidCommandLineError('Invalid drive location type.')
            if options.minimumsize:
                try:
                    minimumsize = int(options.minimumsize)
                except ValueError:
                    raise InvalidCommandLineError('Minimum size is not an integer.')
                newdrive["DataDrives"]["DataDriveMinimumSizeGiB"] = minimumsize

        if newdrive:
            changes = True
            controller['LogicalDrives'].append(newdrive)

        return changes

    def getetag(self, path):
        """ get etag from path """
        etag = None
        instance = self._rdmc.app.monolith.path(path)
        if instance:
            etag = instance.resp.getheader('etag') if 'etag' in instance.resp.getheaders() \
                                            else instance.resp.getheader('ETag')
        return etag

    def raidvalidation(self, raidtype, numdrives, options):
        """ vaidation function for raid levels
        :param raidtype: raid type
        :type options: string.
        :param numdrives: number of drives
        :type numdrives: int.
        :param options: command line options
        :type options: list.
        """

        valid = True

        if raidtype == 'raid5':
            if numdrives < 3:
                valid = False
        elif raidtype == 'raid6':
            if numdrives < 4:
                valid = False
        elif raidtype == 'raid50':
            if numdrives < 6:
                valid = False
        elif raidtype == 'raid60':
            if numdrives < 8:
                valid = False

        return valid

    def createlogicaldrivevalidation(self, options):
        """ Create logical drive validation function

        :param options: command line options
        :type options: list.
        """
        client = None
        inputline = list()
        runlogin = False

        try:
            client = self._rdmc.app.current_client
        except:
            if options.user or options.password or options.url:
                if options.url:
                    inputline.extend([options.url])
                if options.user:
                    if options.encode:
                        options.user = Encryption.decode_credentials(options.user)
                    inputline.extend(["-u", options.user])
                if options.password:
                    if options.encode:
                        options.password = Encryption.decode_credentials(options.password)
                    inputline.extend(["-p", options.password])
                if options.https_cert:
                    inputline.extend(["--https", options.https_cert])
            else:
                if self._rdmc.app.config.get_url():
                    inputline.extend([self._rdmc.app.config.get_url()])
                if self._rdmc.app.config.get_username():
                    inputline.extend(["-u", self._rdmc.app.config.get_username()])
                if self._rdmc.app.config.get_password():
                    inputline.extend(["-p", self._rdmc.app.config.get_password()])
                if self._rdmc.app.config.get_ssl_cert():
                    inputline.extend(["--https", self._rdmc.app.config.get_ssl_cert()])

        if inputline or not client:
            runlogin = True
            if not inputline:
                sys.stdout.write('Local login initiated...\n')

        if runlogin:
            self.lobobj.loginfunction(inputline)

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        add_login_arguments_group(customparser)

        customparser.add_argument(
            '--controller',
            dest='controller',
            help="""Use this flag to select the corresponding controller """\
                """using either the slot number or index.""",
            default=None,
        )
        customparser.add_argument(
            '-n',
            '--name',
            dest='drivename',
            help="""Optionally include to set the drive name (usable in """ \
                """custom creation only).""",
            default=None,
        )
        customparser.add_argument(
            '--spare-drives',
            dest='sparedrives',
            help="""Optionally include to set the spare drives by the """ \
                """physical drive's index. (usable in custom creation only)""",
            default=None,
        )
        customparser.add_argument(
            '--minimumSize',
            dest='minimumsize',
            help="""Optionally include to set the minimum size of the drive """ \
                """in GiB. (usable in quick creation only, use -1 for max size)""",
            default=None,
        )
        customparser.add_argument(
            '--capacityGiB',
            dest='capacitygib',
            help="""Optionally include to set the capacity of the drive in """ \
                """GiB. (usable in custom creation only, use -1 for max """ \
                """size)""",
            default=None,
        )
        customparser.add_argument(
            '--spare-type',
            dest='sparetype',
            help="""Optionally include to choose the spare drive type. """ \
                """(usable in custom creation only)""",
            default=None,
        )
        customparser.add_argument(
            '--accelerator-type',
            dest='acceleratortype',
            help="""Optionally include to choose the accelerator type.""",
            default=None,
        )
        customparser.add_argument(
            '--legacy-boot',
            dest='legacyboot',
            help="""Optionally include to choose the legacy boot priority. """ \
                """(usable in custom creation only)""",
            default=None,
        )
        customparser.add_argument(
            '--capacityBlocks',
            dest='capacityblocks',
            help="""Optionally include to choose the capacity in blocks. """ \
                """(use -1 for max size, usable in custom creation only)""",
            default=None,
        )
        customparser.add_argument(
            '--paritygroupcount',
            dest='paritygroup',
            help="""Optionally include to include the number of parity """ \
                """groups to use. (only valid for certain RAID levels)""",
            default=None,
        )
        customparser.add_argument(
            '--paritytype',
            dest='paritytype',
            help="""Optionally include to choose the parity initialization""" \
                """ type. (usable in custom creation only)""",
            default=None,
        )
        customparser.add_argument(
            '--block-size-bytes',
            dest='blocksize',
            help="""Optionally include to choose the block size of the disk""" \
                """ drive. (usable in custom creation only)""",
            default=None,
        )
        customparser.add_argument(
            '--strip-size-bytes',
            dest='stripsize',
            help="""Optionally include to choose the strip size in bytes. """ \
                """(usable in custom creation only)""",
            default=None,
        )
        customparser.add_argument(
            '--stripe-size-bytes',
            dest='stripesize',
            help="""Optionally include to choose the stripe size in bytes. """ \
                """(usable in custom creation only)""",
            default=None,
        )
