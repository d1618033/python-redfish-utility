###
# Copyright 2016-2021 Hewlett Packard Enterprise, Inc. All rights reserved.
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
""" Smart Array Command for rdmc """
import sys
import json

# from redfish.ris.rmc_helper import EmptyRaiseForEAFP

import redfish

from argparse import ArgumentParser, SUPPRESS, RawDescriptionHelpFormatter

# from rdmc_base_classes import RdmcCommandBase, HARDCODEDLIST

try:
    from rdmc_base_classes import RdmcCommandBase, HARDCODEDLIST
except ImportError:
    from ilorest.rdmc_base_classes import RdmcCommandBase, HARDCODEDLIST
try:
    from rdmc_helper import (
        ReturnCodes,
        InvalidCommandLineError,
        Encryption,
        IncompatableServerTypeError,
        InvalidCommandLineErrorOPTS,
        UI,
        InvalidFileInputError,
    )
except ImportError:
    from ilorest.rdmc_helper import (
        ReturnCodes,
        InvalidCommandLineError,
        Encryption,
        IncompatableServerTypeError,
        InvalidCommandLineErrorOPTS,
        UI,
        InvalidFileInputError,
    )
from redfish.ris.resp_handler import ResponseHandler

# from redfish.ris.utils import iterateandclear

__config_file__ = "smartarray_config.json"

# from rdmc_base_classes import HARDCODEDLIST

__subparsers__ = ["load", "save", "state"]


