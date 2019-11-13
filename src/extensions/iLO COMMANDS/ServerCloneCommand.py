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
""" Server Clone Command for rdmc """

import re
import os
import os.path
import sys
import copy
import json
import time
import getpass
import traceback

from collections import OrderedDict
from argparse import ArgumentParser

import jsonpath_rw
import redfish.ris

from redfish.ris.utils import iterateandclear, diffdict
from redfish.ris.rmc_helper import (IloResponseError, IdTokenError, InstanceNotFoundError)

from six.moves import input
from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group

from rdmc_helper import ReturnCodes, InvalidCommandLineError, InvalidKeyError, Encryption, \
            InvalidCommandLineErrorOPTS, InvalidFileInputError, NoChangesFoundOrMadeError, \
            NoContentsFoundForOperationError, ResourceExists, NoDifferencesFoundError

#default file name
__DEFAULT__ = "<p/k>"
__MINENCRYPTIONLEN__ = 16
__clone_file__ = 'ilorest_clone.json'
__tmp_clone_file__ = '_ilorest_clone_tmp'
__tmp_sel_file__ = '_ilorest_sel_tmp'
__error_log_file__ = 'clone_error_logfile.log'
__changelog_file__ = 'changelog.log'
__tempfoldername__ = "serverclone_data"

def log_decor(func):
    """
    Log Decorator function
    :param func: function to be decorated
    :type func: class method

    """
    def func_wrap(*args, **kwargs):
        """
        Log Decorator function wrapper
    :   :param args: function to be decorated
    :   :type args: *
        :param kwargs: keyword arguments
        :type kwargs: *

        """
        try:
            return func(*args, **kwargs)
        except IdTokenError as excp:
            sys.stderr.write("You have logged into iLO with an account which has insufficient "\
                             " user access privileges to modify properties in this type:\n %s\n" % \
                             (excp))
        except NoDifferencesFoundError:
            sys.stdout.write("No differences identified from current configuration.\n")
        except Exception as excp:
            if not args[0]._rdmc.opts.debug:
                sys.stderr.write("An error occurred: %s. Check the ServerClone Error logfile "\
                                 "for further info: %s\n" % (excp, __error_log_file__))
                logging(func.func_name, traceback.format_exc(), excp, args)

    return func_wrap

def logging(command, _trace, error, _args):
    """
    Handler for error logging
    :param command: command in error
    :type command: method identifier
    :param _trace: traceback data
    :type _trace: object
    :param error: error logged (simplified version)
    :type error: string
    :param _agrs: array of methods arguments
    :type _args: array
    """

    sys.stderr.write("Logging error to \'%s\'.\n" % __error_log_file__)
    with open(__error_log_file__, 'a+') as efh:
        efh.write(command + ":\n")
        efh.write("Simplified Error: " + str(error) + '\n')
        efh.write("Traceback:\n")
        efh.write(str(_trace)+'\n')
        efh.write("Args State in: \'%s\'.\n" % command)
        i = 0
        for _arg in _args:
            efh.write("Arg %s: %s\n" % (str(i), _arg))
            i += 1
        efh.write('\n')

