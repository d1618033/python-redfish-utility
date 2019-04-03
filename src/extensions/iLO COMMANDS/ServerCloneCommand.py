###
# Copyright 2018 Hewlett Packard Enterprise, Inc. All rights reserved.
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
from zipfile import ZipFile
from optparse import OptionParser, SUPPRESS_HELP

import jsonpath_rw
import redfish.ris
from redfish.ris.rmc_helper import (IloResponseError, IdTokenError, InstanceNotFoundError)
from six.moves import input
from rdmc_base_classes import RdmcCommandBase

from rdmc_helper import ReturnCodes, InvalidCommandLineError, InvalidKeyError, Encryption, \
            InvalidCommandLineErrorOPTS, InvalidFileInputError, NoChangesFoundOrMadeError, \
            NoContentsFoundForOperationError, ResourceExists

#default file name
__DEFAULT__ = "<p/k>"
__MINENCRYPTIONLEN__ = 16
__clone_file__ = 'ilorest_clone.json'
__tmp_clone_file__ = '_ilorest_clone_tmp'
__error_log_file__ = 'clone_error_logfile.log'
__changelog_file__ = 'changelog.log'
__archive_file__ = 'ilo_clone_arch.zip'
__ilorest_logfile__ = 'iLOrest.log'

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
        except IloResponseError as exp:
            if not args[0]._rdmc.opts.debug:
                sys.stderr.write("iLO reported an error.\n")
                logging(func.func_name, traceback.format_exc(), exp, args)
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
            usage='This is a BETA command. See serverclone documentation for more information.\n\n'\
            '\tserverclone [save/load] [OPTIONS]\n\n\tCreate a JSON formatted clone file'\
            ' of a system\'s iLO and Bios configuration.\n\tSSA configuration can also optionally '\
            'be added.\n\tBy default the JSON file will be named "ilorest_clone.json".\n\t'\
            'SSO and TLS certificates may be added on load.'\
            '\n\n\tSave of an iLO and Bios config.\n\texample: serverclone save'\
            '\n\n\tSave of an iLO, Bios, and SSA config.\n\texample: serverclone save --ilossa'\
            '\n\n\tSave iLO config omitting BIOS attributes to a non-default file name.\n\t'\
            'example: serverclone save -f serv_clone.json --nobios' \
            '\n\n\tSave an encrypted iLO configuration file (to the default file name)\n\t' \
            'example: serverclone save --encryption <ENCRYPTION KEY>'\
            '\n\n\tLoad a clone file from a non-default file name.\n\t'\
            'example: serverclone load -f serv_clone.json'\
            '\n\n\tLoad a clone file with SSO and TLS certificates.\n\t'\
            'example: serverclone load -ssocert sso.txt --tlscert tls.txt'\
            '\n\n\tLoad a clone file which has been encrypted.\n\t'\
            'example: servercloen laod --encryption abc12abc12abc123\n\n\t'\
            'NOTE 1: Use the \'--silent\' OR \'-quiet\'option to ignore \n\t        '\
            'all user input. Intended for scripting purposes.\n\n\t' \
            'NOTE 2: During clone load, login using an ilo account with\n\t        full privileges'\
            ' (such as the Administrator account)\n\t        to ensure all items are cloned '\
            'successfully.',\
            summary="This is a BETA command. See serverclone documentation for more information. "\
            "Creates a JSON formated clone file of a system's iLO, Bios, and SSA "\
            "configuration which can be duplicated onto other systems. "\
            "User editable JSON file can be manipulated to modify settings before being "\
            "loaded onto another machine.", \
            aliases=None,\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.typepath = rdmcObj.app.typepath
        self.clone_file = None #set in validation
        self.tmp_clone_file = __tmp_clone_file__
        self.change_log_file = __changelog_file__
        self.error_log_file = __error_log_file__
        self.archive_file = None #set in validation
        self.ilorest_log_file = __ilorest_logfile__
        self.https_cert_file = None
        self.sso_cert_file = None
        self.save = None
        self.load = None

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

    def run(self, line):
        """ Main Serverclone Command function
        :param line: string of arguments passed in
        :type line: str.
        """
        _valid_args = ['save', 'load']
        try:
            (options, args) = self._parse_arglist(line)
        except:
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

        if options.archive:
            self.archive_handler()

        return ReturnCodes.SUCCESS

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

        if options.noBIOS and self.save:
            supported_types_list.remove('Bios')

        unsupported_types_list = ['Collection', 'PowerMeter', 'HpeBiosMapping']

        _types = _types2 = list()
        _types = sorted(set(self._rdmc.app.types('--fulltypes')))

        #supported types comparison
        _types2 = []
        for _type in _types:
            for stype in supported_types_list:
                if stype.lower() in _type.lower():
                    _types2.append(_type)
                    break

        #unsupported types comparison
        _types = _types2
        _types2 = []
        for _type in _types:
            found = False
            for utype in unsupported_types_list:
                if utype.lower() in _type.lower():
                    found = True
            if not found:
                _types2.append(_type)

        return _types2

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

        try:
            if options.encryption:
                file_handle = open(self.clone_file, 'r+b')
                fdata = json.loads(Encryption().decrypt_file(file_handle.read(),\
                                                        options.encryption))
            else:
                file_handle = open(self.clone_file, 'r+')
                fdata = json.loads(file_handle.read())
        except:
            raise InvalidFileInputError("Invalid file formatting found. Verify the file has a "\
                                        "valid JSON format.")
        finally:
            file_handle.close()

        self.loadhelper(fdata, options)
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

        if options.archive:
            self.archive_handler()

        if reset_confirm:
            if 'http' not in self._rdmc.app._rmc_clients._rest_client.base_url:
                sys.stdout.write("Resetting iLO...\n")
                self.iloresetobj.run("")
                sys.stdout.write("Sleeping 120 seconds for iLO reset...\n")
                time.sleep(120)
                sys.stdout.write("Resetting System...\n")
                self.reboot_server()
            else:
                sys.stdout.write("Resetting System...\n")
                self.reboot_server()
                sys.stdout.write("Resetting iLO...\n")
                self.iloresetobj.run("")
                sys.stdout.write("Sleeping 120 seconds for iLO reset...\n")
                time.sleep(120)
        else:
            sys.stdout.write("Aborting Server Reboot and iLO reset...\n")
            sys.stdout.write("TestMode...%s\n" % options.testmode)
            sys.stdout.write("Reset...%s\n" % reset_confirm)

    def loadhelper(self, fdata, options):
        """
        Helper function for loading which calls additional helper functions for
        Server BIOS and Firmware compatibility, type compatibility, patch or
        postability (special functions). Data deemed for exclusive patching
        (through load) is written into a temporary file, which is deleted unless
        archived for later use.

        :param fdata: JSON payload
        :type fdata: JSON
        :param options: command line options
        :type options: attribute

        """
        data = list()

        server_avail_types = self.getilotypes(options)
        if not server_avail_types:
            raise NoContentsFoundForOperationError("Unable to Obtain iLO Types from server.")

        if 'Comments' in fdata.keys():
            self.system_compatibility_check(fdata['Comments'], options)
            del fdata['Comments']
        else:
            raise InvalidFileInputError("Clone File \'%s\' does not include a valid \'Comments\' "\
                                        "dictionary.")

        if options.ssocert:
            self.load_ssocertificate()  #check and load sso certificates
        if options.tlscert:
            self.load_tlscertificate()  #check and load tls certificates

        typelist = []
        for _x in fdata:
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
            thispath = next(iter(fdata[_type].keys()))
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
            for thing in fdata[_type]:
                # if we only have a single path, the base path is in the path and only a single
                #instance was retrieved from the server
                if singlet and root_path_comps[0] in thing and len(scanned_dict) is 1:
                    scanned_dict[next(iter(scanned_dict))] = {'Origin': 'File', 'Scanned': False, \
                                                              'Data': fdata[_type][thing]}
                else:
                    scanned_dict[thing] = {'Origin': 'File', 'Scanned': False, 'Data': fdata[_type]\
                                           [thing]}

            for path in scanned_dict.keys():
                try:
                    if scanned_dict[path]['Origin'] is 'Server':
                        # if the instance item was not replaced with an entry in the clone file then
                        # it will be deleted
                        sys.stdout.write("Entry \'%s\' will be removed from this server.\n" % path)
                        raise KeyError(path)
                    else:
                        tmp = self.subhelper(scanned_dict[path]['Data'], _type, path, options)
                        if tmp:
                            data.append(tmp)

                except KeyError as excp:
                    if path in str(excp):
                        if not self.delete(scanned_dict[path]['Data'], _type, path, options):
                            #ok so this thing does not have a valid path, is not considered a
                            #deletable item so....idk what to do with you. You go to load.
                            #Goodluck
                            tmp = self.altsubhelper(scanned_dict[path]['Data'], _type, path)
                            if tmp:
                                data.append(tmp)

                except Exception as excp:
                    sys.stdout.write("An error occurred: \'%s\'" % excp)
                    continue
                finally:
                    scanned_dict[path]['Scanned'] = True

        if options.encryption:
            with open(self.tmp_clone_file, 'w+b') as outfile:
                outfile.write(Encryption().encrypt_file(json.dumps(data, indent=2, \
                                        cls=redfish.ris.JSONEncoder), options.encryption))
        else:
            with open(self.tmp_clone_file, 'w+') as outfile:
                outfile.write(json.dumps(data, indent=2, cls=redfish.ris.JSONEncoder))

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
        tmp[_type] = {curr_path : file_data[_type][next(iter(file_data[_type]))]}
        self.json_traversal_delete_empty(tmp, None, None)
        return tmp

    def loadpatch(self, options):
        """
        Load temporary patch file to server

        :parm options: command line options
        :type options: attribute
        """
        options_str = ""
        ignore_list = 'ValueChangedError', None, ""

        if options.encryption:
            options_str += " --encryption " + options.encryption

        if options.uniqueoverride:
            options_str += " --uniqueitemoverride"

        try:
            self.loadobj.run("-f " + self.tmp_clone_file + options_str)
        except IloResponseError as iloerr:
            sys.stderr.write("iLO reported an error while patching: %s\n" % iloerr)
        except Exception as excp:
            excp = str(excp)
            if excp not in ignore_list:
                sys.stderr.write("An error occured while patching:\n %s\n" % excp)

        if not options.archive:
            os.remove(self.tmp_clone_file)

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

        if options.encryption:
            with open(self.clone_file, 'w+b') as outfile:
                outfile.write(Encryption().encrypt_file(json.dumps(data, indent=2, \
                                        cls=redfish.ris.JSONEncoder), options.encryption))
        else:
            with open(self.clone_file, 'w+') as outfile:
                outfile.write(json.dumps(data, indent=2, cls=redfish.ris.JSONEncoder))

        outfile.close()

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
        #root_path = None

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

                if 'SmartStorageConfig' in _type or 'HpeiLOLicense' in _type or \
                                                                            'iLOLicense' in _type:
                    templist = ["Modified", "Type", "Description", "Status",\
                            "links", "SettingsResult", "Attributes", \
                            "@odata.context", "@odata.type", "@odata.id",\
                            "@odata.etag", "Links", "Actions", \
                            "AvailableActions", "BiosVersion"]
                    instance = self._rdmc.app.iterateandclear(instance, templist)
                else:
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
            with open(self.change_log_file, 'w+') as change_file:
                change_file.write(json.dumps(status_list, indent=2))

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
    def delete(self, data, _type, path, options):
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
                    return 0
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
                return False

            return True

        if 'FederationGroup' in _type:
            if data['FederationName'] != "DEFAULT":
                sys.stdout.write("Federation Account, \'%s\' was not found in the clone file." \
                                 " Deleting entry from server.\n" % data['FederationName'])
                self.ilofedobj.run("delete "+ data['FederationName'])
            else:
                sys.stdout.write("Deletion of the Default iLO Federation Group is not allowed.\n")
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
        redfish_dhcp4 = False
        redfish_dhcp6 = False

        support_ipv6 = True
        oem = True

        dhcpv4curr = None
        dhcpv4conf = None
        oem_dhcpv4curr = None
        oem_dhcpv4conf = None

        errors = []

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

        if 'Oem' not in ethernet_data.keys():
            sys.stdout.write("OEM section for DHCPv4 and DHCPv6 not present.\n")
            oem = False

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
            if oem and not curr_sel.dict['Oem'][self.typepath.defs.oemhp]['NICEnabled'] and \
                                    ethernet_data['Oem'][self.typepath.defs.oemhp]['NICEnabled']:
                self._rdmc.app.patch_handler(path, {"Oem": {self.typepath.defs.oemhp: \
                                                                            {"NICEnabled": True}}})
                sys.stdout.write("NIC Interface Enabled.\n")
            elif oem and not curr_sel.dict['Oem'][self.typepath.defs.oemhp]['NICEnabled'] and not\
                         ethernet_data['Oem'][self.typepath.defs.oemhp]['NICEnabled']:
                self._rdmc.app.patch_handler(path, {"Oem": { \
                            self.typepath.defs.oemhp: {"NICEnabled": False}}})
                sys.stdout.write("NIC Interface Disabled.\n")
                return
        #except IloResponseError:
        #    raise

        if oem and 'NICSupportsIPv6' in curr_sel.dict['Oem'][self.typepath.defs.oemhp].keys():
            support_ipv6 = curr_sel.dict['Oem'][self.typepath.defs.oemhp]['NICSupportsIPv6']

        try:
            if 'DHCPv4' in curr_sel.dict.keys() and 'DHCPv4' in ethernet_data.keys():
                redfish_dhcp4 = True
                dhcpv4curr = copy.deepcopy(curr_sel.dict['DHCPv4'])
                dhcpv4conf = copy.deepcopy(ethernet_data['DHCPv4'])
            if oem:
                oem_dhcpv4curr = copy.deepcopy(curr_sel.dict['Oem'][self.typepath.defs.oemhp]\
                                                                                        ['DHCPv4'])
                oem_dhcpv4conf = copy.deepcopy(ethernet_data['Oem'][self.typepath.defs.oemhp]\
                                                                                        ['DHCPv4'])
                ipv4curr = copy.deepcopy(curr_sel.dict['Oem'][self.typepath.defs.oemhp]['IPv4'])
                ipv4conf = copy.deepcopy(ethernet_data['Oem'][self.typepath.defs.oemhp]['IPv4'])

        except (KeyError, NameError, TypeError, AttributeError):
            #DHCPv4 Redfish settings are not available. Fallback to OEM.
            sys.stdout.write("Unable to find Redfish DHCPv4 Settings.\n")
            try:
                if oem:
                    oem_dhcpv4curr = copy.deepcopy(curr_sel.dict['Oem'][self.typepath.defs.oemhp]\
                                                                                        ['DHCPv4'])
                    oem_dhcpv4conf = copy.deepcopy(ethernet_data['Oem'][self.typepath.defs.oemhp]\
                                                                                        ['DHCPv4'])
                    ipv4curr = copy.deepcopy(curr_sel.dict['Oem'][self.typepath.defs.oemhp]['IPv4'])
                    ipv4conf = copy.deepcopy(ethernet_data['Oem'][self.typepath.defs.oemhp]['IPv4'])
            except (KeyError, NameError):
                raise InvalidKeyError("Unable to find OEM Keys for DHCPv4 or IPv4")

        if oem_dhcpv4curr:
            if 'DHCPEnabled' in oem_dhcpv4curr.keys():
                dhcp_enabled_key = 'DHCPEnabled'
            else:
                dhcp_enabled_key = 'Enabled'

        try:
            if support_ipv6:
                if 'DHCPv6' in curr_sel.dict.keys() and 'DHCPv6' in ethernet_data.keys():
                    redfish_dhcp6 = True
                    dhcpv6curr = copy.deepcopy(curr_sel.dict['DHCPv6'])
                    dhcpv6conf = copy.deepcopy(ethernet_data['DHCPv6'])
                if oem:
                    oem_dhcpv4curr = copy.deepcopy(curr_sel.dict['Oem'][self.typepath.defs.oemhp]\
                                                                                        ['DHCPv6'])
                    oem_dhcpv6conf = copy.deepcopy(ethernet_data['Oem'][self.typepath.defs.oemhp]\
                                                                                        ['DHCPv6'])
                    ipv6curr = copy.deepcopy(curr_sel.dict['Oem'][self.typepath.defs.oemhp]['IPv6'])
                    ipv6conf = copy.deepcopy(ethernet_data['Oem'][self.typepath.defs.oemhp]['IPv6'])
            else:
                sys.stdout.write("NIC Does not support IPv6.\n")
        except (KeyError, NameError, TypeError, AttributeError):
            sys.stdout.write("Unable to find Redfish DHCPv6 Settings.\n")
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
            if dhcpv4conf[dhcp_enabled_key] and not curr_sel.dict['DHCPv4'][dhcp_enabled_key]:
                self._rdmc.app.patch_handler(path, {"DHCPv4": {"DHCPEnabled": True}})
                sys.stdout.write("DHCP Enabled.\n")
            #if DHCP Disable request but currently enabled
            elif not dhcpv4conf[dhcp_enabled_key] and curr_sel.dict['DHCPv4'][dhcp_enabled_key]:
                self._rdmc.app.patch_handler(path, {"DHCPv4": { \
                                                        "DHCPEnabled": False}})
                dhcpv4conf['UseDNSServers'] = False
                dhcpv4conf['UseNTPServers'] = False
                dhcpv4conf['UseGateway'] = False
                dhcpv4conf['UseDomainName'] = False
                sys.stdout.write("DHCP Disabled.\n")
        except (KeyError, NameError, TypeError, AttributeError):
            #try with OEM
            try:
                if oem and oem_dhcpv4conf['Enabled'] and not curr_sel.dict\
                        ['Oem'][self.typepath.defs.oemhp]['DHCPv4']['Enabled']:
                    self._rdmc.app.patch_handler(path, {'Oem': { \
                    self.typepath.defs.oemhp: {"DHCPv4": {"DHCPEnabled": True}}}})
                    sys.stdout.write("DHCP Enabled.\n")
                    if 'IPv4Addresses' in ethernet_data:
                        del ethernet_data['IPv4Addresses']
                elif oem and not oem_dhcpv4conf['Enabled'] and curr_sel.dict\
                        ['Oem'][self.typepath.defs.oemhp]['DHCPv4']['Enabled']:
                    oem_dhcpv4conf['UseDNSServers'] = False
                    oem_dhcpv4conf['UseNTPServers'] = False
                    oem_dhcpv4conf['UseGateway'] = False
                    oem_dhcpv4conf['UseDomainName'] = False
                    sys.stdout.write("DHCP Disabled.\n")
            except (KeyError, NameError) as exp:
                errors.append("Failure in parsing or removing data in OEM DHCPv4: %s.\n" % exp)

        #diff and overwrite the original payload
        ethernet_data = self._rdmc.app.diffdict(ethernet_data, curr_sel.dict)

        #verify any remaining properties are valid
        try:
            #delete Domain name and FQDN if UseDomainName for DHCPv4 or DHCPv6
            #is present. can wait to apply at the end
            if dhcpv4conf['UseDomainName'] or dhcpv6conf['UseDomainName']:
                if oem and 'DomainName' in ethernet_data['Oem'][self.typepath.defs.oemhp]:
                    del ethernet_data['Oem'][self.typepath.defs.oemhp]['DomainName']
                if 'FQDN' in ethernet_data:
                    del ethernet_data['FQDN']
        except (KeyError, NameError, TypeError, AttributeError):
            #try again with OEM
            try:
                if oem_dhcpv4conf['UseDomainName'] or oem_dhcpv6conf['UseDomainName']:
                    if oem and ('DomainName' in ethernet_data['Oem'][self.typepath.defs.oemhp]):
                        del ethernet_data['Oem'][self.typepath.defs.oemhp]['DomainName']
                    if 'FQDN' in ethernet_data:
                        del ethernet_data['FQDN']
            except (KeyError, NameError) as exp:
                errors.append("Unable to remove property %s.\n" % exp)

        try:
            #delete DHCP4 DNSServers from IPV4 dict if UseDNSServers Enabled
            #can wait to apply at the end
            if dhcpv4conf['UseDNSServers'] and 'DNSServers' in ipv4conf.keys():
                del ipv4conf['DNSServers']
                if 'NameServers' in ethernet_data:
                    del ethernet_data['NameServers']
        except (KeyError, NameError, TypeError, AttributeError):
            #try again with OEM
            try:
                if oem_dhcpv4conf['UseDNSServers'] and 'DNSServers' in ipv4conf.keys():
                    del ipv4conf['DNSServers']
            except (KeyError, NameError) as exp:
                errors.append("Unable to remove property %s.\n" % exp)

        if support_ipv6:
            try:
                #delete DHCP6 DNSServers from IPV6 dict if UseDNSServers Enabled
                #can wait to apply at the end
                if dhcpv6conf['UseDNSServers'] and 'DNSServers' in ipv6conf.keys():
                    del ipv6conf['DNSServers']
            except (KeyError, NameError, TypeError, AttributeError):
                #try againw tih OEM
                try:
                    if oem_dhcpv6conf['UseDNSServers'] and 'DNSServers' in ipv6conf.keys():
                        del ipv6conf['DNSServers']
                except (KeyError, NameError) as exp:
                    errors.append("Unable to remove property %s.\n" % exp)

        try:
            if dhcpv4conf['UseWINSServers']:
                if 'WINServers' in ipv4conf.keys():
                    del ipv4conf['WINServers']
                if 'WINSRegistration' in ipv4conf.keys():
                    del ipv4conf['WINSRegistration']
        except (KeyError, NameError, TypeError, AttributeError):
            #try again with OEM
            try:
                if oem_dhcpv4conf['UseWINSServers']:
                    if 'WINServers' in ipv4conf.keys():
                        del ipv4conf['WINServers']
                    if 'WINSRegistration' in ipv4conf.keys():
                        del ipv4conf['WINSRegistration']
            except (KeyError, NameError) as exp:
                errors.append("Unable to remove property %s.\n" % exp)

        try:
            if dhcpv4conf['UseStaticRoutes'] and 'StaticRoutes' in ipv4conf.keys():
                del ipv4conf['StaticRoutes']
        except (KeyError, NameError, TypeError, AttributeError):
            #try again with OEM
            try:
                if oem_dhcpv4conf['UseStaticRoutes'] and 'StaticRoutes' in ipv4conf.keys():
                    del ipv4conf['StaticRoutes']
            except (KeyError, NameError) as exp:
                errors.append("Unable to remove property %s.\n" % exp)

        try:
            #if using DHCPv4, remove static addresses
            if dhcpv4conf[dhcp_enabled_key] and 'IPv4StaticAddresses' in ethernet_data.keys():
                del ethernet_data['IPv6StaticAddresses']
        except (KeyError, NameError, TypeError, AttributeError):
            #try again with OEM
            try:
                if oem_dhcpv4conf[dhcp_enabled_key]:
                    if 'IPv4StaticAddresses' in ipv4conf.keys():
                        del ipv4conf['IPv4StaticAddresses']
                    if 'IPv4Addresses' in ethernet_data.keys():
                        del ethernet_data['IPv4Addresses']
            except (KeyError, NameError) as exp:
                errors.append("Unable to remove property %s.\n" % exp)

        try:
            #if not using DHCPv6, remove static addresses from payload
            if not dhcpv6conf[dhcp_enabled_key] and 'IPv6StaticAddresses' in ethernet_data.keys():
                del ethernet_data['IPv6StaticAddresses']
        except (KeyError, NameError, TypeError, AttributeError):
            #try again with OEM
            try:
                if not oem_dhcpv6conf[dhcp_enabled_key] and 'IPv6StaticAddresses' in \
                                                                                ipv4conf.keys():
                    del ipv4conf['IPv6StaticAddresses']
            except (KeyError, NameError) as exp:
                errors.append("Unable to remove property %s.\n" % exp)

        try:
            if 'AutoNeg' not in ethernet_data.keys() and 'SpeedMbps' \
                                            not in ethernet_data.keys():
                del ethernet_data['FullDuplex']

            if 'AutoNeg' in ethernet_data.keys():
                if ethernet_data['AutoNeg'] or ethernet_data['AutoNeg'] is None:
                    if 'FullDuplex' in ethernet_data.keys():
                        del ethernet_data['FullDuplex']
                    if 'SpeedMbps' in ethernet_data.keys():
                        del ethernet_data['SpeedMbps']
            #if Full Duplex exists, check if FullDuplexing enabled. If so,
            #remove Speed setting.
            elif 'FullDuplex' in ethernet_data.keys():
                if ethernet_data['FullDuplex']:
                    del ethernet_data['FullDuplex']
                if 'SpeedMbps' in ethernet_data.keys():
                    del ethernet_data['SpeedMbps']
        except (KeyError, NameError):
            errors.append("Unable to remove property %s.\n" % exp)

        try:
            if 'FrameSize' in list(ethernet_data.keys()):
                del ethernet_data['FrameSize']
        except (KeyError, NameError) as exp:
            errors.append("Unable to remove property %s.\n" % exp)

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

        self.json_traversal_delete_empty(ethernet_data, None, None)
        try:
            self._rdmc.app.patch_handler(path, ethernet_data)
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
        if 'StaticNTPServers' in datetime_data:
            oem_str = self.typepath.defs.oempath
            prop_str = (oem_str + '/DHCPv4/UseNTPServers')[1:]
            path_str = self.typepath.defs.managerpath + '*'
            _instances = self._rdmc.app.select('EthernetInterface', \
                                                        (self.typepath.defs.hrefstring, path_str))
            _content = self._rdmc.app.getprops('EthernetInterface', \
                                                        [prop_str], None, True, True, _instances)

            for item in _content:
                if next(iter(jsonpath_rw.parse('$..UseNTPServers').find(item))).value:
                    self._rdmc.app.patch_handler(path, \
                                            {'Oem':{oem_str:{'DHCPv4':{'UseNTPServers':True}}}})
                else:
                    self._rdmc.app.patch_handler(path, \
                                            {'Oem':{oem_str:{'DHCPv4':{'UseNTPServers':False}}}})

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
        if 'LicenseKey' in license_data.keys():
            license_keys.append(license_data['LicenseKey'])
        if not self.typepath.defs.flagforrest:
            if 'LicenseKey' in license_data['ConfirmationRequest']['EON'].keys():
                license_keys.append(license_data['ConfirmationRequest']['EON']['LicenseKey'])
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
                    "Password": password[0], "Privileges": privileges}

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
        user_name = user_accounts['UserName']
        login_name = user_accounts['LoginName']

        #set the current privileges to those in the clone file
        curr_privs = user_accounts['Privileges']

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
        if 'HostNICConfigPriv' in user_accounts['Privileges'] and 'HostNICConfigPriv' in curr_privs:
            if user_accounts['Privileges']['HostNICConfigPriv'] and curr_privs['HostNICConfigPriv']:
                config_privs_str += "7,"
        if 'HostStorageConfigPriv' in user_accounts['Privileges'] and 'HostStorageConfigPriv' in \
                                                                                        curr_privs:
            if user_accounts['Privileges']['HostStorageConfigPriv'] and curr_privs\
                                                                    ['HostStorageConfigPriv']:
                config_privs_str += '9,'
        if 'LoginPriv' in user_accounts['Privileges'] and 'LoginPriv' in curr_privs:
            if user_accounts['Privileges']['LoginPriv'] and curr_privs['LoginPriv']:
                config_privs_str += "1,"
        if 'RemoteConsolePriv' in user_accounts['Privileges'] and 'RemoteConsolePriv' in curr_privs:
            if user_accounts['Privileges']['RemoteConsolePriv'] and curr_privs['RemoteConsolePriv']:
                config_privs_str += "2,"
        if 'SystemRecoveryConfigPriv' in user_accounts['Privileges'] and 'SystemRecoveryConfigPriv'\
                                                                                     in curr_privs:
            if user_accounts['Privileges']['SystemRecoveryConfigPriv'] and curr_privs\
                                                                ['SystemRecoveryConfigPriv']:
                config_privs_str += "10,"
        if 'UserConfigPriv' in user_accounts['Privileges'] and 'UserConfigPriv' in curr_privs:
            if user_accounts['Privileges']['UserConfigPriv'] and curr_privs['UserConfigPriv']:
                config_privs_str += "3,"
        if 'VirtualMediaPriv' in user_accounts['Privileges'] and 'VirtualMediaPriv' in curr_privs:
            if user_accounts['Privileges']['VirtualMediaPriv'] and curr_privs['VirtualMediaPriv']:
                config_privs_str += "5,"
        if 'VirtualPowerAndResetPriv' in user_accounts['Privileges'] and 'VirtualPowerAndResetPriv'\
                                                                                     in curr_privs:
            if user_accounts['Privileges']['VirtualPowerAndResetPriv'] and curr_privs\
                                                                ['VirtualPowerAndResetPriv']:
                config_privs_str += "6,"
        if 'iLOConfigPriv' in user_accounts['Privileges'] and 'iLOConfigPriv' in curr_privs:
            if user_accounts['Privileges']['iLOConfigPriv'] and curr_privs['iLOConfigPriv']:
                config_privs_str += "4,"
        config_privs_str = config_privs_str[:-1]

        #Don't think we need to rely on ResourceExists. Should be able to easily tell which
        #operation should be performed before this point.
        if user_pass:
            if user_pass == __DEFAULT__:
                self._rdmc.app.warning_handler("The default password will be attempted.")
            try:
                if found_user:
                    raise ResourceExists('')
                if config_privs_str:
                    sys.stdout.write("Adding user \'%s\' to iLO Accounts.\n" % user_name)
                    self.iloacctsobj.run("add "+ user_name + " "+ login_name + " "+ user_pass +" "+\
                                      " --addprivs "+ config_privs_str)
                else:
                    self.iloacctsobj.run("add "+ user_name + " "+ login_name + " "+ user_pass)
            except ResourceExists:
                sys.stdout.write("The account name \'%s\' exists on this system. "\
                                 "Checking for account modifications.\n" % user_name)
                sys.stdout.write("Changing account password for \'%s\'.\n" % user_name)
                self.iloacctsobj.run("changepass "+ user_name + " "+ user_pass)
                if config_privs_str:
                    sys.stdout.write("Changing privileges for \'%s\'.\n" % user_name)
                    self.iloacctsobj.run("modify " + user_name + " --addprivs "+ config_privs_str)

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
        if fed_key:
            if fed_key == __DEFAULT__:
                self._rdmc.app.warning_handler("The default password will be attempted.")
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
                raise

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
    def reboot_server(self):
        """
        Reboot server operation
        """
        # unable to use Reboot command due to logout upon completion

        results = self._rdmc.app.select(selector="ComputerSystem.")
        bdict = next(iter(results)).resp.dict
        if results and bdict:
            try:
                reboot_path = bdict[self.typepath.defs.hrefstring]
            except KeyError:
                reboot_path = bdict['links']['self'][self.typepath.defs.hrefstring]
            finally:
                if 'Actions' in bdict:
                    action = next(iter(bdict['Actions'].keys())).split('#')[-1]
                    reboot_path += 'Actions/' + action + '/'
                else:
                    action = 'Reset'
                body = {"Action": action, "ResetType": "ForceRestart"}
                self._rdmc.app.post_handler(reboot_path, body)

    @log_decor
    def archive_handler(self):
        """
        Handles archiving of data for bug tracking and reporting
        """
        #hidden command only
        packlist = [self.clone_file, self.error_log_file, self.ilorest_log_file]

        if self.load:
            packlist.append(self.tmp_clone_file)
            packlist.append(self.change_log_file)

        with ZipFile(self.archive_file, 'w') as zip_arch:
            for _file in packlist:
                try:
                    zip_arch.write(_file)
                    os.remove(_file)
                except:
                    pass

        sys.stdout.write("Clone file, and log files saved to: %s\n" % \
                         self.archive_file)
        zip_arch.printdir()

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

                    self.json_traversal_delete_empty(val, old_key, idx)

                if list_quick_scan:
                    for j in remove_list:
                        for _ in range(data.count(j)):
                            data.remove(j)

        elif isinstance(data, dict):
            for key, value in data.items():
                if (isinstance(value, dict) and len(value) < 1) or (isinstance(value, list)\
                        and len(value) < 1) or None or value in remove_list:
                    del data[key]

                else:
                    self.json_traversal_delete_empty(value, key)
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
        client = None
        inputline = list()

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

        if inputline or not client:
            self.loginobj.loginfunction(inputline)

        if options.clonefilename:
            if len(options.clonefilename) < 2:
                self.clone_file = options.clonefilename[0]
            else:
                raise InvalidCommandLineErrorOPTS("Only a single clone file may be specified.")
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
                raise InvalidCommandLineErrorOPTS("Ensure you are loading a single SSO certificate"\
                                                  ".\n")
        if options.tlscert:
            if len(options.tlscert) < 2 and self.load:
                self.https_cert_file = options.tlscert[0]
            else:
                raise InvalidCommandLineErrorOPTS("Ensure you are loading a single TLS certificate"\
                                                  ".\n")

        if options.archive:
            if len(options.archive) < 2:
                self.archive_file = options.archive[0]
            else:
                raise InvalidCommandLineErrorOPTS("Only a single archive file may be specified.")
        else:
            self.archive_file = __archive_file__

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
            help="Pass this flag along with the password flag if you are"\
            "running in local higher security modes.""",
            default=None,
        )
        customparser.add_option(
            '-p',
            '--password',
            dest='password',
            help="Pass this flag along with the username flag if you are"\
            "running in local higher security modes.""",
            default=None,
        )
        customparser.add_option(
            '--logout',
            dest='logout',
            help="Include option to logout",
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
            '--encryption',
            dest='encryption',
            help="Optionally include this flag to encrypt/decrypt a file"\
            " using the key provided.",
            default=None
        )
        customparser.add_option(
            '--ssocert',
            dest='ssocert',
            help="Use this flag during \'load\' to include an SSO certificate."\
            " This should be properly formatted in a simple text file.",
            action="append",
            default=None,
        )
        customparser.add_option(
            '--tlscert',
            dest='tlscert',
            help="Use this flag during \'load\' to include a TLS certificate."\
            " This should be properly formatted in a simple text file.",
            action="append",
            default=None,
        )
        customparser.add_option(
            '-f',
            '--clonefile',
            dest='clonefilename',
            help="Optionally rename the default clone file "\
            "\'ilorest_clone.json\'",
            action="append",
            default=None,
        )
        #to possibly be deleted in a future release
        customparser.add_option(
            '--errarch',
            '--archive',
            dest='archive',
            help="Allow for save to automatically archive the clone file and "\
                 "error log file. Use with load will archive the clone file, "\
                 "temporary patch file, error log file and changelog file.",
            action="append",
            default=None,
        )
        customparser.add_option(
            '--uniqueitemoverride',
            dest='uniqueoverride',
            action='store_true',
            help="Override the measures stopping the tool from writing "\
            "over items that are system unique.",
            default=None,
        )
        customparser.add_option(
            '--quiet',
            '--silent',
            dest='silentcopy',
            help="Optionally include this flag to ignore user prompts for save"\
            " or load processes.",
            action="store_true",
            default=None,
        )
        customparser.add_option(
            '--ilossa',
            dest='iLOSSA',
            help="Optionally include this flag to include configuration of" \
            " iLO Smart Array Devices during save or load processes.",
            action="store_true",
            default=None,
        )
        customparser.add_option(
            '--nobios',
            dest='noBIOS',
            help="Optionally include this flag to remove Bios configuration "\
            " during save or load processes.",
            action="store_true",
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