class SmartArrayCommand:
    """Smart array command"""

    def __init__(self):
        self.ident = {
            "name": "smartarray",
            "usage": None,
            "description": "\tRun without arguments for the "
                           "current list of smart array controllers.\n\texample: "
                           "smartarray\n\n\tTo get more details on a specific controller "
                           "select it by index.\n\texample: smartarray --controller=2"
                           "\n\n\tTo get more details on a specific controller select "
                           'it by location.\n\texample: smartarray --controller "Slot 0"'
                           "\n\n\tIn order to get a list of all physical drives for "
                           "each controller.\n\texample: smartarray --physicaldrives"
                           "\n\n\tTo obtain details about physical drives for a "
                           "specific controller.\n\texample: smartarray --controller=3 "
                           "--physicaldrives\n\n\tTo obtain details about a specific "
                           "physical drive for a specific controller.\n\texample: smartarray "
                           "--controller=3 --pdrive=1I:1:1\n\n\tIn order to get a list of "
                           "all volumes for the each controller.\n\texample: "
                           "smartarray --logicaldrives\n\n\tTo obtain details about "
                           "volumes for a specific controller.\n\texample: "
                           "smartarray --controller=3 --logicaldrives\n\n\tTo obtain "
                           "details about a specific volume for a specific "
                           "controller.\n\texample: smartarray --controller=3 --ldrive=1\n",
            "summary": "Discovers all storage controllers installed in the "
                       "server and managed by the SmartStorage.",
            "aliases": ["storagearray"],
            "auxcommands": ["SelectCommand"],
        }
        self.config_file = None
        self.fdata = None
        self.cmdbase = None
        self.rdmc = None
        self.auxcommands = dict()

    def file_handler(self, filename, operation, options, data=None, sk=None):
        """
        Wrapper function to read or write data to a respective file

        :param data: data to be written to output file
        :type data: container (list of dictionaries, dictionary, etc.)
        :param file: filename to be written
        :type file: string (generally this should be self.clone_file or tmp_clone_file
        :param operation: file operation to be performed
        :type operation: string ('w+', 'a+', 'r+')
        :param sk: sort keys flag
        :type sk: boolean
        :param options: command line options
        :type options: attribute
        :returns: json file data
        """
        writeable_ops = ["w", "w+", "a", "a+"]
        readable_ops = ["r", "r+"]
        fdata = None

        try:
            if operation in writeable_ops:
                if getattr(options, "encryption", False):
                    with open(filename, operation + "b") as outfile:
                        outfile.write(
                            Encryption().encrypt_file(
                                json.dumps(
                                    data,
                                    indent=2,
                                    cls=redfish.ris.JSONEncoder,
                                    sort_keys=sk,
                                ),
                                getattr(options, "encryption", False),
                            )
                        )
                else:
                    with open(filename, operation) as outfile:
                        outfile.write(
                            json.dumps(
                                data,
                                indent=2,
                                cls=redfish.ris.JSONEncoder,
                                sort_keys=sk,
                            )
                        )
            else:
                if getattr(options, "encryption", False):
                    with open(filename, operation + "b") as file_handle:
                        fdata = json.loads(
                            Encryption().decrypt_file(
                                file_handle.read(),
                                getattr(options, "encryption", False),
                            )
                        )
                else:
                    with open(filename, operation) as file_handle:
                        fdata = json.loads(file_handle.read())
                return fdata
        except Exception as excp:
            raise InvalidFileInputError(
                "Unable to open file: %s.\nVerify the file location "
                "and the file has a valid JSON format.\n" % excp
            )

    def run(self, line, help_disp=False):
        """Main smart array worker function

        :param line: command line input
        :type line: string.
        """
        if help_disp:
            line.append("-h")
            try:
                (_, _) = self.rdmc.rdmc_parse_arglist(self, line)
            except:
                return ReturnCodes.SUCCESS
            return ReturnCodes.SUCCESS
        try:
            ident_subparser = False
            for cmnd in __subparsers__:
                if cmnd in line:
                    (options, args) = self.rdmc.rdmc_parse_arglist(self, line)
                    if not line or line[0] == "help":
                        self.parser.print_help()
                        return ReturnCodes.SUCCESS
                    ident_subparser = True
                    break
            if not ident_subparser:
                (options, args) = self.rdmc.rdmc_parse_arglist(self, line, default=True)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.smartarrayvalidation(options)
        ilo_ver = self.rdmc.app.getiloversion()

        if options.command == "state":
            if ilo_ver >= 6.110:
                storage_ctlr = self.storagecontroller(options, print_ctrl=False, single_use=True)
                for storage in storage_ctlr:
                    if storage_ctlr[storage].get("@Redfish.Settings"):
                        time = storage_ctlr[storage]["@Redfish.Settings"].get(
                            "Time", "Not Available"
                        )
                        sys.stdout.write("Last Configuration Attempt: %s\n" % str(time))
                        for message in storage_ctlr[storage]["@Redfish.Settings"].get(
                                "Messages", []
                        ):
                            ResponseHandler(
                                self.rdmc.app.validationmanager,
                                self.rdmc.app.typepath.defs.messageregistrytype,
                            ).message_handler(response_data=message, message_text="", verbosity=2, dl_reg=False)
                    else:
                        sys.stdout.write(
                            "Previous smart array configuration status messages are "
                            "not available for controller '%s - %s - %s' (@Redfish.Settings not "
                            "available).\n"
                            % (
                                storage,
                                storage_ctlr[storage].get("Location", "Unknown"),
                                storage_ctlr[storage].get("Model", "Unknown"),
                            )
                        )
            else:
                controllers = self.controllers(options, print_ctrl=False, single_use=True)
                for controller in controllers:
                    if controllers[controller].get("@Redfish.Settings"):
                        time = controllers[controller]["@Redfish.Settings"].get(
                            "Time", "Not Available"
                        )
                        sys.stdout.write("Last Configuration Attempt: %s\n" % str(time))
                        for message in controllers[controller]["@Redfish.Settings"].get(
                                "Messages", []
                        ):
                            ResponseHandler(
                                self.rdmc.app.validationmanager,
                                self.rdmc.app.typepath.defs.messageregistrytype,
                            ).message_handler(response_data=message, message_text="", verbosity=2, dl_reg=False)
                    else:
                        sys.stdout.write(
                            "Previous smart array configuration status messages are "
                            "not available for controller '%s - %s - %s' (@Redfish.Settings not "
                            "available).\n"
                            % (
                                controller,
                                controllers[controller].get("Location", "Unknown"),
                                controllers[controller].get("Model", "Unknown"),
                            )
                        )

        if options.command == "save":
            if ilo_ver >= 6.110:
                storage = {}
                storage_Controller = self.rdmc.app.select("StorageCollection", path_refresh=True)
                for sel in storage_Controller:
                    controller_dict = sel.dict
                    mem_Controller = controller_dict["Members"]
                    get_id = mem_Controller[0]["@odata.id"]
                    getval = self.rdmc.app.get_handler(get_id, silent=True, service=True).dict
                    getid = getval["Id"]
                    storage.update(getval)
                    s_controller = self.storagecontroller(options, print_ctrl=False, single_use=True)
                    s_logical_drive = self.storagelogical_drives(options, "", print_ctrl=False, single_use=True)
                    s_physical_drive = self.storagephysical_drives(options,"", print_ctrl=False, single_use=True)
                    storage["Controllers"] = s_controller
                    storage["Drives"] = s_physical_drive
                    storage["Volumes"] = s_logical_drive

                self.file_handler(self.config_file, "w", options, storage, sk=True)
                sys.stdout.write(
                    "Smart Array configuration saved to '%s'.\n" % self.config_file
                )
            else:
                controllers = self.controllers(options, print_ctrl=False, single_use=True)
                for key, controller in controllers.items():
                    physical_drives = self.physical_drives(
                        options, controller, print_ctrl=False, single_use=True
                    )
                    logical_drives = self.logical_drives(
                        options, controller, print_ctrl=False, single_use=True
                    )
                    if self.rdmc.app.typepath.defs.isgen10:
                        for drivec_idx, drivec in enumerate(
                                controller.get("PhysicalDrives", [])
                        ):
                            for drive in physical_drives:
                                if drivec["Location"] == physical_drives[drive]["Location"]:
                                    controller["PhysicalDrives"][drivec_idx].update(
                                        physical_drives[drive]
                                    )
                                    break
                        for drivec_idx, drivec in enumerate(
                                controller.get("LogicalDrives", [])
                        ):
                            for drive in logical_drives:
                                if (
                                        drivec["LogicalDriveNumber"]
                                        == logical_drives[drive]["Id"]
                                ):
                                    controller["LogicalDrives"][drivec_idx].update(
                                        logical_drives[drive]
                                    )
                                    break
                    if controller.get("Links"):
                        controller["Links"]["LogicalDrives"] = logical_drives
                        controller["Links"]["PhysicalDrives"] = physical_drives
                    else:
                        controller["links"]["LogicalDrives"] = logical_drives
                        controller["links"]["PhysicalDrives"] = physical_drives

                self.file_handler(self.config_file, "w", options, controllers, sk=True)
                sys.stdout.write(
                    "Smart Array configuration saved to '%s'.\n" % self.config_file
                )

        if options.command == "load":
            if ilo_ver >= 6.110:
                storage_load = self.file_handler(self.config_file, operation="rb", options=options)
                controller_id = storage_load["Controllers"]
                logical_id = storage_load["Volumes"]
                physical_id = storage_load["Drives"]
                if controller_id:
                    for data in controller_id:
                        id_controller = controller_id[data].get('@odata.id')
                        controllers = self.rdmc.app.get_handler(id_controller, silent=True).dict
                        readonly_removed_controllers = self.smartarrayremovereadonly(controllers)
                        readonly_removed = storage_load["Controllers"]
                        for controller, val in readonly_removed.items():
                            for i in readonly_removed_controllers:
                                try:
                                    if (i in val) and (controllers[i] != val[i]):
                                        body = {str(i): val[i]}
                                        self.rdmc.app.patch_handler(id_controller, body)
                                except:
                                    sys.stdout.write(
                                        "Unable to update the property "
                                        "for: '%s'.\n" % i
                                    )
                                    continue
                if logical_id:
                    for logical_data in logical_id:
                        id_logical = logical_id[logical_data].get('@odata.id')
                        logicals = self.rdmc.app.get_handler(id_logical, silent=True).dict
                        readonly_removed_logical = self.smartarrayremovereadonly(logicals)
                        readonly_logical = storage_load["Volumes"]
                        for logical, val in readonly_logical.items():
                            for l in readonly_removed_logical:
                                try:
                                    if (l in val) and (logicals[l] != val[l]):
                                        body = {str(l): val[l]}
                                        self.rdmc.app.patch_handler(id_logical, body)
                                except:
                                    sys.stdout.write(
                                        "Unable to update the property "
                                        "for: '%s'.\n" % l
                                    )
                                    continue
                if physical_id:
                    for physical_data in physical_id:
                        id_physical = physical_id[physical_data].get('@odata.id')
                        physicals = self.rdmc.app.get_handler(id_physical, silent=True).dict
                        readonly_removed_physical = self.smartarrayremovereadonly(physicals)
                        readonly_physical = storage_load["Drives"]
                        for logical, val in readonly_physical.items():
                            for l in readonly_removed_physical:
                                try:
                                    if (l in val) and (physicals[l] != val[l]):
                                        body = {str(l): val[l]}
                                        self.rdmc.app.patch_handler(id_physical, body)
                                except:
                                    sys.stdout.write(
                                        "Unable to update the property "
                                        "for: '%s'.\n" % l
                                    )
                                    continue
                sys.stdout.write(
                    "Smart Array configuration loaded. Reboot the server to "
                    "finalize the configuration.\n"
                )

            else:
                controllers = self.file_handler(
                    self.config_file, operation="rb", options=options
                )

                for controller in controllers:
                    put_path = controllers[controller]["@Redfish.Settings"]["SettingsObject"]["@odata.id"]
                    if controllers[controller].get("DataGuard"):
                        controllers[controller]["DataGuard"] = "Disabled"
                        readonly_removed = self.rdmc.app.removereadonlyprops(
                            controllers[controller]
                        )
                        readonly_removed["LogicalDrives"] = controllers[controller][
                            "LogicalDrives"
                        ]
                        readonly_removed["PhysicalDrives"] = controllers[controller][
                            "PhysicalDrives"
                        ]
                        # self.rdmc.app.put_handler(controllers[controller]["@odata.id"], readonly_removed)
                        self.rdmc.app.put_handler(put_path, readonly_removed)

                        sys.stdout.write(
                            "Smart Array configuration loaded. Reboot the server to "
                            "finalize the configuration.\n"
                        )
        elif options.command == "default":
            if getattr(options, "json", False):
                if ilo_ver >= 6.110:
                    self.storagecontroller(options, print_ctrl=False, single_use=False)
                else:
                    self.controllers(options, print_ctrl=False, single_use=False)
            else:
                if ilo_ver >= 6.110:
                    self.storagecontroller(options, print_ctrl=True, single_use=False)
                else:
                    self.controllers(options, print_ctrl=True, single_use=False)

        self.cmdbase.logout_routine(self, options)
        # Return code
        return ReturnCodes.SUCCESS

    def smartarrayremovereadonly(self, controller):
        templist = [
            "Ports",
            "CacheSummary",
            "SupportedRAIDTypes",
            "PCIeInterface",
            "SupportedControllerProtocols",
            "SupportedDeviceProtocols",
            "SKU",
            "SpeedGbps",
            "SerialNumber",
            "PartNumber",
            "Model",
            "@odata.etag",
            "Status",
            "Manufacturer",
            "Location",
            "Identifiers",
            "FirmwareVersion",
            "Name",
            "Id",
            "@odata.type",
            "@odata.id",
            "Links",
        ]

        remove_data = self.rdmc.app.removereadonlyprops(controller, False, True, templist)
        return remove_data

    def odataremovereadonly(self, tmp):
        templist = [
            "@odata.etag",
            "@odata.type",
            "@odata.context",
        ]
        remove_data = self.rdmc.app.removereadonlyprops(tmp, False, True, templist)
        return remove_data

    def controllers(self, options, print_ctrl=False, single_use=False):
        """
        Identify/parse volumes (and child properties) of a parent array controller

        :param options: command line options (options.controller is a required attribute)
        :type options: object attributes
        :param print_ctrl: flag for console print enablement/disablement (default disabled)
        :type print_ctrl: bool
        :param single_use: singular usage - True or explore mode - False,
        returns dictionary of results to calling function (default disabled) - see returns.
        :type single_use: bool
        :returns: None, dictionary of all controllers identified by 'Id'
        """

        if getattr(options, "controller", False):
            controller_ident = False
        if (
                not (getattr(options, "json", False))
                and not (getattr(options, "controller", False))
                and print_ctrl and (options.physicaldrives is None)
                and (options.pdrive is None) and (options.logicaldrives is None)
                and (options.ldrive is None)
        ):
            sys.stdout.write("Controllers:\n")

        controller_data = {}

        for sel in self.rdmc.app.select("SmartStorageArrayController", path_refresh=True):
            if "Collection" not in sel.maj_type:
                controller = sel.dict
                if getattr(options, "controller", False):
                    if (
                            getattr(options, "controller", False) == controller["Id"]
                            or getattr(options, "controller", False) == controller["Location"]
                    ):
                        controller_ident = True
                    else:
                        continue

                if self.rdmc.app.typepath.defs.isgen10:
                    for g10controller in self.rdmc.app.select(
                            "SmartStorageConfig.", path_refresh=True
                    ):
                        if g10controller.dict.get("Location") == controller.get(
                                "Location"
                        ):
                            id = controller.get("Id")
                            controller.update(g10controller.dict)
                            if id:  # iLO Bug - overwrite the Id from collection
                                controller["Id"] = id
                            break

                if (
                        print_ctrl and (options.controller is None) and (options.physicaldrives is None)
                        and (options.pdrive is None) and (options.ldrive is None) and
                        (options.logicaldrives is None)
                ):
                    sys.stdout.write(
                        "[%s]: %s - %s\n"
                        % (
                            controller["Id"],
                            controller["Location"],
                            controller["Model"],
                        )
                    )

                    # self.tranverse_func(controller)

                elif (
                        getattr(options, "json", False) and (options.controller is None)
                        and (options.physicaldrives is None)
                        and (options.pdrive is None) and (options.ldrive is None) and
                        (options.logicaldrives is None)
                ):
                    outjson = dict()
                    outjson["Controllers"] = dict()
                    outjson["Controllers"][controller["Id"]] = dict()
                    outjson["Controllers"][controller["Id"]]["Location"] = controller[
                        "Location"
                    ]
                    outjson["Controllers"][controller["Id"]]["Model"] = controller[
                        "Model"
                    ]
                    UI().print_out_json(outjson)

                elif (print_ctrl and (options.controller is not None) and ((options.ldrive is not None) or
                                                                           options.pdrive is not None)):
                    pass

                elif (
                        getattr(options, "json", False) and (options.controller is not None) and
                        ((options.ldrive is not None) or (options.pdrive is not None))
                ):
                    pass

                elif print_ctrl and (options.controller is not None):
                    controller_info = ""
                    controller_info = "------------------------------------------------\n"
                    controller_info += "Controller Info \n"
                    controller_info += "------------------------------------------------\n"
                    controller_info += "Id: %s\n" % controller["Id"]
                    controller_info += "AdapterType: %s\n" % controller["AdapterType"]
                    controller_info += "DataGuard: %s\n" % controller["DataGuard"]
                    controller_info += "Description: %s\n" % controller["Description"]
                    controller_info += "FirmwareVersion: %s\n" % controller["FirmwareVersion"]
                    controller_info += "Name: %s\n" % controller["Name"]
                    controller_info += "Model: %s\n" % controller["Model"]
                    controller_info += "Location: %s\n" % controller["Location"]
                    #controller_info += "Links: %s\n" % controller["Links"]
                    controller_info += "SerialNumber: %s\n" % controller["SerialNumber"]
                    controller_info += "Status: %s\n" % controller["Status"]
                    self.rdmc.ui.printer(controller_info, verbose_override=True)

                elif getattr(options, "json", False) and (options.controller is not None):
                    outjson_data = dict()
                    outjson_data.update({"Id": controller["Id"]})
                    outjson_data.update({"AdapterType": controller["AdapterType"]})
                    outjson_data.update({"DataGuard": controller["DataGuard"]})
                    outjson_data.update({"Description": controller["Description"]})
                    outjson_data.update({"FirmwareVersion": controller["FirmwareVersion"]})
                    outjson_data.update({"Name": controller["Name"]})
                    outjson_data.update({"Model": controller["Model"]})
                    outjson_data.update({"Location": controller["Location"]})
                    #outjson_data.update({"Links": controller["Links"]})
                    outjson_data.update({"SerialNumber": controller["SerialNumber"]})
                    outjson_data.update({"Status": controller["Status"]})
                    UI().print_out_json(outjson_data)

                if (
                        getattr(options, "logicaldrives", False)
                        or getattr(options, "ldrive", False)
                        or single_use
                ):
                    self.logical_drives(options, controller, print_ctrl)

                if (
                        getattr(options, "physicaldrives", False)
                        or getattr(options, "pdrive", False)
                        or single_use
                ):
                    self.physical_drives(options, controller, print_ctrl)

                if single_use:
                    controller_data[controller["Id"]] = controller

        if getattr(options, "controller", False) and not controller_ident and print_ctrl:
            sys.stdout.write(
                "Controller in position '%s' was not found\n"
                % (getattr(options, "controller", False))
            )

        if single_use:
            return controller_data

    def storagecontroller(self, options, print_ctrl=False, single_use=False):

        if getattr(options, "controller", False):
            controller_ident = False

        if (
                not (getattr(options, "json", False))
                and not (getattr(options, "controller", False))
                and print_ctrl and (options.physicaldrives is None)
                and (options.pdrive is None) and (options.logicaldrives is None)
                and (options.ldrive is None)
        ):
            sys.stdout.write("Controllers:\n")

        storage_data = {}
        get_contrller = []

        self.auxcommands["select"].selectfunction("StorageCollection.")
        st_content = self.rdmc.app.getprops()
        for st_controller in st_content:
            path = st_controller["Members"]
            for mem in path:
                for val in mem.values():
                    if "DE" in val:
                        getval = self.rdmc.app.get_handler(val, silent=True, service=True).dict
                        controller = getval["Controllers"]
                        for ctl in controller.values():
                            ctl = ctl + "/0"
                            get_sel = self.rdmc.app.get_handler(ctl, silent=True, service=True)
                        get_contrller.append(get_sel)

        for sel in get_contrller:
            if "Collection" not in sel.path:
                controller = sel.dict
                storage_id = controller["@odata.id"].split("/")
                storage_id = storage_id[6]
                if getattr(options, "controller", False):
                    if (
                            getattr(options, "controller", False) == controller["Id"]
                            or getattr(options, "controller", False)
                            == controller["Location"]["PartLocation"]["ServiceLabel"]
                    ):
                        controller_ident = True
                    else:
                        continue
                if (
                        print_ctrl and (options.controller is None) and (options.physicaldrives is None)
                        and (options.pdrive is None) and (options.ldrive is None) and
                        (options.logicaldrives is None)
                ):
                    sys.stdout.write(
                        "[%s]: %s StorageId=%s - %s\n"
                        % (
                            controller["Id"],
                            controller["Location"]["PartLocation"]["ServiceLabel"],
                            storage_id,
                            controller["Model"],
                        )
                    )

                elif (
                        getattr(options, "json", False) and (options.controller is None) and (
                        options.physicaldrives is None)
                        and (options.pdrive is None) and (options.ldrive is None) and
                        (options.logicaldrives is None)
                ):
                    outjson = dict()
                    outjson["Controllers"] = dict()
                    outjson["Controllers"][controller["Id"]] = dict()
                    outjson["Controllers"][controller["Id"]]["Location"] = controller[
                        "Location"]["PartLocation"]["ServiceLabel"]
                    outjson["Controllers"][controller["Id"]]["StorageId"] = storage_id
                    outjson["Controllers"][controller["Id"]]["Model"] = controller[
                        "Model"
                    ]
                    UI().print_out_json(outjson)

                elif (print_ctrl and (options.controller is not None) and ((options.ldrive is not None) or
                                                                           options.pdrive is not None)):
                    pass

                elif (
                        getattr(options, "json", False) and (options.controller is not None) and
                        ((options.ldrive is not None) or (options.pdrive is not None))
                ):
                    pass

                elif print_ctrl and (options.controller is not None):
                    controller_info = ""
                    controller_info = "------------------------------------------------\n"
                    controller_info += "Controller Info \n"
                    controller_info += "------------------------------------------------\n"
                    controller_info += "Id: %s\n" % controller["Id"]
                    controller_info += "StorageId: %s\n" % storage_id
                    controller_info += "Name: %s\n" % controller["Name"]
                    controller_info += "FirmwareVersion: %s\n" % controller["FirmwareVersion"]
                    controller_info += "Manufacturer: %s\n" % controller["Manufacturer"]
                    controller_info += "Model: %s\n" % controller["Model"]
                    controller_info += "PartNumber: %s\n" % controller["PartNumber"]
                    controller_info += "SerialNumber: %s\n" % controller["SerialNumber"]
                    try:
                        controller_info += "SKU: %s\n" % controller["SKU"]
                    except KeyError:
                        pass
                    controller_info += "Status: %s\n" % controller["Status"]
                    try:
                        controller_info += "SupportedDeviceProtocols: %s\n" % controller["SupportedDeviceProtocols"]
                    except KeyError:
                        pass
                    try:
                        controller_info += "SupportedControllerProtocols: %s\n" % controller[
                            "SupportedControllerProtocols"]
                    except KeyError:
                        pass
                    self.rdmc.ui.printer(controller_info, verbose_override=True)

                elif getattr(options, "json", False) and (options.controller is not None):
                    outjson_data = dict()
                    outjson_data.update({"Id": controller["Id"]})
                    outjson_data.update({"StorageId": storage_id})
                    outjson_data.update({"Name": controller["Name"]})
                    outjson_data.update({"FirmwareVersion": controller["FirmwareVersion"]})
                    outjson_data.update({"Manufacturer": controller["Manufacturer"]})
                    outjson_data.update({"Model": controller["Model"]})
                    outjson_data.update({"PartNumber": controller["PartNumber"]})
                    outjson_data.update({"SerialNumber": controller["SerialNumber"]})
                    try:
                        outjson_data.update({"SKU": controller["SKU"]})
                    except KeyError:
                        pass
                    outjson_data.update({"Status": controller["Status"]})
                    try:
                        outjson_data.update({"SupportedDeviceProtocols": controller["SupportedDeviceProtocols"]})
                    except KeyError:
                        pass
                    try:
                        outjson_data.update(
                            {"SupportedControllerProtocols": controller["SupportedControllerProtocols"]})
                    except KeyError:
                        pass
                    UI().print_out_json(outjson_data)

                if (
                        getattr(options, "logicaldrives", False)
                        or getattr(options, "ldrive", False)
                        or single_use
                ):
                    self.storagelogical_drives(options, controller, print_ctrl)

                if (
                        getattr(options, "physicaldrives", False)
                        or getattr(options, "pdrive", False)
                        or single_use
                ):
                    self.storagephysical_drives(options, controller, print_ctrl)

                if single_use:
                    storage_data[controller["Id"]] = controller
        if (
                getattr(options, "controller", False)
                and not controller_ident
                and print_ctrl
        ):
            sys.stdout.write(
                "Controller in position '%s' was not found\n"
                % (getattr(options, "controller", False))
            )
        if single_use:
            return storage_data

    def storagephysical_drives(self, options, controller, print_ctrl=False, single_use=False):
        found_entries = False
        if not getattr(options, "json", False) and print_ctrl:
            sys.stdout.write("Physical Drives:\n")
        if getattr(options, "pdrive", False):
            pdrive_ident = False
        else:
            pdrive_ident = True
        if single_use:
            physicaldrives = {}

        for sel in self.rdmc.app.select(
                "Drive", path_refresh=True
        ):
            if "Collection" not in sel.maj_type:
                tmp = sel.dict

                if getattr(options, "pdrive", False):
                    pdrive_ident = False
                else:
                    pdrive_ident = True
                # if single_use:
                #    physicaldrives = {}
                found_entries = True

                location = tmp["PhysicalLocation"]["PartLocation"]["ServiceLabel"]
                loc = location.split(":")
                temp_str = str(loc[1].split("=")[1] + ':' + loc[2].split("=")[1] + ':' + loc[3].split("=")[1])
                # temp_str = str(loc[1][-2:] + ':' + loc[2][-1] + ':' + loc[3][-1])
                location = temp_str

                if getattr(options, "pdrive", False):
                    if options.pdrive != location:
                        continue
                    else:
                        pdrive_ident = True
                if single_use:
                    # physicaldrives[tmp["Id"]] = tmp
                    physicaldrives.update({tmp["Id"]: tmp})
                if print_ctrl and pdrive_ident and options.pdrive is None:
                    sys.stdout.write(
                        "\t[%s]: Model %s, Location %s, Type %s, Serial %s - %s Bytes\n"
                        % (
                            location,
                            tmp["Model"],
                            location,
                            tmp["MediaType"],
                            tmp["SerialNumber"],
                            tmp["CapacityBytes"]
                        )
                    )
                elif getattr(options, "json", False) and pdrive_ident and options.pdrive is None:
                    outjson = dict()
                    outjson["PhysicalDrives"] = dict()
                    outjson["PhysicalDrives"][location] = dict()
                    outjson["PhysicalDrives"][location]["Model"] = tmp["Model"]
                    outjson["PhysicalDrives"][location]["Location"] = location
                    outjson["PhysicalDrives"][location]["MediaType"] = tmp["MediaType"]
                    outjson["PhysicalDrives"][location]["SerialNumber"] = tmp["SerialNumber"]
                    outjson["PhysicalDrives"][location]["CapacityBytes"] = tmp["CapacityBytes"]
                    UI().print_out_json(outjson)

                elif print_ctrl and pdrive_ident and options.pdrive is not None:
                    ctl_logical = dict()
                    contoller_loc = controller["Location"]["PartLocation"]["ServiceLabel"] + '-' + controller[
                        "Model"]
                    ctl_logical.update({"Controller": contoller_loc})
                    remove_odata = self.odataremovereadonly(tmp)
                    ctl_logical.update(remove_odata)
                    UI().print_out_json(ctl_logical)

                elif getattr(options, "json", False) and pdrive_ident and options.pdrive is not None:
                    ctl_logical = dict()
                    contoller_loc = controller["Location"]["PartLocation"]["ServiceLabel"] + '-' + controller[
                        "Model"]
                    ctl_logical.update({"Controller": contoller_loc})
                    remove_odata = self.odataremovereadonly(tmp)
                    ctl_logical.update(remove_odata)
                    UI().print_out_json(ctl_logical)

                if getattr(options, "pdrive", False) and pdrive_ident:
                    break
        if getattr(options, "pdrive", False) and not pdrive_ident and print_ctrl:
            sys.stdout.write(
                "\tPhysical drive in position '%s' was not found" % options.pdrive
            )
        elif not found_entries and print_ctrl:
            sys.stdout.write("\tPhysical drives not found.\n")

        if single_use:
            return physicaldrives

    def storagelogical_drives(self, options, controller, print_ctrl=False, single_use=False):
        found_entries = False
        if not getattr(options, "json", False) and print_ctrl:
            sys.stdout.write("Logical Drives:\n")
        if getattr(options, "ldrive", False):
            ldrive_ident = False
        else:
            ldrive_ident = True
        if single_use:
            logicaldrives = {}

        for sel in self.rdmc.app.select(
                "Volume", path_refresh=True
        ):
            if "VolumeCollection" not in sel.maj_type:
                # if "Collection" not in sel.maj_type:
                tmp = sel.dict

                if getattr(options, "ldrive", False):
                    ldrive_ident = False
                else:
                    ldrive_ident = True
                # if single_use:
                #    logicaldrives = {}

                if getattr(options, "ldrive", False):
                    if options.ldrive != tmp["Id"]:
                        continue
                    else:
                        ldrive_ident = True

                if "Identifiers" in tmp:
                    durablename = tmp["Identifiers"]
                    d_name = [name["DurableName"] for name in durablename]
                    found_entries = True

                    if (print_ctrl and ldrive_ident and
                            options.ldrive is None):
                        sys.stdout.write(
                            "\t[%s]: Name %s RAIDType %s VUID %s - %s Bytes\n"
                            % (
                                tmp["Id"],
                                tmp["Name"],
                                tmp["RAIDType"],
                                d_name[0],
                                tmp["CapacityBytes"],
                            )
                        )
                    elif getattr(options, "json", False) and ldrive_ident and options.ldrive is None:
                        outjson = dict()
                        outjson["LogicalDrives"] = dict()
                        outjson["LogicalDrives"][tmp["Id"]] = dict()
                        outjson["LogicalDrives"][tmp["Id"]]["LogicalDriveName"] = tmp[
                            "Name"
                        ]
                        outjson["LogicalDrives"][tmp["Id"]]["RAIDType"] = tmp["RAIDType"]
                        outjson["LogicalDrives"][tmp["Id"]]["VolumeUniqueIdentifier"] = d_name[0]
                        outjson["LogicalDrives"][tmp["Id"]]["CapacityMiB"] = tmp[
                            "CapacityBytes"
                        ]
                        UI().print_out_json(outjson)

                    elif print_ctrl and ldrive_ident and options.ldrive is not None:
                        ctl_logical = dict()
                        contoller_loc = controller["Location"]["PartLocation"]["ServiceLabel"] + '-' + controller[
                            "Model"]
                        ctl_logical.update({"Controller": contoller_loc})
                        remove_odata = self.odataremovereadonly(tmp)
                        ctl_logical.update(remove_odata)
                        UI().print_out_json(ctl_logical)

                    elif getattr(options, "json", False) and ldrive_ident and options.ldrive is not None:
                        ctl_logical = dict()
                        contoller_loc = controller["Location"]["PartLocation"]["ServiceLabel"] + '-' + controller[
                            "Model"]
                        ctl_logical.update({"Controller": contoller_loc})
                        remove_odata = self.odataremovereadonly(tmp)
                        ctl_logical.update(remove_odata)
                        UI().print_out_json(ctl_logical)

                    # this piece of code will give drive data which is link to volumes
                    # try:
                    #    tmp2 = tmp["Links"]["Drives"][self.rdmc.app.typepath.defs.hrefstring]
                    # except:
                    #    data_drive = tmp["Links"]["Drives"]
                    #    tmp2 = [drive["@odata.id"] for drive in data_drive]
                    #    tmp2 = tmp2[0]
                    # finally:
                    #    tmp2 = self.rdmc.app.get_handler(tmp2, silent=True).dict
                    # if ldrive_ident:
                    #    datadrive = self.get_storage_data_drives(
                    #        options, tmp2, print_ctrl, single_use
                    #    )
                    #    try:
                    #        tmp["Links"]["Drives"] = datadrive
                    #    except:
                    #        tmp["links"]["Drives"] = datadrive
                    if single_use:
                        # logicaldrives[tmp["Id"]] = tmp
                        logicaldrives.update({tmp["Id"]: tmp})
                    if getattr(options, "ldrive", False) and ldrive_ident:
                        break

        if getattr(options, "ldrive", False) and not ldrive_ident:
            sys.stdout.write("\tLogical drive in position '%s' was not found.\n" % options.ldrive)

        elif not found_entries and print_ctrl:
            sys.stdout.write("\tLogical drives not found.\n")

        if single_use:
            return logicaldrives

    def get_storage_data_drives(self, options, drives, print_ctrl=False, single_use=False):
        if not (getattr(options, "json", False)) and print_ctrl:
            sys.stdout.write("\tData Drives:\n\n")
        if single_use:
            subsetdrives = {}
            subsetdrives[drives["Id"]] = drives
        found_entries = False
        if print_ctrl:
            self.tranverse_func(drives)
            found_entries = True

        elif getattr(options, "json", False):
            UI().print_out_json(drives)

        if not found_entries and print_ctrl:
            sys.stdout.write("\t\tComponent drives not found.\n")

        if single_use:
            return subsetdrives

    def tranverse_func(self, data, indent=0):
        for key, value in data.items():
            sys.stdout.write("\t %s :" % str(key))
            if isinstance(value, dict):
                self.tranverse_func(value, indent + 1)
            else:
                sys.stdout.write("%s \n" % str(value))

    def physical_drives(self, options, content, print_ctrl=False, single_use=False):
        """
        Identify/parse physical drives (and child properties) of a parent array controller

        :param options: command line options
        :type options: object attributes
        :param content: dictionary of physical drive href or @odata.id paths (expect @odata.type
        "SmartStorageArrayController", @odata.id /Systems/1/SmartStorage/ArrayControllers/X/)
        :type content: dict
        :param print_ctrl: flag for console print enablement/disablement (default disabled)
        :type print_ctrl: bool
        :param single_use: singular usage - True or explore mode - False,
        returns dictionary of results to calling function (default disabled) - see returns.
        :type single_use: bool
        :returns: None, dictionary of all physical drives identified by 'Id'
        """

        confd = content.get("PhysicalDrives")
        try:
            dd = content["links"]["PhysicalDrives"][
                self.rdmc.app.typepath.defs.hrefstring
            ]
        except:
            dd = content["Links"]["PhysicalDrives"][
                self.rdmc.app.typepath.defs.hrefstring
            ]
        finally:
            if not getattr(options, "json", False) and print_ctrl:
                sys.stdout.write("Physical Drives:\n")
            if getattr(options, "pdrive", False):
                pdrive_ident = False
            else:
                pdrive_ident = True
            if single_use:
                physicaldrives = {}
            found_entries = False
            for data in self.rdmc.app.get_handler(dd, silent=True).dict.get(
                    "Members", {}
            ):
                try:
                    tmp = data[self.rdmc.app.typepath.defs.hrefstring]
                except:
                    tmp = data[next(iter(data))]
                finally:
                    tmp = self.rdmc.app.get_handler(tmp, silent=True).dict
                    found_entries = True
                if confd:
                    for confdd in confd:
                        if confdd.get("Location") == tmp.get("Location"):
                            tmp.update(confdd)
                            break
                if getattr(options, "pdrive", False):
                    if options.pdrive != tmp["Location"]:
                        continue
                    else:
                        pdrive_ident = True
                if single_use:
                    physicaldrives[tmp["Id"]] = tmp
                if print_ctrl and pdrive_ident and options.pdrive is None:
                    sys.stdout.write(
                        "\t[%s]: Model %s, Location %s, Type %s, Serial %s - %s MiB\n"
                        % (
                            tmp["Location"],
                            tmp["Model"],
                            tmp["Location"],
                            tmp["MediaType"],
                            tmp["SerialNumber"],
                            tmp["CapacityMiB"],
                        )
                    )
                    # self.tranverse_func(tmp)
                    # sys.stdout.write("\n")
                elif getattr(options, "json", False) and pdrive_ident and options.pdrive is None:
                    outjson = dict()
                    outjson["PhysicalDrives"] = dict()
                    outjson["PhysicalDrives"][tmp["Location"]] = dict()
                    outjson["PhysicalDrives"][tmp["Location"]]["Model"] = tmp["Model"]
                    outjson["PhysicalDrives"][tmp["Location"]]["Location"] = tmp[
                        "Location"
                    ]
                    outjson["PhysicalDrives"][tmp["Location"]]["MediaType"] = tmp[
                        "MediaType"
                    ]
                    outjson["PhysicalDrives"][tmp["Location"]]["SerialNumber"] = tmp[
                        "SerialNumber"
                    ]
                    outjson["PhysicalDrives"][tmp["Location"]]["CapacityMiB"] = tmp[
                        "CapacityMiB"
                    ]
                    UI().print_out_json(outjson)

                elif print_ctrl and pdrive_ident and options.pdrive is not None:
                    ctl_logical = dict()
                    contoller_loc = content["Location"] + '-' + content["Model"]
                    ctl_logical.update({"Controller": contoller_loc})
                    remove_odata = self.odataremovereadonly(tmp)
                    ctl_logical.update(remove_odata)
                    UI().print_out_json(ctl_logical)

                elif getattr(options, "json", False) and pdrive_ident and options.pdrive is not None:
                    ctl_logical = dict()
                    contoller_loc = content["Location"] + '-' + content["Model"]
                    ctl_logical.update({"Controller": contoller_loc})
                    remove_odata = self.odataremovereadonly(tmp)
                    ctl_logical.update(remove_odata)
                    UI().print_out_json(ctl_logical)

                if getattr(options, "pdrive", False) and pdrive_ident:
                    break
            if getattr(options, "pdrive", False) and not pdrive_ident and print_ctrl:
                sys.stdout.write(
                    "\tPhysical drive in position '%s' was not found" % options.pdrive
                )
            elif not found_entries and print_ctrl:
                sys.stdout.write("\tPhysical drives not found.\n")

            if single_use:
                return physicaldrives

    def logical_drives(self, options, content, print_ctrl=False, single_use=False):
        """
        Identify/parse volumes (and child properties) of an associated array controller

        :param options: command line options
        :type options: object attributes
        :param content: dictionary of volume href or @odata.id paths (expect @odata.type
        "SmartStorageArrayController", @odata.id /Systems/1/SmartStorage/ArrayControllers/X/)
        :type content: dict
        :param print_ctrl: flag for console print enablement/disablement (default disabled)
        :type print_ctrl: bool
        :param single_use: singular usage - True or explore mode - False,
        returns dictionary of results to calling function (default disabled) - see returns.
        :type single_use: bool
        :returns: None, dictionary of all volumes identified by 'Id'
        """

        confd = content.get("LogicalDrives")
        try:
            dd = content["links"]["LogicalDrives"][self.rdmc.app.typepath.defs.hrefstring]
        except:
            dd = content["Links"]["LogicalDrives"][self.rdmc.app.typepath.defs.hrefstring]
        finally:
            if not getattr(options, "json", False) and print_ctrl:
                sys.stdout.write("Logical Drives:\n")
            if getattr(options, "ldrive", False):
                ldrive_ident = False
            else:
                ldrive_ident = True
            if single_use:
                logicaldrives = {}
            found_entries = False
            for data in self.rdmc.app.get_handler(dd, silent=True).dict.get(
                    "Members", {}
            ):
                try:
                    tmp = data[self.rdmc.app.typepath.defs.hrefstring]
                except:
                    tmp = data[next(iter(data))]
                finally:
                    tmp = self.rdmc.app.get_handler(tmp, silent=True).dict
                    found_entries = True
                if confd:
                    for confdd in confd:
                        if confdd.get("LogicalDriveNumber") == tmp.get(
                                "LogicalDriveNumber"
                        ):
                            tmp.update(confdd)
                            break
                if getattr(options, "ldrive", False):
                    if options.ldrive != tmp["Id"]:
                        continue
                    else:
                        ldrive_ident = True
                if print_ctrl and ldrive_ident and options.ldrive is None:
                    sys.stdout.write(
                        "\t[%s]: Name %s Raid %s VUID %s - %s MiB\n"
                        % (
                            tmp["Id"],
                            tmp["LogicalDriveName"],
                            tmp["Raid"],
                            tmp["VolumeUniqueIdentifier"],
                            tmp["CapacityMiB"],
                        )
                    )
                elif getattr(options, "json", False) and ldrive_ident and options.ldrive is None:
                    outjson = dict()
                    outjson["LogicalDrives"] = dict()
                    outjson["LogicalDrives"][tmp["Id"]] = dict()
                    outjson["LogicalDrives"][tmp["Id"]]["LogicalDriveName"] = tmp[
                        "LogicalDriveName"
                    ]
                    outjson["LogicalDrives"][tmp["Id"]]["Raid"] = tmp["Raid"]
                    outjson["LogicalDrives"][tmp["Id"]]["VolumeUniqueIdentifier"] = tmp[
                        "VolumeUniqueIdentifier"
                    ]
                    outjson["LogicalDrives"][tmp["Id"]]["CapacityMiB"] = tmp[
                        "CapacityMiB"
                    ]
                    UI().print_out_json(outjson)
                    # self.tranverse_func(tmp)
                    # sys.stdout.write("\n")
                elif print_ctrl and ldrive_ident and options.ldrive is not None:
                    ctl_logical = dict()
                    contoller_loc = content["Location"] + '-' + content["Model"]
                    ctl_logical.update({"Controller": contoller_loc})
                    remove_odata = self.odataremovereadonly(tmp)
                    ctl_logical.update(remove_odata)
                    UI().print_out_json(ctl_logical)

                elif getattr(options, "json", False) and ldrive_ident and options.ldrive is not None:
                    ctl_logical = dict()
                    contoller_loc = content["Location"] + '-' + content["Model"]
                    ctl_logical.update({"Controller": contoller_loc})
                    remove_odata = self.odataremovereadonly(tmp)
                    ctl_logical.update(remove_odata)
                    UI().print_out_json(ctl_logical)

                elif getattr(options, "json", False) and ldrive_ident:
                    UI().print_out_json(tmp)
                """    
                try:
                    tmp2 = tmp["Links"]["DataDrives"][
                        self.rdmc.app.typepath.defs.hrefstring
                    ]
                except:
                    tmp2 = tmp["links"]["DataDrives"][
                        next(iter(tmp["links"]["DataDrives"]))
                    ]
                finally:
                    tmp2 = self.rdmc.app.get_handler(tmp2, silent=True).dict
                if ldrive_ident:
                    data_drives = self.get_data_drives(
                        options, tmp2, print_ctrl, single_use
                    )
                    try:
                        tmp["links"]["DataDrives"] = data_drives
                    except:
                        tmp["Links"]["DataDrives"] = data_drives
                """
                if single_use:
                    logicaldrives[tmp["Id"]] = tmp
                if getattr(options, "ldrive", False) and ldrive_ident:
                    break
            if getattr(options, "ldrive", False) and not ldrive_ident:
                sys.stdout.write(
                    "\tLogical drive in position '%s' was not found" % options.pdrive
                )
            elif not found_entries and print_ctrl:
                sys.stdout.write("\tLogical drives not found.\n")

            if single_use:
                return logicaldrives

    def get_data_drives(self, options, drives, print_ctrl=False, single_use=False):
        """
        Identify/parse a physical component drive collection of a respective volume. The
        physical disk properties as well as some logical RAID parameters within each respective
        member.

        :param options: command line options
        :type options: object attributes
        :param content: collection of data drives href or @odata.id paths (as members) as attributed
        to a respective volume.
        :type content: dict
        :param print_ctrl: flag for console print enablement/disablement (default disabled)
        :type print_ctrl: bool
        :param single_use: singular usage, returns dictionary of results to calling function
        (default disabled)
        :type single_use: bool
        :returns: None, dictionary of all physical drives composing a parent volume,
        each instance identified by 'Id'
        """

        if not (getattr(options, "json", False)) and print_ctrl:
            sys.stdout.write("\tData Drives:\n\n")
        if single_use:
            subsetdrives = {}
        found_entries = False
        for member in drives.get("Members", {}):
            try:
                tmp = member[self.rdmc.app.typepath.defs.hrefstring]
            except:
                tmp = member[next(iter(member))]
            finally:
                tmp = self.rdmc.app.get_handler(tmp, silent=True).dict
                found_entries = True
            if single_use:
                subsetdrives[tmp["Id"]] = tmp
            if print_ctrl:
                self.tranverse_func(tmp)
            elif getattr(options, "json", False):
                UI().print_out_json(tmp)
        if not found_entries and print_ctrl:
            sys.stdout.write("\t\tComponent drives not found.\n")

        if single_use:
            return subsetdrives

    def smartarrayvalidation(self, options):
        """Smart array validation function

        :param options: command line options
        :type options: list.
        """
        self.cmdbase.login_select_validation(self, options)

        if getattr(options, "sa_conf_filename", False):
            if options.command == "save":
                open(options.sa_conf_filename, "w+b")
            if options.command == "load":
                open(options.sa_conf_filename, "r+b")
            self.config_file = options.sa_conf_filename
        else:
            self.config_file = __config_file__

    def definearguments(self, customparser):
        """Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        self.cmdbase.add_login_arguments_group(customparser)
        subcommand_parser = customparser.add_subparsers(dest="command")

        default_parser = subcommand_parser.add_parser(
            "default",
            help="Running without any sub-command will return smart array configuration data\n"
                 "on the currently logged in server. Additional optional arguments will narrow the\n"
                 "scope of returned data to individual controllers, physical or volumes",
        )
        default_parser.add_argument(
            "--controller",
            dest="controller",
            help="Use this flag to select the corresponding controller using either the slot "
                 "number or index. \n\tExamples:\n\t1. To get more details on a specific "
                 "controller, select it by index.\tsmartarray --controller=2"
                 "\n\t2. To get more details on a specific controller select "
                 "it by location.\tsmartarray --controller='Slot 0'",
            default=None,
        )
        default_parser.add_argument(
            "--physicaldrives",
            dest="physicaldrives",
            action="store_true",
            help="Use this flag to return the physical drives for the controller selected."
                 "\n\tExamples:\n\t1. smartarray --physicaldrives\n\t2. To obtain details about "
                 "physical drives for a specific controller.\tsmartarray --controller=3 "
                 "--physicaldrives",
            default=None,
        )
        default_parser.add_argument(
            "--logicaldrives",
            dest="logicaldrives",
            action="store_true",
            help="Use this flag to return the volumes for the controller selected.\n\t "
                 "\n\tExamples:\n\t1. smartarray --logicaldrives\n\t2. To obtain details about "
                 "volumes for a specific controller.\tsmartarray --controller=3 "
                 "--logicaldrives",
            default=None,
        )
        default_parser.add_argument(
            "--pdrive",
            dest="pdrive",
            help="Use this flag to select the corresponding physical disk.\n\tExamples:\n\t "
                 "1. To obtain details about a specific physical drive for a specific controller."
                 "\tsmartarray --controller=3 --pdrive=1I:1:1",
            default=None,
        )
        default_parser.add_argument(
            "--ldrive",
            dest="ldrive",
            help="Use this flag to select the corresponding logical disk.\n\tExamples:\n\t "
                 "1. To obtain details about a specific physical drive for a specific controller."
                 "\tsmartarray --controller=3 --ldrive=1",
            default=None,
        )
        default_parser.add_argument(
            "-j",
            "--json",
            dest="json",
            action="store_true",
            help="""Use this flag to output data in JSON format.""",
            default=None,
        )
        self.cmdbase.add_login_arguments_group(default_parser)

        state_help = "Print state/event information from @Redfish.Settings (if available)"
        state_parser = subcommand_parser.add_parser(
            "state",
            help=state_help,
            description=state_help + "\n\tExample: smartarray state",
            formatter_class=RawDescriptionHelpFormatter,
        )
        state_parser.add_argument(
            "--controller",
            dest="controller",
            help="Use this flag to select the corresponding controller using either the slot "
                 "number or index. \n\tExamples:\n\t1. To get more details on a specific "
                 "controller, select it by index.\tsmartarray state --controller=2"
                 "\n\t2. To get more details on a specific controller select "
                 "it by location.\tsmartarray state --controller='Slot 0'",
            default=None,
        )
        self.cmdbase.add_login_arguments_group(state_parser)
        json_save_help = "Save a JSON file with all current configurations (all controllers, logical and \nphysical drives)."
        # json save sub-parser
        json_save_parser = subcommand_parser.add_parser(
            "save",
            help=json_save_help,
            description=json_save_help + "\n\tExample: smartarray save -f <filename>",
            formatter_class=RawDescriptionHelpFormatter,
        )
        json_save_parser.add_argument(
            "-f",
            dest="sa_conf_filename",
            help="Specify a filename for saving the smartarray configuration. (Default: "
                 "'smartarray_config.json')",
            default=None,
        )
        self.cmdbase.add_login_arguments_group(json_save_parser)
        json_load_help = (
            "Load a JSON file with modified smartarray configurations (All read-only "
            "properties\nare discarded)."
        )
        # json load sub-parser
        json_load_parser = subcommand_parser.add_parser(
            "load",
            help=json_load_help,
            description=json_load_help + "\n\tExample: smartarray load -f <filename>",
            formatter_class=RawDescriptionHelpFormatter,
        )
        json_load_parser.add_argument(
            "-f",
            dest="sa_conf_filename",
            help="Specify a filename for loading a smartarray configuration. (Default: "
                 "'smartarray_config.json')",
            default=None,
        )
        self.cmdbase.add_login_arguments_group(json_load_parser)