class ServerCloneCommand(RdmcCommandBase):
    """ Constructor """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='serverclone',\
            usage='serverclone [save/load] [OPTIONS]\n\n\tCreate a JSON formatted clone file'\
            ' of a system\'s iLO and Bios configuration.\n\tSSA configuration can also optionally '\
            'be added.\n\tBy default the JSON file will be named "ilorest_clone.json".\n\t'\
            'SSO and TLS certificates may be added on load.'\
            '\n\n\tSave of an iLO and Bios config.\n\texample: serverclone save'\
            '\n\n\tSave iLO config omitting BIOS attributes to a non-default file name.\n\t'\
            'example: serverclone save -f serv_clone.json --nobios' \
            '\n\n\tSave an encrypted iLO configuration file (to the default file name)\n\t' \
            'example: serverclone save --encryption <ENCRYPTION KEY>'\
            '\n\n\tLoad a clone file from a non-default file name.\n\t'\
            'example: serverclone load -f serv_clone.json'\
            '\n\n\tLoad a clone file with SSO and TLS certificates.\n\t'\
            'example: serverclone load -ssocert sso.txt --tlscert tls.txt'\
            '\n\n\tLoad a clone file which has been encrypted.\n\t'\
            'example: serverclone load --encryption abc12abc12abc123\n\n\t'\
            'NOTE 1: Use the \'--silent\' OR \'--quiet\'option to ignore \n\t        '\
            'all user input. Intended for scripting purposes.\n\n\t' \
            'NOTE 2: During clone load, login using an ilo account with\n\t        full privileges'\
            ' (such as the Administrator account)\n\t        to ensure all items are cloned '\
            'successfully.',\
            summary="Creates a JSON formatted clone file of a system's iLO, Bios, and SSA "\
            "configuration which can be duplicated onto other systems. "\
            "User editable JSON file can be manipulated to modify settings before being "\
            "loaded onto another machine.", \
            aliases=None,\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.clone_file = None #set in validation
        self._cache_dir = None #set in validation
        self.tmp_clone_file = __tmp_clone_file__
        self.tmp_sel_file = __tmp_sel_file__
        self.change_log_file = __changelog_file__
        self.error_log_file = __error_log_file__
        self.https_cert_file = None
        self.sso_cert_file = None
        self.save = None
        self.load = None
        self._fdata = None

        self.loginobj = rdmcObj.commands_dict["LoginCommand"](rdmcObj)
        self.logoutobj = rdmcObj.commands_dict["LogoutCommand"](rdmcObj)
        self.loadobj = rdmcObj.commands_dict["LoadCommand"](rdmcObj)

        #referenced for special POST commands
        self.makedriveobj = rdmcObj.commands_dict["CreateLogicalDriveCommand"](rdmcObj)

        #referenced for accounts management processes
        self.iloacctsobj = rdmcObj.commands_dict["IloAccountsCommand"](rdmcObj)
        self.ilofedobj = rdmcObj.commands_dict["IloFederationCommand"](rdmcObj)
        self.ilolicobj = rdmcObj.commands_dict["IloLicenseCommand"](rdmcObj)
        self.ilocertobj = rdmcObj.commands_dict["CertificateCommand"](rdmcObj)
        self.ssoobj = rdmcObj.commands_dict["SingleSignOnCommand"](rdmcObj)

        #reset/reboot commands
        self.iloresetobj = rdmcObj.commands_dict["IloResetCommand"](rdmcObj)
        self.ilorebootobj = rdmcObj.commands_dict["RebootCommand"](rdmcObj)

    def cleanup(self):
        self.save = None
        self.load = None
        self._fdata = None

    def run(self, line):
        """ Main Serverclone Command function
        :param line: string of arguments passed in
        :type line: str.
        """
        _valid_args = ['save', 'load']
        try:
            (options, args) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        if not len(args) > 1:
            for arg in args:
                arg = arg.lower()
        else:
            raise InvalidCommandLineError("Too many arguments included. The following arguments "\
                                          "were observed: %s." % args)
        if 'save' in args:
            self.save = True
            self.load = False
        elif 'load' in args:
            self.save = False
            self.load = True
        else:
            raise InvalidCommandLineError("Save or load was not selected.")

        self.serverclonevalidation(options)
        self.check_files(options)

        if self.save:
            self.gatherandsavefunction(self.getilotypes(options), options)
            sys.stdout.write('Saving of clonefile to \'%s\' is complete.\n' % self.clone_file)
        elif self.load:
            self.loadfunction(options)
            sys.stdout.write("Loading of clonefile \'%s\' to server is complete. Review the "\
                             "changelog file \'%s\'.\n" % (self.clone_file, self.change_log_file))
        self.cleanup()
        return ReturnCodes.SUCCESS

    @log_decor
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
        writeable_ops = ['w', 'w+', 'a', 'a+']
        readable_ops = ['r', 'r+']
        fdata = None

        if operation in writeable_ops:
            try:
                if options.encryption:
                    with open(filename, operation + 'b') as outfile:
                        outfile.write(Encryption().encrypt_file(json.dumps(data, indent=2, \
                                    cls=redfish.ris.JSONEncoder, sort_keys=sk), options.encryption))
                else:
                    with open(filename, operation) as outfile:
                        outfile.write(json.dumps(data, indent=2, cls=redfish.ris.JSONEncoder, \
                                                                                    sort_keys=sk))
            except FileNotFoundError as excp:
                self.cleanup()
                raise InvalidFileInputError("Unable to open file: %s" % excp)
        else:
            try:
                if options.encryption:
                    with open(filename, operation + 'b') as file_handle:
                        fdata = json.loads(Encryption().decrypt_file(file_handle.read(),\
                                                                options.encryption))
                else:
                    with open(filename, operation) as file_handle:
                        fdata = json.loads(file_handle.read())
            except:
                raise InvalidFileInputError("Invalid file formatting found. Verify the file has a "\
                                        "valid JSON format.")
        return fdata

    @log_decor
    def getilotypes(self, options):
        """
        Get iLO types from server and return a list of types

        :parm options: command line options
        :type options: attribute
        :returns: returns list of types
        """

        supported_types_list = ['ManagerAccount', 'AccountService', 'Bios', \
                                'Manager', 'SmartStorageConfig', 'SNMP', 'iLOLicense', \
                                'EthernetNetworkInterface', 'iLODateTime', \
                                'iLOFederationGroup', 'iLOSSO', 'ESKM', 'ComputerSystem', \
                                'EthernetInterface', 'ServerBootSettings', 'SecureBoot', \
                                'ManagerNetworkService', 'SmartStorageConfig']

        if options.noBIOS:
            sys.stdout.write("Bios configuration will be excluded from save operation.\n")
            supported_types_list.remove('Bios')
        if options.iLOSSA:
            sys.stdout.write("Smart storage configuration will be included in save operation.\n")
        else:
            supported_types_list.remove('SmartStorageConfig')

        unsupported_types_list = ['Collection', 'PowerMeter', 'BiosMapping']

        #supported types comparison
        types_accepted = set()
        for _type in sorted(set(self._rdmc.app.types('--fulltypes'))):
            if _type[:1].split('.')[0] == '#':
                _type_mod = _type[1:].split('.')[0]
            else:
                _type_mod = _type.split('.')[0]
            for stype in supported_types_list:
                if stype.lower() in _type_mod.lower():
                    found = False
                    for ustype in unsupported_types_list:
                        if ustype.lower() in _type_mod.lower():
                            found = True
                            break
                    if not found:
                        types_accepted.add(_type)

        return sorted(types_accepted)

    def loadfunction(self, options):
        """
        Main load function. Handles SSO and SSL/TLS Certificates, kickoff load
        helper, load of patch file, get server status and issues system reboot
        and iLO reset after completion of all post and patch commands.

        :param options: command line options
        :type options: attribute
        """

        reset_confirm = True

        if not options.silentcopy:
            while True:
                ans = input("A configuration file \'%s\' containing " \
                            "configuration changes will be applied to this iLO"\
                            " server resulting in system setting changes for"\
                            " BIOS, ethernet controllers, disk controllers, "\
                            "deletion and rearrangement of logical disks..."\
                            "etc. Please confirm you acknowledge and would "\
                            "like to perform this operation now? (y/n)\n" %
                            self.clone_file)
                if ans.lower() == 'y':
                    sys.stdout.write("Proceeding with ServerClone Load "\
                                     "Operation...\n")
                    break
                elif ans.lower() == 'n':
                    sys.stdout.write("Aborting load operation. No changes "\
                                     "made to the server.\n")
                    return ReturnCodes.SUCCESS
                else:
                    sys.stdout.write("Invalid input...\n")

        self._fdata = self.file_handler(self.clone_file, operation='r+', options=options)
        self.loadhelper(options)
        self.loadpatch(options)
        self.getsystemstatus()

        if not options.silentcopy:
            while True:
                ans = input("The system is ready to be reset. Perform a reset"\
                            " now? (y/n)\n")
                if ans.lower() == 'n':
                    reset_confirm = False
                    break
                elif ans.lower() == 'y':
                    break
                else:
                    sys.stdout.write("Invalid input...\n")

        if reset_confirm:
            if self._rdmc.app.config.get_url: #reset process in remote mode
                sys.stdout.write("Resetting System...\n")
                self.ilorebootobj.run("ForceRestart")
                sys.stdout.write("Resetting iLO...\n")
                self.iloresetobj.run("")
                sys.stdout.write("You will need to re-login to access this system...\n")
            else: #reset process in local mode
                sys.stdout.write("Resetting local iLO...\n")
                self.iloresetobj.run("")
                sys.stdout.write("Sleeping 120 seconds for iLO reset...\n")
                time.sleep(120)
                self.loginobj.run("")
                sys.stdout.write("Resetting System...\n")
                self.ilorebootobj.run("ForceRestart")
        else:
            sys.stdout.write("Aborting Server Reboot and iLO reset...\n")
            sys.stdout.write("TestMode...%s\n" % options.testmode)
            sys.stdout.write("Reset...%s\n" % reset_confirm)

    def loadhelper(self, options):
        """
        Helper function for loading which calls additional helper functions for
        Server BIOS and Firmware compatibility, type compatibility, patch or
        postability (special functions). Data deemed for exclusive patching
        (through load) is written into a temporary file, which is deleted unless
        archived for later use.

        :param options: command line options
        :type options: attribute

        """
        data = list()

        server_avail_types = self.getilotypes(options)
        if not server_avail_types:
            raise NoContentsFoundForOperationError("Unable to Obtain iLO Types from server.")

        if 'Comments' in self._fdata.keys():
            self.system_compatibility_check(self._fdata['Comments'], options)
            del self._fdata['Comments']
        else:
            raise InvalidFileInputError("Clone File \'%s\' does not include a valid \'Comments\' "\
                                        "dictionary.")

        if options.ssocert:
            self.load_ssocertificate()  #check and load sso certificates
        if options.tlscert:
            self.load_tlscertificate()  #check and load tls certificates

        typelist = []
        for _x in self._fdata:
            for _y in server_avail_types:
                _x1 = re.split('#|\.', _x)
                _y1 = re.split('#|\.', _y)
                if _x1[0] == '':
                    _x1.pop(0)
                if _y1[0] == '':
                    _y1.pop(0)
                if _x1[0] == _y1[0]: # _x.split('.')[0] == _y.split('.')[0]:
                    _comp_tuple = self.type_compare(_x, _y)
                    if (_comp_tuple[0] and _comp_tuple[1]):
                        sys.stdout.write("Type \'%s\' is compatible with this system.\n" % _x)
                        typelist.append(_x)
                    else:
                        sys.stdout.write("The type: \'%s\' isn't compatible with the type: \'%s\'"\
                                         "found on this system. Associated properties can not "\
                                         "be applied...Skipping\n" % (_x, _y))

        for _type in typelist:
            singlet = True
            thispath = next(iter(self._fdata[_type].keys()))
            try:
                root_path_comps = self.get_rootpath(thispath)

                multi_sel = self._rdmc.app.select(_type.split('.')[0] + '.', \
                        (self.typepath.defs.hrefstring, root_path_comps[0] + '*'), rel=True)

                curr_sel = self._rdmc.app.select(_type.split('.')[0] + '.', \
                                (self.typepath.defs.hrefstring, thispath), rel=True)

            except InstanceNotFoundError:
                curr_sel = self._rdmc.app.select(_type.split('.')[0] + '.')

            except Exception as excp:
                sys.stdout.write("Unable to find the correct path based on system "\
                                 "type and clone file type \'%s\': %s\n" % (excp, _type))
                continue

            finally:
                try:
                    if 'multi_sel' in locals() and 'curr_sel' in locals():
                        if len(multi_sel) > 1 and len(curr_sel) == 1 and (root_path_comps[1].\
                                                    isdigit() or 'iLOFederationGroup' in _type):
                            singlet = False
                            curr_sel = multi_sel
                except (ValueError, KeyError):
                    pass

            scanned_dict = dict()
            for thing in curr_sel:
                scanned_dict[thing.path] = {'Origin': 'Server', 'Scanned': False, \
                                            'Data': thing.dict}
            for thing in self._fdata[_type]:
                # if we only have a single path, the base path is in the path and only a single
                #instance was retrieved from the server
                if singlet and root_path_comps[0] in thing and len(scanned_dict) is 1:
                    scanned_dict[next(iter(scanned_dict))] = {'Origin': 'File', 'Scanned': False, \
                                                              'Data': self._fdata[_type][thing]}
                else:
                    scanned_dict[thing] = {'Origin': 'File', 'Scanned': False, \
                                           'Data': self._fdata[_type][thing]}

            for path in scanned_dict.keys():
                try:
                    if scanned_dict[path]['Origin'] is 'Server':
                        raise KeyError(path)
                    else:
                        tmp = self.subhelper(scanned_dict[path]['Data'], _type, path, options)
                        if tmp:
                            data.append(tmp)

                except KeyError as excp:
                    if path in str(excp) and self._fdata.get(_type):
                        if self.delete(scanned_dict[path]['Data'], _type, path, \
                                       self._fdata[_type], options):
                            #ok so this thing does not have a valid path, is not considered a
                            #deletable item so....idk what to do with you. You go to load.
                            #Goodluck
                            tmp = self.altsubhelper(scanned_dict[path]['Data'], _type, path)
                            if tmp:
                                data.append(tmp)
                    else:
                        # if the instance item was not replaced with an entry in the clone file then
                        # it will be deleted
                        sys.stdout.write("Entry at \'%s\' removed from this server.\n" % path)

                except Exception as excp:
                    sys.stdout.write("An error occurred: \'%s\'" % excp)
                    continue
                finally:
                    scanned_dict[path]['Scanned'] = True

        self.file_handler(self.tmp_clone_file, 'w+', options, data, True)

    def subhelper(self, data, _type, path, options):
        """
        Reusable code section for load helper
        :param data: dict data (from file or server)
        :type: dictionary
        :param _type: cross compatible iLO type
        :type: string
        :param path: iLO schema path determined from system query
        :type: string
        :param prev
        :parm options: command line options
        :type options: attribute
        """

        #due to EthernetInterfaces OEM/HPE/DHCPv4 also having a key with 'Name'
        #this is required, removing readonly types after POST commands have
        #completed. Would be great if that was resolved...
        prop_list = ["Modified", "Type", "Description", "Status", "Name",\
                    "AttributeRegistry", "links", "SettingsResult", \
                    "@odata.context", "@odata.type", "@odata.id",\
                    "@odata.etag", "Links", "Actions", \
                    "AvailableActions", "MACAddress", "BiosVersion"]

        tmp = dict()
        tmp[_type] = {path: data}
        tmp[_type][path] = self._rdmc.app.removereadonlyprops(tmp[_type][path], False, True, \
                                                                                    prop_list)
        self.json_traversal_delete_empty(tmp, None, None)
        if not self.ilo_special_functions(tmp, _type, path, options):
            return tmp

    @log_decor
    def altsubhelper(self, file_data, _type, curr_path):
        """
        Just for manipulating the file_data in the clone file and handing it off to load.
        :param file_data: clone file data
        :type: dictionary
        :param _type: cross compatible iLO type
        :type: string
        :param curr_path: iLO schema path determined from system query
        :type: string
        :param file_path: iLO schema path as observed in the clone file
        :type: string
        :returns: a dictionary containing the data which will be passed off to load.
        """

        tmp = dict()
        try:
            tmp[_type] = {curr_path : file_data[_type][next(iter(file_data[_type]))]}
        except KeyError:
            tmp[_type] = {curr_path : file_data}
        self.json_traversal_delete_empty(tmp, None, None)
        return tmp

    def loadpatch(self, options):
        """
        Load temporary patch file to server

        :parm options: command line options
        :type options: attribute
        """
        sys.stdout.write("Patching remaining data.\n")
        fdata = self.file_handler(self.tmp_clone_file, operation='r+', options=options)
        for _sect in fdata:
            _tmp_sel = {}
            _key = (next(iter(_sect)))
            _tmp_sel[_key.split('.')[0] + '.'] = _sect[_key]
            self.file_handler(self.tmp_sel_file, 'w+', options, [_tmp_sel], True)
            self.loadpatch_helper(_key, _sect, options)

    @log_decor
    def loadpatch_helper(self, type, dict, options):
        """
        Load temporary patch file to server

        :parm options: command line options
        :type options: attribute
        """
        options_str = ""
        if options.encryption:
            options_str += " --encryption " + options.encryption

        if options.uniqueoverride:
            options_str += " --uniqueitemoverride"

        sys.stdout.write("Patching \'%s\'.\n" % type)
        self.loadobj.run("-f " + self.tmp_sel_file + options_str)

    def gatherandsavefunction(self, typelist, options):
        """
        Write parsed JSON save data to file

        :param typelist: list of available types on iLO
        :type typelist: list
        :param options: command line options
        :type options: attribute
        """
        data = OrderedDict()
        data.update(self._rdmc.app.create_save_header(selectignore=True))

        for _type in typelist:
            self.gatherandsavehelper(_type, data, options)

        self.file_handler(self.clone_file, 'w+', options, data, False)

    def gatherandsavehelper(self, _type, data, options):
        """
        Collect data on types and parse properties (delete unnecessary/readonly/
        empty properties.

        :param type: type for subsequent select and save
        :type type: string
        :param data: JSON data (to be written to file)
        :type data: JSON
        :param options: command line options
        :type options: attribute
        """
        _typep = _type.split('.')[0]
        _spec_list = ['SmartStorageConfig', 'iLOLicense', 'Bios']

        try:
            if 'EthernetInterface' in _type:
                instances = self._rdmc.app.select(_typep + '.', \
                            (self.typepath.defs.hrefstring, self.typepath.defs.managerpath + '*'), \
                                                                                        rel=True)
            #'links/self/href' required when using iLO 4 (rest).
            elif 'EthernetNetworkInterface' in _type:
                instances = self._rdmc.app.select(_typep + '.', ("links/self/" + \
                            self.typepath.defs.hrefstring, self.typepath.defs.managerpath + '*'), \
                                                                                        rel=True)
            else:
                instances = self._rdmc.app.select(_typep + '.', rel=True)

            for j, instance in enumerate(self._rdmc.app.getprops(insts=instances)):
                if '#' in _typep:
                    _typep = _typep.split('#')[1]
                if self.typepath.defs.flagforrest:
                    try:
                        path = instance['links']['self'][self.typepath.defs.hrefstring]
                    except:
                        path = instance['links'][next(iter(instance['links']))]\
                                                                    [self.typepath.defs.hrefstring]
                else:
                    path = instance[self.typepath.defs.hrefstring]

                instance = self.ilo_special_functions(instance, _type, path, options)

                _itc_pass = True
                for _itm in _spec_list:
                    if _itm.lower() in _type.lower():
                        templist = ["Modified", "Type", "Description", "Status", "links", \
                                    "SettingsResult", "@odata.context", "@odata.type", "@odata.id",\
                                    "@odata.etag", "Links", "Actions", \
                                    "AvailableActions", "BiosVersion"]
                        instance = iterateandclear(instance, templist)
                        _itc_pass = False
                        break
                if _itc_pass:
                    instance = self._rdmc.app.removereadonlyprops(instance, False, True)

                if instance:
                    sys.stdout.write("Saving properties of type: %s, path: %s\n" % (_typep, path))
                    if _type not in data:
                        data[_type] = OrderedDict(sorted({path: instance}.items()))
                    else:
                        data[_type][path] = instance

        except Exception as excp:
            sys.stdout.write("An error occurred saving type: %s\nError: \"%s\"\n" % (_typep, excp))

    @log_decor
    def getsystemstatus(self):
        """
        Retrieve system status information and save to a changelog file. This
        file will be added to an archive if the archive selection is made.

        :parm options: command line options
        :type options: attribute
        """
        status_list = []

        for item in self._rdmc.app.status():
            status_list.append(item)

        if status_list:
            self.file_handler(self.change_log_file, 'w+', options, status_list, True)
        else:
            sys.stdout.write("No changes pending.\n")

    def ilo_special_functions(self, data, _type, path, options):
        '''
        Function used by both load and save for Restful commands requing a
        POST or PUT.

        :param data: JSON payload for saved or loaded properties
        :type data: json
        :param _type: selected type
        :type _type: string
        :param path: path of the selected type
        :type path: string
        :parm options: command line options
        :type options: attribute
        :returns: returns boolean indicating if the type/path was found.
        '''
        identified = False

        if 'EthernetInterfaces' in path:
            identified = True
            #save function not needed
            if self.load:
                self.load_ethernet(data[_type][path], _type, path)

        elif 'DateTime' in path:
            #do not use identified=True. Kind of a hack to have additional items patched.
            #save function not needed
            if self.load:
                self.load_datetime(data[_type][path], path)

        elif 'LicenseService' in path:
            identified = True
            if self.save:
                data = self.save_license(data, _type, options)
            elif self.load:
                self.load_license(data[_type][path])

        elif 'AccountService/Accounts' in path and 'AccountService' not in  _type.split('.')[0]:
            identified = True
            if self.save:
                data = self.save_accounts(data, _type, options)
            elif self.load:
                self.load_accounts(data[_type][path], _type, path)

        elif 'FederationGroups' in path:
            identified = True
            if self.save:
                data = self.save_federation(data, _type, options)
            elif self.load:
                self.load_federation(data[_type][path])

        elif 'smartstorageconfig' in path:
            #do not use identified=True. Kind of a hack to have the settings patched.
            if self.save:
                data = self.save_smartstorage(data, _type)
            elif self.load:
                self.load_smartstorage(data[_type][path], _type, path)

        if self.save:
            return data

        return identified

    @log_decor
    def delete(self, data, _type, path, fdata, options):
        """
        Delete operations to remove things on server

        :param data: Data to be deleted from the server
        :type data: dictionary
        :parm _type: iLO type to be queried
        :type _type: string
        :param path: iLO schema path
        :type path: string
        :returns: boolean indicating if the delete option occurred.
        """

        if not options.silentcopy:
            while True:
                ans = input("Are you sure you would like to delete the entry:\n %s" %
                            json.dumps(data.dict, indent=1, sort_keys=True))
                if ans.lower() == 'y':
                    sys.stdout.write("Proceeding with Deletion...\n")
                    break
                elif ans.lower() == 'n':
                    sys.stdout.write("Aborting deletion. No changes have been made made to the " \
                                     "server.\n")
                    return True
                else:
                    sys.stdout.write("Invalid input...\n")

        if 'ManagerAccount' in _type:
            user_name = data['UserName']

            #obtaining account information on the current server as a check to verify the user
            #provided a decent path to use. This can be re-factored.
            try:
                for curr_sel in self._rdmc.app.select(_type.split('.')[0] + '.'):
                    try:
                        if 'UserName' in curr_sel.dict.keys():
                            curr_un = curr_sel.dict['UserName']
                        if curr_un != user_name:
                            #check file to make sure this is not to be added later?
                            for fpath in fdata:
                                try:
                                    if fdata[fpath]['UserName'] == data['UserName']:
                                        sys.stdout.write("Account \'%s\' exists in \'%s\', not "
                                                         "deleting.\n" % (data['UserName'], \
                                                                                self.clone_file))
                                        return False
                                except:
                                    continue
                        else:
                            if data['UserName'] != "Administrator":
                                sys.stdout.write("Manager Account, \'%s\' was not found in the "\
                                                 "clone file. Deleting entry from server.\n"\
                                                  % data['UserName'])
                                self.iloacctsobj.run("delete "+ data['UserName'])
                            else:
                                sys.stdout.write("Deletion of the System Administrator Account "\
                                                 "is not allowed.\n")
                    except (KeyError, NameError):
                        sys.stderr.write("Unable to obtain the account information for: \'%s\'\'s'"\
                                         "account.\n" % user_name)
                        continue
            except InstanceNotFoundError:
                return True
            return False

        if 'FederationGroup' in _type:
            fed_identifier = None
            if 'FederationName' in data:
                fed_identifier = 'FederationName'
            elif 'Name' in data:
                fed_identifier = 'Name'
            else:
                raise InvalidKeyError("An invalid key was provided for the Federation Group Name.")
            if data[fed_identifier] != "DEFAULT":
                sys.stdout.write("Federation Account, \'%s\' was not found in the clone file." \
                                 " Deleting entry from server.\n" % data[fed_identifier])
                for fpath in fdata:
                    if fdata[next(iter(fdata))].get('FederationName') == data[fed_identifier]:
                        sys.stdout.write("Account \'%s\' exists in file, not deleting."
                                         "\n" % data[fed_identifier])
                        return False
                self.ilofedobj.run("delete "+ data[fed_identifier])
            else:
                sys.stdout.write("Deletion of the Default iLO Federation Group is not "\
                                 "allowed.\n")
            return False
        return True

    @log_decor
    def load_ssocertificate(self):
        """
        Load the SSO Certificate specified in the user defined options.
        """
        sys.stdout.write("Uploading SSO Certificate...\n")
        self.ssoobj.run("importcert "+ self.sso_cert_file)

    @log_decor
    def load_tlscertificate(self):
        """
        Load the SSO Certificate specified in the user defined options.
        """
        sys.stdout.write("Uploading TLS Certificate...\n")
        self.ilocertobj.run("tls "+ self.https_cert_file)

    @log_decor
    def load_ethernet(self, ethernet_data, _type, path):
        """
        Load iLO Ethernet Adapters settings Payload.

        :parm datetime_data: iLO Ethernet Adapters payload to be loaded
        :type datetime_data: dict
        :param _type: iLO schema type
        :type _type: string
        :param path: iLO schema path
        :type path: string

        """
        support_ipv6 = True
        dhcpv4curr = dhcpv4conf = None
        dhcpv6curr = dhcpv6conf = None
        oem_dhcpv4curr = oem_dhcpv4conf = None
        oem_dhcpv6curr = oem_dhcpv6conf = None
        errors = []

        self.json_traversal_delete_empty(ethernet_data, None, None)

        if 'EthernetInterface' in _type:
            for curr_sel in self._rdmc.app.select(_type.split('.')[0] + '.', \
                        (self.typepath.defs.hrefstring, self.typepath.defs.managerpath + '*')):
                if curr_sel.path == path:
                    break
            #'links/self/href' required when using iLO 4 (rest).
        elif 'EthernetNetworkInterface' in _type:
            for curr_sel in self._rdmc.app.select(_type.split('.')[0] + '.', ("links/self/" + \
                    self.typepath.defs.hrefstring, self.typepath.defs.managerpath + '*'), rel=True):
                if curr_sel.path == path:
                    break
        else:
            raise Exception("Invalid Type in Ethernet Loading Operation: \'%s\'" % _type)

        #ENABLING ETHERNET INTEFACE SECTION
        #---------------
        try:
            #Enable the Interface if called for and not already enabled
            if ethernet_data['InterfaceEnabled'] and not curr_sel.dict\
                                                        ['InterfaceEnabled']:
                self._rdmc.app.patch_handler(path, {"InterfaceEnabled": True})
                sys.stdout.write("NIC Interface Enabled.\n")
            #Disable the Interface if called for and not disabled already
            #No need to do anything else, just return
            elif not ethernet_data['InterfaceEnabled'] and not curr_sel.dict\
                                                        ['InterfaceEnabled']:
                self._rdmc.app.patch_handler(path, {"InterfaceEnabled": False})
                sys.stdout.write("NIC Interface Disabled.\n")
                return
        except (KeyError, NameError, TypeError, AttributeError):
            #check OEM for NICEnabled instead
            if not curr_sel.dict['Oem'][self.typepath.defs.oemhp]['NICEnabled'] and \
                                    ethernet_data['Oem'][self.typepath.defs.oemhp]['NICEnabled']:
                self._rdmc.app.patch_handler(path, {"Oem": {self.typepath.defs.oemhp: \
                                                                            {"NICEnabled": True}}})
                sys.stdout.write("NIC Interface Enabled.\n")
            elif not curr_sel.dict['Oem'][self.typepath.defs.oemhp]['NICEnabled'] and not\
                         ethernet_data['Oem'][self.typepath.defs.oemhp]['NICEnabled']:
                self._rdmc.app.patch_handler(path, {"Oem": { \
                            self.typepath.defs.oemhp: {"NICEnabled": False}}})
                sys.stdout.write("NIC Interface Disabled.\n")
                return
        #except IloResponseError should just be raised and captured by decorator. No point in
        #performing any other operations if the interface can not be set.

        #END ENABLING ETHERNET INTEFACE SECTION
        #---------------
        #---------------
        #---------------
        #DETERMINE DHCPv4 and DHCPv6 States and associated flags

        if 'NICSupportsIPv6' in curr_sel.dict['Oem'][self.typepath.defs.oemhp].keys():
            support_ipv6 = curr_sel.dict['Oem'][self.typepath.defs.oemhp]['NICSupportsIPv6']

        #obtain DHCPv4 Config and OEM
        try:
            if 'DHCPv4' in curr_sel.dict.keys() and 'DHCPv4' in ethernet_data.keys():
                dhcpv4curr = copy.deepcopy(curr_sel.dict['DHCPv4'])
                dhcpv4conf = copy.deepcopy(ethernet_data['DHCPv4'])
        except (KeyError, NameError, TypeError, AttributeError):
            sys.stdout.write("Unable to find Redfish DHCPv4 Settings.\n")
        finally:
            try:
                oem_dhcpv4curr = copy.deepcopy(curr_sel.dict['Oem'][self.typepath.defs.oemhp]\
                                                                                    ['DHCPv4'])
                oem_dhcpv4conf = copy.deepcopy(ethernet_data['Oem'][self.typepath.defs.oemhp]\
                                                                                    ['DHCPv4'])
                ipv4curr = copy.deepcopy(curr_sel.dict['Oem'][self.typepath.defs.oemhp]['IPv4'])
                ipv4conf = copy.deepcopy(ethernet_data['Oem'][self.typepath.defs.oemhp]['IPv4'])
            except (KeyError, NameError):
                raise InvalidKeyError("Unable to find OEM Keys for DHCPv4 or IPv4")

        try:
            if support_ipv6:
                if 'DHCPv6' in curr_sel.dict.keys() and 'DHCPv6' in ethernet_data.keys():
                    dhcpv6curr = copy.deepcopy(curr_sel.dict['DHCPv6'])
                    dhcpv6conf = copy.deepcopy(ethernet_data['DHCPv6'])
            else:
                sys.stdout.write("NIC Does not support IPv6.\n")
        except (KeyError, NameError, TypeError, AttributeError):
            sys.stdout.write("Unable to find Redfish DHCPv6 Settings.\n")
        finally:
            try:
                oem_dhcpv4curr = copy.deepcopy(curr_sel.dict['Oem'][self.typepath.defs.oemhp]\
                                                                                        ['DHCPv6'])
                oem_dhcpv6conf = copy.deepcopy(ethernet_data['Oem'][self.typepath.defs.oemhp]\
                                                                                        ['DHCPv6'])
                ipv6curr = copy.deepcopy(curr_sel.dict['Oem'][self.typepath.defs.oemhp]['IPv6'])
                ipv6conf = copy.deepcopy(ethernet_data['Oem'][self.typepath.defs.oemhp]['IPv6'])
            except (KeyError, NameError):
                raise InvalidKeyError("Unable to find OEM Keys for DHCPv6 or IPv6")

        try:
            #if DHCP Enable request but not currently enabled
            if dhcpv4conf['DHCPEnabled'] and not curr_sel.dict['DHCPv4']['DHCPEnabled']:
                self._rdmc.app.patch_handler(path, {"DHCPv4": {"DHCPEnabled": True}})
                sys.stdout.write("DHCP Enabled.\n")
            #if DHCP Disable request but currently enabled
            elif not dhcpv4conf['DHCPEnabled'] and curr_sel.dict['DHCPv4']['DHCPEnabled']:
                self._rdmc.app.patch_handler(path, {"DHCPv4": {"DHCPEnabled": False}})
                dhcpv4conf['UseDNSServers'] = False
                dhcpv4conf['UseNTPServers'] = False
                dhcpv4conf['UseGateway'] = False
                dhcpv4conf['UseDomainName'] = False
                sys.stdout.write("DHCP Disabled.\n")
        except (KeyError, NameError, TypeError, AttributeError):
            #try with OEM
            try:
                if oem_dhcpv4conf['Enabled'] and not curr_sel.dict\
                        ['Oem'][self.typepath.defs.oemhp]['DHCPv4']['Enabled']:
                    self._rdmc.app.patch_handler(path, {'Oem': { \
                    self.typepath.defs.oemhp: {"DHCPv4": {"DHCPEnabled": True}}}})
                    sys.stdout.write("DHCP Enabled.\n")
                    if 'IPv4Addresses' in ethernet_data:
                        del ethernet_data['IPv4Addresses']
                elif not oem_dhcpv4conf['Enabled'] and curr_sel.dict\
                        ['Oem'][self.typepath.defs.oemhp]['DHCPv4']['Enabled']:
                    oem_dhcpv4conf['UseDNSServers'] = False
                    oem_dhcpv4conf['UseNTPServers'] = False
                    oem_dhcpv4conf['UseGateway'] = False
                    oem_dhcpv4conf['UseDomainName'] = False
                    sys.stdout.write("DHCP Disabled.\n")
            except (KeyError, NameError) as exp:
                errors.append("Failure in parsing or removing data in OEM DHCPv4: %s.\n" % exp)

        try:
            #if the ClientIDType is custom and we are missing the ClientID then this property can
            #not be set.
            if 'ClientIdType' in dhcpv4conf.keys():
                if dhcpv4conf['ClientIdType'] == 'Custom' and 'ClientID' not in dhcpv4conf.keys():
                    del ethernet_data['DHCPv4']['ClientIdType']
            elif 'ClientIdType' in oem_dhcpv4conf.keys():
                if oem_dhcpv4conf['ClientIdType'] == 'Custom' and 'ClientID' not in \
                                                                            oem_dhcpv4conf.keys():
                    del ethernet_data['Oem'][self.typepath.defs.oemhp]['DHCPv4']['ClientIdType']
        except (KeyError, NameError, TypeError, AttributeError):
            try:
                if 'ClientIdType' in oem_dhcpv4conf.keys():
                    if oem_dhcpv4conf['ClientIdType'] == 'Custom' and 'ClientID' not in \
                                                                            oem_dhcpv4conf.keys():
                        del ethernet_data['Oem'][self.typepath.defs.oemhp]['DHCPv4']['ClientIdType']
            except (KeyError, NameError) as exp:
                errors.append("Unable to remove property %s.\n" % exp)

        #special considerations go here for things that need to stay despite diffdict
        #EX: IPv4 addresses (aka bug). Changing only one property within the 
        #IPv4StaticAddresses or IPv4Addresses causes an issue during load. Must include IP, 
        #subnet mask and gateway (they can not be patched individually).
        spec_dict = {'Oem': {self.typepath.defs.oemhp: {}}}
        if "IPv4Addresses" in ethernet_data:
            spec_dict['IPv4Addresses'] = copy.deepcopy(ethernet_data['IPv4Addresses'])
        try:
            if "IPv4Addresses" in ethernet_data['Oem'][self.typepath.defs.oemhp]:
                spec_dict['Oem'][self.typepath.defs.oemhp]['IPv4Addresses'] = \
                    copy.deepcopy(ethernet_data['Oem'][self.typepath.defs.oemhp]\
                                                                        ['IPv4StaticAddresses'])
        except (KeyError, NameError, TypeError, AttributeError):
            pass

        #diff and overwrite the original payload
        ethernet_data = diffdict(ethernet_data, curr_sel.dict)
        ethernet_data.update(spec_dict)

        #verify dependencies on those flags which are to be applied are eliminated
        try:
            #delete Domain name and FQDN if UseDomainName for DHCPv4 or DHCPv6
            #is present. can wait to apply at the end
            if dhcpv4conf['UseDomainName']:
                if 'DomainName' in ethernet_data['Oem'][self.typepath.defs.oemhp]:
                    del ethernet_data['Oem'][self.typepath.defs.oemhp]['DomainName']
                if 'FQDN' in ethernet_data:
                    del ethernet_data['FQDN']
        except (KeyError, NameError, TypeError, AttributeError):
            #try again with OEM
            try:
                if oem_dhcpv4conf['UseDomainName'] or oem_dhcpv6conf['UseDomainName']:
                    if 'DomainName' in ethernet_data['Oem'][self.typepath.defs.oemhp]:
                        del ethernet_data['Oem'][self.typepath.defs.oemhp]['DomainName']
                    if 'FQDN' in ethernet_data:
                        del ethernet_data['FQDN']
            except (KeyError, NameError) as exp:
                errors.append("Unable to remove property %s.\n" % exp)

        try:
            #delete DHCP4 DNSServers from IPV4 dict if UseDNSServers Enabled
            #can wait to apply at the end
            if dhcpv4conf.get('UseDNSServers'): #and ethernet_data.get('NameServers'):
                #del_sections('NameServers', ethernet_data)
                self.json_traversal_delete_empty(data=ethernet_data, remove_list=['NameServers'])
        except (KeyError, NameError, TypeError, AttributeError):
            pass
        finally:
            try:
                if oem_dhcpv4conf.get('UseDNSServers'):
                    #del_sections('DNSServers', ethernet_data)
                    self.json_traversal_delete_empty(data=ethernet_data, \
                                                                    remove_list=['DNSServers'])
            except (KeyError, NameError) as exp:
                errors.append("Unable to remove property %s.\n" % exp)

        try:
            if dhcpv4conf.get('UseWINSServers'):
                self.json_traversal_delete_empty(data=ethernet_data, remove_list=['WINServers'])
        except (KeyError, NameError, TypeError, AttributeError):
            pass
        finally:
            try:
                if oem_dhcpv4conf.get('UseWINSServers'):
                    self.json_traversal_delete_empty(data=ethernet_data, \
                                                    remove_list=['WINServers', 'WINSRegistration'])
            except (KeyError, NameError) as exp:
                errors.append("Unable to remove property %s.\n" % exp)

        try:
            if dhcpv4conf['UseStaticRoutes']:
                self.json_traversal_delete_empty(data=ethernet_data, remove_list=['StaticRoutes'])
        except (KeyError, NameError, TypeError, AttributeError):
            pass
        finally:
            try:
                if oem_dhcpv4conf['UseStaticRoutes']:
                    self.json_traversal_delete_empty(data=ethernet_data, \
                                                                    remove_list=['StaticRoutes'])
            except (KeyError, NameError) as exp:
                errors.append("Unable to remove property %s.\n" % exp)

        try:
            #if using DHCPv4, remove static addresses
            if dhcpv4conf.get('DHCPEnabled'):
                self.json_traversal_delete_empty(data=ethernet_data, \
                                            remove_list=['IPv4Addresses', 'IPv4StaticAddresses'])
        except (KeyError, NameError, TypeError, AttributeError):
            pass
        finally:
            try:
                if oem_dhcpv4conf.get('Enabled'):
                    self.json_traversal_delete_empty(data=ethernet_data, \
                                            remove_list=['IPv4Addresses', 'IPv4StaticAddresses'])
            except (KeyError, NameError) as exp:
                errors.append("Unable to remove property %s.\n" % exp)

        try:
            #if not using DHCPv6, remove static addresses from payload
            if dhcpv6conf.get('OperatingMode') == 'Disabled':
                self.json_traversal_delete_empty(data=ethernet_data, \
                                            remove_list=['IPv6Addresses', 'IPv6StaticAddresses'])
        except (KeyError, NameError, TypeError, AttributeError):
            pass
        finally:
            try:
                if not oem_dhcpv6conf.get('StatefulModeEnabled'):
                    self.json_traversal_delete_empty(data=ethernet_data, \
                                            remove_list=['IPv6Addresses', 'IPv6StaticAddresses'])
            except (KeyError, NameError) as exp:
                errors.append("Unable to remove property %s.\n" % exp)

        flags = dict()
        if dhcpv4conf:
            flags['DHCPv4'] = dhcpv4conf
        if dhcpv6conf:
            flags['DHCPv6'] = dhcpv6conf
        if oem_dhcpv4conf:
            flags['Oem'] = {self.typepath.defs.oemhp : {'DHCPv4': oem_dhcpv4conf}}
        if oem_dhcpv6conf:
            flags['Oem'] = {self.typepath.defs.oemhp : {'DHCPv6': oem_dhcpv6conf}}

        #verify dependencies on those flags which are to be applied are eliminated

        try:
            self._rdmc.app.patch_handler(path, flags)
        except IloResponseError as excp:
            errors.append("iLO Responded with the following errors setting DHCP: %s.\n" % excp)

        try:
            if 'AutoNeg' not in ethernet_data.keys():
                self.json_traversal_delete_empty(data=ethernet_data, \
                                            remove_list=['FullDuplex', 'SpeedMbps'])

            #if Full Duplex exists, check if FullDuplexing enabled. If so,
            #remove Speed setting.
            elif 'FullDuplex' in ethernet_data.keys():
                self.json_traversal_delete_empty(data=ethernet_data, \
                                            remove_list=['FullDuplex', 'SpeedMbps'])
        except (KeyError, NameError) as exp:
            errors.append("Unable to remove property %s.\n" % exp)

        try:
            if 'FrameSize' in list(ethernet_data.keys()):
                self.json_traversal_delete_empty(data=ethernet_data, remove_list=['FrameSize'])
        except (KeyError, NameError) as exp:
            errors.append("Unable to remove property %s.\n" % exp)

        try:
            if ethernet_data:
                self._rdmc.app.patch_handler(path, ethernet_data)
            else:
                raise NoDifferencesFoundError
        except IloResponseError:
            try:
                sys.stdout.write("This machine may not have a reconfigurable MACAddress...Retrying"\
                                 " without patching MACAddress.\n")
                if 'MACAddress' in ethernet_data:
                    del ethernet_data['MACAddress']
                if 'MacAddress' in ethernet_data:
                    del ethernet_data['MacAddress']
                self._rdmc.app.patch_handler(path, ethernet_data)
            except IloResponseError as excp:
                errors.append("iLO Responded with the following error: %s.\n" % excp)

        if errors:
            raise IloResponseError("The following errors in, \'%s\' were found collectively: %s" \
                                   % (_type, errors))

    @log_decor
    def load_datetime(self, datetime_data, path):
        """
        Load iLO NTP Servers, DateTime Locale Payload.

        :parm datetime_data: iLO NTP Server and Datetime payload to be loaded
        :type datetime_data: dict
        :param path: iLO schema path
        :type path: string

        """
        errors = []

        if 'StaticNTPServers' in datetime_data:
            sys.stdout.write("Attempting to modify \'UseNTPServers\' in each iLO Management "\
                             "Network Interface regarding the StaticNTPServers list in "\
                             "section \'iLODateTime (DateTime)\'\n")
            oem_str = self.typepath.defs.oempath
            prop_str = (oem_str + '/DHCPv4/UseNTPServers')[1:]
            path_str = self.typepath.defs.managerpath + '*'
            _instances = self._rdmc.app.select('EthernetInterface', \
                                                        (self.typepath.defs.hrefstring, path_str))
            _content = self._rdmc.app.getprops('EthernetInterface', \
                                                        [prop_str], None, True, True, _instances)

            for item in _content:
                try:
                    if next(iter(jsonpath_rw.parse('$..UseNTPServers').find(item))).value:
                        self._rdmc.app.patch_handler(path, \
                                            {'Oem':{oem_str:{'DHCPv4':{'UseNTPServers':True}}}})
                    else:
                        self._rdmc.app.patch_handler(path, \
                                            {'Oem':{oem_str:{'DHCPv4':{'UseNTPServers':False}}}})
                except IloResponseError as excp:
                    errors.append("iLO Responded with the following error: %s.\n" % excp)

        if errors:
            sys.stderr.write("iLO responded with an error while attempting to set values " \
                             "for \'UseNTPServers\'. An attempt to patch DateTime "\
                             "properties will be performed, but may be unsuccessful.\n")
            raise IloResponseError("The following errors in, \'DateTime\' were found " \
                                   "collectively: %s" % errors)

    @log_decor
    def save_license(self, license_data, _type, options):
        """
        Save iLO Server License.

        :parm license_data: iLO Server License payload to be saved
        :type license_data: dict
        :param _type: iLO schema type
        :type _type: string
        :param options: command line options
        :type options: attribute

        """
        key_found = False
        valid_key = False
        license_keys = []
        try:
            if 'LicenseKey' in license_data['ConfirmationRequest']['EON'].keys():
                license_keys.append(license_data['ConfirmationRequest']['EON']['LicenseKey'])
        except:
            pass
        finally:
            license_keys.append(license_data.get('LicenseKey'))
        for lic in reversed(license_keys):
            if lic != '' and lic is not None:
                license_key = lic
                key_found = True
                sys.stdout.write("License Key Found ending in: %s\n" % license_key.split('-')[-1])
                segpass = []
                for seg in lic.split('-'):
                    if 'XXXXX' in seg.upper():
                        segpass.append(True)

                if True not in segpass:
                    valid_key = True
                    break

        if not key_found:
            sys.stdout.write("A License Key was not found on this system.\n")
            license_key = "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"

        if not options.silentcopy and not valid_key:
            while True:
                segpass = []
                license_key = input("Provide your license key: (press enter to skip)\n")

                if license_key.count('X') is 25 or license_key.count('-') is 0:
                    break

                for seg in license_key[0].split('-'):
                    if len(seg) is 5:
                        segpass.append(True)

                if len(segpass) is 5:
                    break
                else:
                    segpass = False
                    sys.stdout.write("An Invalid License Key was Provided: %s\n" % license_key)
        else:
            sys.stdout.write("Remember to verify your License Key...\n")

        #clear everything, we do not need and just keep license key
        license_data = {"LicenseKey": license_key.upper()}
        return license_data

    @log_decor
    def load_license(self, ilolicdata):
        """
        Load iLO Server License.

        :parm ilolicdata: iLO Server License payload to be loaded
        :type ilolicdata: dict

        """
        license_error_list = 'InvalidLicenseKey'
        license_str = ""
        try:
            license_str = ilolicdata['LicenseKey']
            segpass = []
            for seg in license_str.split('-'):
                if len(seg) is 5:
                    segpass.append(True)

            if len(segpass) is 5:
                sys.stdout.write("Attempting to load a license key to the server.\n")
                self.ilolicobj.run(""+ license_str)
            else:
                raise ValueError
        except IloResponseError as excp:
            if str(excp) in license_error_list:
                sys.stdout.write("iLO is not accepting your license key ending in \'%s\'.\n" % \
                                 license_str.split('-')[-1])
        except ValueError:
            sys.stdout.write("An Invalid License Key ending in \'%s\' was provided.\n" % \
                                license_str.split('-')[-1])

    @log_decor
    def save_accounts(self, accounts, _type, options):
        """
        Load iLO User Account Data.

        :parm accounts: iLO User Account payload to be saved
        :type accounts: dict
        :param _type: iLO schema type
        :type _type: string
        :param options: command line options
        :type options: attribute

        """
        try:
            account_type = next(iter(jsonpath_rw.parse('$..Name').find(accounts))).value
        except StopIteration:
            account_type = None

        try:
            account_un = next(iter(jsonpath_rw.parse('$..UserName').find(accounts))).value
        except StopIteration:
            account_un = None

        try:
            account_ln = next(iter(jsonpath_rw.parse('$..LoginName').find(accounts))).value
        except StopIteration:
            account_ln = None

        try:
            privileges = next(iter(jsonpath_rw.parse('$..Privileges').find(accounts))).value
        except StopIteration:
            privileges = None

        try:
            role_id = next(iter(jsonpath_rw.parse('$..RoleId').find(accounts))).value
        except StopIteration:
            role_id = None

        password = [__DEFAULT__, __DEFAULT__]
        if not options.silentcopy:
            while True:
                for i in range(2):
                    if i < 1:
                        sys.stdout.write("Please input the desired password for user: %s\n" \
                                         % account_un)
                    else:
                        sys.stdout.write("Please re-enter the desired password for user: %s\n" \
                                         % account_un)

                    password[i] = getpass.getpass()
                    try:
                        [password[i], _] = password[i].split('\r')
                    except ValueError:
                        pass

                if password[0] == password[1] and (password[0] is not None or password[0] != ''):
                    break
                else:
                    ans = input("You have entered two different passwords...Retry?(y/n)\n")
                    if ans.lower() != 'y':
                        sys.stdout.write("Skipping Account Migration for: %s\n" % account_un)
                        return None
        else:
            sys.stdout.write("Remember to edit password for user: \'%s\', login name: \'%s\'.\n" % \
                             (account_un, account_ln))

        if not password[0]:
            password[0] = __DEFAULT__
            sys.stdout.write("Using a placeholder password of \'%s\' in %s file.\n"  % \
                                                                    (password[0], self.clone_file))
        accounts = {"AccountType": account_type, "UserName": account_un, "LoginName": account_ln,\
                    "Password": password[0], "RoleId": role_id, "Privileges": privileges}

        return accounts

    @log_decor
    def load_accounts(self, user_accounts, _type, path):
        """
        Load iLO User Account Data.

        :parm user_accounts: iLO User Account payload to be loaded
        :type user_accounts: dict
        :param _type: iLO schema type
        :type _type: string
        :param path: iLO schema path
        :type path: string

        """
        config_privs_str = ""
        found_user = False
        if 'UserName' in user_accounts:
            user_name = user_accounts['UserName']
        else:
            user_name = user_accounts['User_Name']
        if 'LoginName' in user_accounts:
            login_name = user_accounts['LoginName']
        else:
            login_name = user_accounts['Login_Name']

        #set minimum password length:
        for _t in self._fdata:
            try:
                if 'AccountService' in _t:
                    _t_path = next(iter(self._fdata.get(_t).keys()))
                    pass_dict = {"Oem": {self.typepath.defs.oemhp: {}}}
                    pass_dict["Oem"][self.typepath.defs.oemhp]['MinPasswordLength'] = \
                                                self._fdata[_t][_t_path]["Oem"]\
                                                [self.typepath.defs.oemhp]["MinPasswordLength"]
                    del self._fdata[_t][_t_path]["Oem"][self.typepath.defs.oemhp]\
                                                                            ["MinPasswordLength"]
                    self._rdmc.app.patch_handler(_t_path, pass_dict)
                    break
            except KeyError as excp:
                if "MinPasswordLength" in excp:
                    pass
                else:
                    raise Exception("An unknown exception occurred: %s" % excp)
            except Exception as excp:
                sys.stderr.write("Unable to set minimum password length for manager accounts.\n")

        #set the current privileges to those in the clone file
        curr_privs = user_accounts['Privileges']

        #set the current role to that in the clone file
        curr_role_id = role_id = None
        role_id = user_accounts.get('RoleId')

        if self.typepath.defs.flagforrest:
            href_path = 'links/self/' + self.typepath.defs.hrefstring
        else:
            href_path = self.typepath.defs.hrefstring

        #obtaining account information on the current server as a check to verify the user
        #provided a decent path to use. This can be re-factored.
        try:
            for curr_sel in self._rdmc.app.select(_type.split('.')[0] + '.'):
                try:
                    curr_privs = curr_sel.dict['Oem'][self.typepath.defs.oemhp]['Privileges']
                    curr_role_id = curr_sel.dict.get('RoleId')
                    #curr_ln = curr_sel.dict['Oem'][self.typepath.defs.oemhp]['LoginName']
                    if 'UserName' in curr_sel.dict.keys():
                        curr_un = curr_sel.dict['UserName']
                    else:
                        curr_un = curr_sel.dict['Oem'][self.typepath.defs.oemhp]['LoginName']
                    if curr_un != user_name:
                        continue
                    else:
                        found_user = True
                        break
                except (KeyError, NameError):
                    sys.stderr.write("Unable to obtain the account information for: \'%s\'\'s'"\
                                     "account.\n" % user_name)
                    continue
        except InstanceNotFoundError:
            pass

        if not found_user:
            sys.stdout.write("Account \'%s\' was not found on this system.\n" % user_name)

        user_pass = user_accounts['Password']

        if 'HostBIOSConfigPriv' in user_accounts['Privileges'] and 'HostBiosConfigPriv' in \
                                                                                    curr_privs:
            if user_accounts['Privileges']['HostBIOSConfigPriv'] and curr_privs\
                                                                    ['HostBIOSConfigPriv']:
                config_privs_str += "8,"
        if 'HostNICConfigPriv' in user_accounts['Privileges'] and 'HostNICConfigPriv' in \
                                                                                    curr_privs:
            if user_accounts['Privileges']['HostNICConfigPriv'] and \
                                                            curr_privs['HostNICConfigPriv']:
                config_privs_str += "7,"
        if 'HostStorageConfigPriv' in user_accounts['Privileges'] and \
                                                    'HostStorageConfigPriv' in curr_privs:
            if user_accounts['Privileges']['HostStorageConfigPriv'] and curr_privs\
                                                                ['HostStorageConfigPriv']:
                config_privs_str += '9,'
        if 'LoginPriv' in user_accounts['Privileges'] and 'LoginPriv' in curr_privs:
            if user_accounts['Privileges']['LoginPriv'] and curr_privs['LoginPriv']:
                config_privs_str += "1,"
        if 'RemoteConsolePriv' in user_accounts['Privileges'] and 'RemoteConsolePriv' \
                                                                                in curr_privs:
            if user_accounts['Privileges']['RemoteConsolePriv'] and \
                                                            curr_privs['RemoteConsolePriv']:
                config_privs_str += "2,"
        if 'SystemRecoveryConfigPriv' in user_accounts['Privileges'] and \
                                                    'SystemRecoveryConfigPriv' in curr_privs:
            if user_accounts['Privileges']['SystemRecoveryConfigPriv'] and curr_privs\
                                                            ['SystemRecoveryConfigPriv']:
                config_privs_str += "10,"
        if 'UserConfigPriv' in user_accounts['Privileges'] and 'UserConfigPriv' in curr_privs:
            if user_accounts['Privileges']['UserConfigPriv'] and curr_privs['UserConfigPriv']:
                config_privs_str += "3,"
        if 'VirtualMediaPriv' in user_accounts['Privileges'] and 'VirtualMediaPriv' in \
                                                                                    curr_privs:
            if user_accounts['Privileges']['VirtualMediaPriv'] and \
                                                                curr_privs['VirtualMediaPriv']:
                config_privs_str += "5,"
        if 'VirtualPowerAndResetPriv' in user_accounts['Privileges'] and \
                                                    'VirtualPowerAndResetPriv' in curr_privs:
            if user_accounts['Privileges']['VirtualPowerAndResetPriv'] and curr_privs\
                                                            ['VirtualPowerAndResetPriv']:
                config_privs_str += "6,"
        if 'iLOConfigPriv' in user_accounts['Privileges'] and 'iLOConfigPriv' in curr_privs:
            if user_accounts['Privileges']['iLOConfigPriv'] and curr_privs['iLOConfigPriv']:
                config_privs_str += "4,"
        config_privs_str = config_privs_str[:-1]

        if curr_role_id == role_id:
            role_id = None

        #Don't think we need to rely on ResourceExists. Should be able to easily tell which
        #operation should be performed before this point.
        if user_pass:
            if user_pass == __DEFAULT__:
                sys.stderr.write("The default password will be attempted.")
            try:
                sys.stdout.write("Adding user \'%s\' to iLO Accounts.\n" % user_name)
                if found_user:
                    raise ResourceExists('')
                if role_id or config_privs_str:
                    #if the user includes both role_id and privileges then the role is applied
                    #first then the privileges are added. Since adding can cause a resource exists
                    #issue here then we just let it happen and perform a modify on the account.
                    if role_id:
                        self.iloacctsobj.run("add "+ user_name +" "+ login_name +" "+ \
                                             user_pass +" "+ " --role " + role_id)
                    if config_privs_str:
                        self.iloacctsobj.run("add "+ user_name +" "+ login_name +" "+ \
                                             user_pass +" "+ " --addprivs "+ config_privs_str)
                else:
                    self.iloacctsobj.run("add "+ user_name + " "+ login_name + " "+ user_pass)
            except ResourceExists:
                sys.stdout.write("The account name \'%s\' exists on this system. "\
                                 "Checking for account modifications.\n" % user_name)
                sys.stdout.write("Changing account password for \'%s\'.\n" % user_name)
                self.iloacctsobj.run("changepass "+ user_name + " "+ user_pass)
                #if the user includes both role_id and privileges then the role is applied first.
                #privileges are modified after, if they exist. Extra steps, yes, in certain cases
                #but not necessarily.
                if config_privs_str or role_id:
                    sys.stdout.write("Changing roles and privileges for \'%s\'.\n" % user_name)
                    if role_id:
                        self.iloacctsobj.run("modify "+ user_name + " --role " + role_id)
                    if config_privs_str:
                        self.iloacctsobj.run("modify "+ user_name +" --addprivs "+ config_privs_str)

        else:
            raise Exception("A password was not provided for account: \'%s\', path: \'%s\'. "\
                            "This account will not be added or will remain unaltered until "\
                            "a valid password is provided.\n" % (user_name, path))

    @log_decor
    def save_federation(self, fedaccts, _type, options):
        """
        Save of Federation Account Data.

        :parm fedaccts: Federation account payload to be saved
        :type fedaccts: dict
        :param _type: iLO schema type
        :type _type: string
        :param options: command line options
        :type options: attribute

        """

        try:
            fed_name = next(iter(jsonpath_rw.parse('$..Name').find(fedaccts))).value
        except StopIteration:
            privileges = None

        try:
            fed_id = next(iter(jsonpath_rw.parse('$..Id').find(fedaccts))).value
        except StopIteration:
            privileges = None

        try:
            privileges = next(iter(jsonpath_rw.parse('$..Privileges').find(fedaccts))).value
        except StopIteration:
            privileges = None

        fedkey = [__DEFAULT__, __DEFAULT__]
        if not options.silentcopy:
            while True:
                for i in range(2):
                    if i < 1:
                        sys.stdout.write("Please input the federation key for Federation user: "\
                                         "%s\n" % fed_name)
                    else:
                        sys.stdout.write("Please re-enter the federation key for Federation "\
                                         "user: %s\n" % fed_name)

                    fedkey[i] = getpass.getpass()
                    try:
                        [fedkey[i], _] = fedkey[i].split('\r')
                    except ValueError:
                        pass

                if fedkey[0] == fedkey[1] and (fedkey[0] is not None or fedkey[0] != ''):
                    break
                else:
                    ans = input("You have entered two different federation keys...Retry?(y/n)\n")
                    if ans.lower() != 'y':
                        sys.stdout.write("Skipping Federation Account Migration for: %s\n"%fed_name)
                        return None
        else:
            sys.stdout.write("Remember to edit the Federation key for acct: \'%s\'.\n" % fed_name)

        if not fedkey[0]:
            fedkey[0] = __DEFAULT__
            sys.stdout.write("Using a placeholder federation key \'%s\' in %s file.\n" % \
                                                                    (fedkey[0], self.clone_file))
        fedaccts = {"AccountID": fed_id, "FederationName": fed_name, "FederationKey": fedkey[0], \
                                                                        "Privileges": privileges}
        return fedaccts

    @log_decor
    def load_federation(self, fed_accounts):
        """
        Load of Federation Account Data.

        :parm fed_accounts: Federation account payload to be loaded
        :type fed_accounts: dict

        """

        config_privs_str = " "
        fed_name = fed_accounts['FederationName']
        fed_key = fed_accounts['FederationKey']
        if fed_key and fed_key != __DEFAULT__:
            if 'HostBIOSConfigPriv' in fed_accounts['Privileges']:
                if not fed_accounts['Privileges']['HostBIOSConfigPriv']:
                    config_privs_str += ' --nobiosconfigpriv'
            if 'HostNICConfigPriv' in fed_accounts['Privileges']:
                if not fed_accounts['Privileges']['HostNICConfigPriv']:
                    config_privs_str += ' --nonicconfigpriv'
            if 'LoginPriv' in fed_accounts['Privileges']:
                if not fed_accounts['Privileges']['LoginPriv']:
                    config_privs_str += ' --nologinpriv'
            if 'RemoteConsolePriv' in fed_accounts['Privileges']:
                if not fed_accounts['Privileges']['RemoteConsolePriv']:
                    config_privs_str += ' --noremoteconsolepriv'
            if 'SystemRecoveryConfigPriv' in fed_accounts['Privileges']:
                if not fed_accounts['Privileges']['SystemRecoveryConfigPriv']:
                    config_privs_str += ' --nosysrecoveryconfigpriv'
            if 'UserConfigPriv' in fed_accounts['Privileges']:
                if not fed_accounts['Privileges']['UserConfigPriv']:
                    config_privs_str += ' --nouserconfigpriv'
            if 'VirtualMediaPriv' in fed_accounts['Privileges']:
                if not fed_accounts['Privileges']['VirtualMediaPriv']:
                    config_privs_str += ' --novirtualmediapriv'
            if 'VirtualPowerAndResetPriv' in fed_accounts['Privileges']:
                if not fed_accounts['Privileges']['VirtualPowerAndResetPriv']:
                    config_privs_str += ' --novirtualprpriv'
            if 'iLOConfigPriv' in fed_accounts['Privileges']:
                if not fed_accounts['Privileges']['iLOConfigPriv']:
                    config_privs_str += ' --noiloconfigpriv'
            try:
                sys.stdout.write("Adding \'%s\' to iLO Federation.\n" % fed_name)
                self.ilofedobj.run("add "+ fed_name +" "+ fed_key +" "+ config_privs_str)
            except ResourceExists:
                sys.stdout.write("This account already exists on this system: \'%s\'\n" % fed_name)
                sys.stdout.write("Changing Federation account: \'%s\'s\' key. Privileges will not"\
                                 " be altered.\n" % fed_name)
                self.ilofedobj.run("changekey "+ fed_name + " " + fed_key)
            except ValueError:
                sys.stdout.write("Some other error occured while attempting to create this "\
                                 "account: %s" % fed_name)
        else:
            sys.stdout.write("A valid Federation key was not provided...skipping account "\
                             "creation for Fed. Acct \'%s\'\n" % fed_name)

    @log_decor
    def save_smartstorage(self, drive_data, _type):
        """
        Smart Storage Disk and Array Controller Configuration save.

        :parm drive_data: Smart Storage Configuration payload to be saved
        :type drive_data: dict
        :param _type: iLO schema type
        :type _type: string

        """
        drive_data['DataGuard'] = "Disabled"
        return drive_data

    @log_decor
    def load_smartstorage(self, drive_data, _type, path):
        """
        Smart Storage Disk and Array Controller Configuration load.

        :parm drive_data: Smart Storage Configuration payload to be loaded
        :type drive_data: dict
        :param _type: iLO schema type
        :type _type: string
        :param path: iLO schema path
        :type path: string

        """
        ignore_list = 'ValueChangedError', None, ""
        errors = []

        smc_str = "smartstorageconfig"
        controller_index = 0
        try:
            tmp = path.split('/')[-3]
            if smc_str in tmp:
                i = 1
                for char in reversed(tmp):
                    if char.isdigit():
                        controller_index += int(char)*i
                    else:
                        break
                    i *= 10
        except ValueError:
            controller_index = 1

        if 'LogicalDrives' in drive_data.keys():
            for l_drive in drive_data['LogicalDrives']:
                logical_drive_str = ''
                logical_drive_str += 'customdrive '
                logical_drive_str += str(l_drive['Raid']) + ' '
                for drive_index in l_drive['DataDrives']:
                    logical_drive_str += drive_index[-1] + ','
                if logical_drive_str[-1] == ',':
                    logical_drive_str = logical_drive_str[:-1]
                logical_drive_str += ' --controller=' + str(controller_index)
                if 'Accelerator' in l_drive:
                    if l_drive['Accelerator']:
                        logical_drive_str += ' --accelerator-type=' + \
                                l_drive['Accelerator']
                if 'BlockSizeBytes' in l_drive:
                    if l_drive['BlockSizeBytes']:
                        logical_drive_str += ' --block-size-bytes=' + \
                                str(l_drive['BlockSizeBytes'])
                if 'SpareDrives' in l_drive:
                    tmp = ''
                    for spares in l_drive['SpareDrives']:
                        tmp += str(spares[-1])
                    if tmp is not '':
                        logical_drive_str += ' --spare-drives=' + tmp
                if 'CapacityBlocks' in l_drive:
                    if l_drive['CapacityBlocks']:
                        logical_drive_str += ' --capacityBlocks=' + \
                                str(l_drive['CapacityBlocks'])
                if 'CapacityGiB' in l_drive:
                    if l_drive['CapacityGiB']:
                        logical_drive_str += ' --capacityGiB=' + \
                                str(l_drive['CapacityGiB'])
                if 'LegacyBootPriority' in l_drive:
                    if l_drive['LegacyBootPriority']:
                        logical_drive_str += ' --legacy-boot=' + \
                                    l_drive['LegacyBootPriority']
                if 'ParityGroupCount' in l_drive:
                    if l_drive['ParityGroupCount']:
                        logical_drive_str += ' --paritytype=' + \
                                str(l_drive['ParityGroupCount'])
                if 'StripSizeBytes' in l_drive:
                    if l_drive['StripSizeBytes']:
                        logical_drive_str += ' --strip-size-bytes=' + \
                                str(l_drive['StripSizeBytes'])
                if 'StripeSizeBytes' in l_drive:
                    if l_drive['StripeSizeBytes']:
                        logical_drive_str += ' --stripe-size-bytes=' + \
                                str(l_drive['StripeSizeBytes'])

                try:
                    self.makedriveobj.run(logical_drive_str)
                except Exception as exp:
                    exp = str(exp)
                    if exp not in ignore_list:
                        errors.append("Path:" + path + ', ' + "Error: " + exp)
        #strip the Logical and Physical Drives properties which leaves just the settings for
        #patching
            del drive_data['LogicalDrives']

        if 'PhysicalDrives' in drive_data.keys():
            del drive_data['PhysicalDrives']
        if 'Ports' in drive_data.keys():
            del drive_data['Ports']
        if 'Location' in drive_data.keys():
            del drive_data['Location']

        if errors:
            raise IloResponseError("The following errors in, \'%s\' were found collectively: %s" \
                                   % (_type, errors))

    #Helper Functions
    @log_decor
    def system_compatibility_check(self, sys_info, options):
        """
        Check if files needed for serverclone are available

        :param sys_info: dictionary of comments for iLO firmware and BIOS ROM
        versions
        :type sys_info: dict
        :param options: command line options
        :type options: attribute

        """

        checks = []
        try:
            curr_sys_info = self._rdmc.app.create_save_header\
                                            (selectignore=True)["Comments"]
            curr_iloversion = curr_sys_info['iLOVersion'].split('v')[0].strip()
            curr_ilorev = curr_sys_info['iLOVersion'].split('v')[1].strip()
            file_iloversion = sys_info['iLOVersion'].split('v')[0].strip()
            file_ilorev = sys_info['iLOVersion'].split('v')[1].strip()
            sys.stdout.write("This system has BIOS Version %s.\n"% \
                                                    curr_sys_info['BIOSFamily'])
            if curr_sys_info['BIOSFamily'] == sys_info['BIOSFamily']:
                sys.stdout.write("BIOS Versions are compatible.\n")
                checks.append(True)
            else:
                sys.stdout.write("BIOS Versions are different. Suggest to have"\
                    " \'%s\' in place before upgrading.\n" % sys_info['BIOSFamily'])
                checks.append(False)
            sys.stdout.write("This system has has %s with firmware revision "\
                             "%s.\n" % (curr_iloversion, curr_ilorev))
            if curr_iloversion == file_iloversion:
                sys.stdout.write("iLO Versions are compatible.\n")
                checks.append(True)
                if curr_ilorev.split('.')[0].strip() == \
                                            file_ilorev.split('.')[0].strip():
                    sys.stdout.write("iLO Firmware Revisions are compatible.\n")
                else:
                    sys.stdout.write("The iLO firmware revisions are different"\
                        ". Suggest to upgrade to revision %s.\n" % file_ilorev)
            else:
                sys.stdout.write("The iLO Versions are different. Suggest to "\
                    "have \'%s v%s\' in place before upgrading.\n" % \
                                            (file_iloversion, file_ilorev))
                checks.append(False)
        except KeyError as exp:
            if 'iLOVersion' in exp:
                sys.stderr.write("iLOVersion not found in clone file "\
                                 "\'Comments\' dictionary.\n")
            elif 'BIOSFamily' in exp:
                sys.stderr.write("BIOS Family not found in clone file "\
                                 "\'Comments\' dictionary.\n")
            else:
                raise Exception("%s" % exp)

        if (len(checks) is 0 or False in checks) and not options.silentcopy:
            while True:
                ans = input("Would you like to continue with migration of iLO"\
                            " configuration from \'%s\' to \'%s\'? (y/n)\n" % \
                            (sys_info['Model'], curr_sys_info['Model']))
                if ans.lower() == 'n':
                    raise NoChangesFoundOrMadeError("Aborting load operation. "\
                                               "No changes made to the server.")
                elif ans.lower() == 'y':
                    break
                else:
                    sys.stdout.write("Invalid input...\n")

        sys.stdout.write('Attempting Clone from a \'%s\' to a \'%s\'.\n' % \
                (sys_info['Model'], curr_sys_info['Model']))

    def get_rootpath(self, path):
        """
        Obtain the root path of the current path (multiple instances within a path)
        :param path: current type path
        :returns: a tuple including either the root_path and the ending or the original path and
        ending
        """

        root_path = ''

        if path[-1] == '/':
            ending = path.split('/')[-2]
        else:
            ending = path.split('/')[-1]

        entries_list = [(pos.start(), pos.end()) for pos in list(re.finditer(ending, path))]
        root_path, ident_ending = path[:entries_list[-1][0]], path[entries_list[-1][0]:]

        #check to verify the root path + ending match the original path.
        _ = ''
        if len(root_path + ident_ending) == len(path):
            return (root_path, _.join(ident_ending.split('/')))
        else:
            return (path, ident_ending)

    def get_filenames(self):
        """
        Obtain a dictionary of filenames for clonefile, and cert files
        :returns: returns dictionary of filenames
        """
        return {'clone_file': self.clone_file, \
                'https_cert_file': self.https_cert_file, \
                'sso_cert_file': self.sso_cert_file}

    def check_files(self, options):
        """
        Check if files needed for serverclone are available

        :param options: command line options
        :type options: attribute
        """

        if options.encryption:
            if self.save:
                sys.stdout.write("Serverclone JSON, \'%s\' will be encrypted.\n" \
                                  % self.clone_file)
            if self.load:
                sys.stdout.write("Expecting an encrypted JSON clone file: %s.\n" \
                                 % self.clone_file)

        #delete anything in the change log file
        with open(self.change_log_file, 'w+') as clf:
            clf.write("")
        #delete anything in the error log file
        with open(self.error_log_file, 'w+') as elf:
            elf.write("")

        #check the clone file exists (otherwise create)
        try:
            if options.encryption:
                file_handle = open(self.clone_file, 'r+b')
            else:
                file_handle = open(self.clone_file, 'r+')
            file_handle.close()
        except:
            if self.save:
                if options.encryption:
                    file_handle = open(self.clone_file, 'w+b')
                else:
                    file_handle = open(self.clone_file, 'w+')
                file_handle.close()
            else:
                sys.stdout.write("The clone file \'%s\', selected for loading,"\
                                 " was not found.\n" % self.clone_file)
                raise IOError

    @log_decor
    def json_traversal_delete_empty(self, data, old_key=None, _iter=None, remove_list=None):
        """
        Recursive function to traverse a dictionary and delete things which
        match elements in the remove_list

        :param data: to be truncated
        :type data: list or dict
        :param old_key: key from previous recursive call (higher in stack)
        :type old_key: dictionary key
        :param _iter: iterator tracker for list (tracks iteration across
        recursive calls)
        :type _iter: numerical iterator
        :param remove_list: list of items to be removed
        :type: list
        :returns: none
        """

        if not remove_list:
            remove_list = ["NONE", None, "", {}, [], "::", "0.0.0.0", "Unknown"]
        list_quick_scan = False

        if isinstance(data, list):
            if _iter is None:
                for idx, val in enumerate(data):
                    if idx is (len(data) - 1):
                        list_quick_scan = True

                    self.json_traversal_delete_empty(val, old_key, idx, remove_list)

                if list_quick_scan:
                    for j in remove_list:
                        for _ in range(data.count(j)):
                            data.remove(j)

        elif isinstance(data, dict):
            for key, value in data.items():
                if (isinstance(value, dict) and len(value) < 1) or (isinstance(value, list)\
                        and len(value) < 1) or None or value in remove_list or key in remove_list:
                    del data[key]

                else:
                    self.json_traversal_delete_empty(value, key, remove_list=remove_list)
                    #would be great to not need this section; however,
                    #since recursive deletion is not possible, this is needed
                    #if you can figure out how to pass by reference then fix me!
                    if (isinstance(value, dict) and len(value) < 1) or \
                        (isinstance(value, list) and len(value) < 1) or None or value in\
                        remove_list:
                        del data[key]

    @log_decor
    def type_compare(self, type1, type2):
        """
        iLO schema type compatibility verification

        :param type1
        :type string
        :param type2
        :type string
        :returns: return tuple with booleans of comparison checks
        """
        _type1 = type1
        _type2 = type2
        checklist = ['Major']#, 'Minor'] #No minor checking for now

        found_type = False
        compatible = list()

        _type1 = self.type_break(_type1)
        _type2 = self.type_break(_type2)

        if _type1[type1]['Type'].lower() == _type2[type2]['Type'].lower():
            found_type = True

        for item in checklist:
            if _type1[type1]['Version'][item] == _type2[type2]['Version'][item]:
                compatible.append('True')
            else:
                compatible.append('False')

        if 'False' in compatible:
            return (found_type, False)
        return (found_type, True)

    @log_decor
    def type_break(self, _type):
        """
        Breakdown of each iLO schema type for version comparison

        :param _type: iLO schema type
        :type _type: string
        """

        _type2 = dict()
        _type_breakdown = _type.split('#')[-1].split('.')
        _type2[_type] = dict([("Type", _type_breakdown[0]), ("Version", {})])
        versioning = list()
        if len(_type_breakdown) == 3 and '_' in _type_breakdown[1]:
            rev = _type_breakdown[1].split('_')
            _type2[_type]["Version"] = {"Major": int(rev[0][-1]),
                                        "Minor": int(rev[1]),
                                        "Errata": int(rev[2])}
        elif len(_type_breakdown) > 3 and '_' not in _type:
            for value in _type_breakdown:
                if value.isdigit():
                    versioning.append(int(value))
            _type2[_type]["Version"] = {"Major": versioning[0],
                                        "Minor": versioning[1],
                                        "Errata": versioning[2]}

        return _type2

    def serverclonevalidation(self, options):
        """
        Serverclone validation function. Validates command line options and
        initiates a login to the iLO Server.

        :param options: command line options
        :type options: list.

        """

        self._cache_dir = os.path.join(self._rdmc.app.config.get_cachedir(), __tempfoldername__)
        if not os.path.exists(self._cache_dir):
            os.makedirs(self._cache_dir)
        self.tmp_clone_file = os.path.join(self._cache_dir, __tmp_clone_file__)
        self.tmp_sel_file = os.path.join(self._cache_dir, __tmp_sel_file__)

        client = None
        inputline = list()

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
            self.loginobj.loginfunction(inputline)

        if self.load:
            if options.noBIOS:
                raise InvalidCommandLineError("\'--nobios\' is only intended for \'save\'"\
                                                  " operation.")
            if options.iLOSSA:
                raise InvalidCommandLineError("\'--ilossa\' is only intended for \'save\'"\
                                                  " operation.")

        if options.clonefilename:
            if len(options.clonefilename) < 2:
                self.clone_file = options.clonefilename[0]
            else:
                raise InvalidCommandLineError("Only a single clone file may be specified.")
        else:
            self.clone_file = __clone_file__

        if options.encryption:
            if len((options.encryption).encode("utf8")) not in [16, 24, 32]:
                raise InvalidKeyError("An invalid encryption key has been used with a length of: "\
                                      "%s chars....ensure the encryption key length is 16, 24 or "\
                                      "32 characters long." % len((options.encryption).\
                                                                                encode("utf8")))
        #filenames
        if options.ssocert:
            if len(options.ssocert) < 2 and self.load:
                self.sso_cert_file = options.ssocert[0]
            else:
                raise InvalidCommandLineError("Ensure you are loading a single SSO certificate"\
                                                  ".\n")
        if options.tlscert:
            if len(options.tlscert) < 2 and self.load:
                self.https_cert_file = options.tlscert[0]
            else:
                raise InvalidCommandLineError("Ensure you are loading a single TLS certificate"\
                                                  ".\n")
        if self._rdmc.opts.debug:
            sys.stderr.write("Debug selected...all exceptions will be handled in an external log "\
                             "file (check error log for automatic testing).\n")
            with open(self.error_log_file, 'w+') as efh:
                efh.write("")

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        add_login_arguments_group(customparser)

        customparser.add_argument(
            '--logout',
            dest='logout',
            help="Include option to logout",
            default=None,
        )
        customparser.add_argument(
            '--biospassword',
            dest='biospassword',
            help="Select this flag to input a BIOS password. Include this"\
            " flag if second-level BIOS authentication is needed for the"\
            " command to execute.",
            default=None,
        )
        customparser.add_argument(
            '--encryption',
            dest='encryption',
            help="Optionally include this flag to encrypt/decrypt a file"\
            " using the key provided.",
            default=None
        )
        customparser.add_argument(
            '--ssocert',
            dest='ssocert',
            help="Use this flag during \'load\' to include an SSO certificate."\
            " This should be properly formatted in a simple text file.",
            action="append",
            default=None,
        )
        customparser.add_argument(
            '--tlscert',
            dest='tlscert',
            help="Use this flag during \'load\' to include a TLS certificate."\
            " This should be properly formatted in a simple text file.",
            action="append",
            default=None,
        )
        customparser.add_argument(
            '-f',
            '--clonefile',
            dest='clonefilename',
            help="Optionally rename the default clone file "\
            "\'ilorest_clone.json\'",
            action="append",
            default=None,
        )
        customparser.add_argument(
            '--uniqueitemoverride',
            dest='uniqueoverride',
            action='store_true',
            help="Override the measures stopping the tool from writing "\
            "over items that are system unique.",
            default=None,
        )
        customparser.add_argument(
            '--quiet',
            '--silent',
            dest='silentcopy',
            help="Optionally include this flag to ignore user prompts for save"\
            " or load processes.",
            action="store_true",
            default=None,
        )
        customparser.add_argument(
            '--ilossa',
            dest='iLOSSA',
            help="Optionally include this flag to include configuration of" \
            " iLO Smart Array Devices during save or load processes.",
            action="store_true",
            default=None,
        )
        customparser.add_argument(
            '--nobios',
            dest='noBIOS',
            help="Optionally include this flag to omit save of Bios configuration."\
            " (During save process only.)",
            action="store_true",
            default=None,
        )
