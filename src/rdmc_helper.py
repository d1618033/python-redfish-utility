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
"""This is the helper module for RDMC"""

#---------Imports---------

import sys
import time
import json
import logging
import versioning

import redfish.ris

from collections import OrderedDict

#---------End of imports---------


#---------Debug logger---------

LOGGER = logging.getLogger()

# default logging level setting
LOGGER.setLevel(logging.ERROR)
# log all errors to stderr instead of stdout
LERR = logging.StreamHandler(sys.stderr)
# loggin format
LERRFMT = logging.Formatter("%(levelname)s\t: %(message)s")
# set formatter
LERR.setFormatter(LERRFMT)
LERR.name = 'lerr'
# default stderr level setting
LERR.setLevel(logging.WARN)
# logger handle
LOGGER.addHandler(LERR)

#---------End of debug logger---------

class ReturnCodes(object):
    """ Return code class to be used by all functions """
    SUCCESS = 0

    # ****** RDMC ERRORS ******
    CONFIGURATION_FILE_ERROR = 1
    COMMAND_NOT_ENABLED_ERROR = 2
    INVALID_COMMAND_LINE_ERROR = 3
    INVALID_FILE_FORMATTING_ERROR = 4
    USER_NOT_ADMIN = 5
    NO_CONTENTS_FOUND_FOR_OPERATION = 6
    INVALID_FILE_INPUT_ERROR = 7
    NO_CHANGES_MADE_OR_FOUND = 8
    NO_VALID_INFO_ERROR = 9

    # ****** CLI ERRORS ******
    UI_CLI_ERROR_EXCEPTION = 10
    UI_CLI_WARN_EXCEPTION = 11
    UI_CLI_USAGE_EXCEPTION = 12
    UI_CLI_COMMAND_NOT_FOUND_EXCEPTION = 13

    # ****** RMC/RIS ERRORS ******
    RIS_UNDEFINED_CLIENT_ERROR = 21
    RIS_CURRENTLY_LOGGED_IN_ERROR = 22
    RIS_INSTANCE_NOT_FOUND_ERROR = 23
    RIS_NOTHING_SELECTED_ERROR = 24
    RIS_NOTHING_SELECTED_FILTER_ERROR = 25
    RIS_NOTHING_SELECTED_SET_ERROR = 26
    RIS_INVALID_SELECTION_ERROR = 27
    RIS_VALIDATION_ERROR = 28
    RIS_MISSING_ID_TOKEN = 29
    RIS_SESSION_EXPIRED = 30

    # ****** REST V1 ERRORS ******
    V1_RETRIES_EXHAUSTED_ERROR = 31
    V1_INVALID_CREDENTIALS_ERROR = 32
    V1_SERVER_DOWN_OR_UNREACHABLE_ERROR = 33
    V1_CHIF_DRIVER_MISSING_ERROR = 34
    REST_ILOREST_CHIF_DLL_MISSING_ERROR = 35
    REST_ILOREST_UNEXPECTED_RESPONSE_ERROR = 36
    REST_ILOREST_ILO_ERROR = 37
    REST_ILOREST_CREATE_BLOB_ERROR = 38
    REST_ILOREST_READ_BLOB_ERROR = 39

    # ****** RDMC ERRORS ******
    SAME_SETTINGS_ERROR = 40
    FIRMWARE_UPDATE_ERROR = 41
    BOOT_ORDER_ENTRY_ERROR = 42
    NIC_MISSING_OR_INVALID_ERROR = 43
    NO_CURRENT_SESSION_ESTABLISHED = 44
    FAILURE_DURING_COMMIT_OPERATION = 45
    MULTIPLE_SERVER_CONFIG_FAIL = 51
    MULTIPLE_SERVER_INPUT_FILE_ERROR = 52
    LOAD_SKIP_SETTING_ERROR = 53
    INCOMPATIBLE_ILO_VERSION_ERROR = 54
    INVALID_CLIST_FILE_ERROR = 55
    UNABLE_TO_MOUNT_BB_ERROR = 56
    BIRTHCERT_PARSE_ERROR = 57
    INCOMPATIBLE_SERVER_TYPE = 58
    ILO_LICENSE_ERROR = 59
    ACCOUNT_EXISTS_ERROR = 60

    # ****** RMC/RIS ERRORS ******
    RIS_VALUE_CHANGED_ERROR = 61
    RIS_REF_PATH_NOT_FOUND_ERROR = 62
    RIS_ILO_RESPONSE_ERROR = 63

    # ****** REST V1 ERRORS ******
    REST_ILOREST_WRITE_BLOB_ERROR = 70
    REST_ILOREST_BLOB_DELETE_ERROR = 71
    REST_ILOREST_BLOB_FINALIZE_ERROR = 72
    REST_ILOREST_BLOB_NOT_FOUND_ERROR = 73
    JSON_DECODE_ERROR = 74
    V1_SECURITY_STATE_ERROR = 75
    REST_ILOREST_BLOB_OVERRIDE_ERROR = 76

    # ****** RIS ERRORS ******
    RIS_RIS_BIOS_UNREGISTERED_ERROR = 100

    # ****** GENERAL ERRORS ******
    GENERAL_ERROR = 255


class RdmcError(Exception):
    """ Baseclass for all rdmc exceptions """
    errcode = 1
    def __init__(self, message):
        Exception.__init__(self, message)

class ConfigurationFileError(RdmcError):
    """Raised when something is wrong in the config file"""
    errcode = 3

class CommandNotEnabledError(RdmcError):
    """ Raised when user tries to invoke a command that isn't enabled """
    pass

class PathUnavailableError(Exception):
    """Raised when the requested path is unavailable"""
    pass

class InvalidCommandLineError(RdmcError):
    """ Raised when user enter incorrect command line arguments """
    pass

class NoCurrentSessionEstablished(RdmcError):
    """ Raised when user enter incorrect command line arguments """
    pass

class NoChangesFoundOrMadeError(RdmcError):
    """ Raised when no changes were found or made on the commit function """
    pass

class StandardBlobErrorHandler(RdmcError):
    """ Raised when error occured for blob operations """
    pass

class InvalidCommandLineErrorOPTS(RdmcError):
    """ Raised when user enter incorrect command line arguments """
    pass

class InvalidFileInputError(RdmcError):
    """ Raised when user enter an invalid file input """
    pass

class InvalidFileFormattingError(RdmcError):
    """ Raised when user enter incorrect load file formatting """
    pass

class WindowsUserNotAdmin(RdmcError):
    """ Raised when user is not running as admin """
    pass

class NoContentsFoundForOperationError(RdmcError):
    """ Raised when no contents were found for the current operation """
    pass

class InfoMissingEntriesError(RdmcError):
    """ Raised when no valid entries for info were found in the current
        instance"""
    pass

class InvalidOrNothingChangedSettingsError(RdmcError):
    """ Raised when something is wrong with the settings """
    pass

class NoDifferencesFoundError(RdmcError):
    """ Raised when no differences are found in the current configuration """
    pass

class MultipleServerConfigError(RdmcError):
    """ Raised when one or more servers failed to load given configuration """
    pass

class InvalidMSCfileInputError(RdmcError):
    """ Raised when servers input file for load has incorrect parameters"""
    pass

class FirmwareUpdateError(RdmcError):
    """ Raised when there is an error while updating firmware """
    pass
class FailureDuringCommitError(RdmcError):
    """ Raised when there is an error during commit """
    pass

class BootOrderMissingEntriesError(RdmcError):
    """ Raised when no entries were found for bios tools """
    pass

class NicMissingOrConfigurationError(RdmcError):
    """ Raised when no entries are found for given NIC or all NICs are \
     configured or when wrong inputs are presented for NIC entries"""
    pass

class IncompatibleiLOVersionError(RdmcError):
    """Raised when the iLO version is above or below the required \
    version"""
    pass

class IncompatableServerTypeError(RdmcError):
    """Raised when the server type is incompatable with the requested\
    command"""
    pass

class IloLicenseError(RdmcError):
    """Raised when the proper iLO license is not available for a command"""
    pass

class AccountExists(RdmcError):
    """Raised when the account to be added already exists"""
    pass

class InvalidCListFileError(RdmcError):
    """Raised when an error occurs while reading the cfilelist \
    within AHS logs"""
    pass

class PartitionMoutingError(RdmcError):
    """Raised when there is error or iLO fails to respond to \
    partition mounting request"""
    pass

class LibHPsrvMissingError(RdmcError):
    """ Raised when unable to obtain the libhpsrv handle"""
    pass

class BirthcertParseError(RdmcError):
    """ Raised when unable to parse the birthcert"""
    pass

class UI(object):
    """ UI class handles all of our printing etc so we have
    consistency across the project """

    def command_not_found(self, excp):
        """ Called when command was not found """
        sys.stderr.write(u"\nCommand '%s' not found. Use the help command to " \
                                "see a list of available commands\n" % excp)

    def command_not_enabled(self, excp):
        """ Called when command has not been enabled """
        sys.stderr.write(u"\nCommand has not been enabled: %s\n" % excp)

    def invalid_commmand_line(self, excp):
        """ Called when user entered invalid command line entries """
        sys.stderr.write(u"Error: %s\n" % excp)

    def standard_blob_error(self, excp):
        """ Called when user error encountered with blob """
        sys.stderr.write(u"Error: Blob operation failed with error code %s\n" \
                                                                        % excp)

    def invalid_file_formatting(self, excp):
        """ Called when file formatting is unrecognizable """
        sys.stderr.write(u"Error: %s\n" % excp)

    def user_not_admin(self):
        """ Called when file formatting in unrecognizable """
        sys.stderr.write(u"Both remote and local mode is accessible when %s is "\
            "run as administrator. Only remote mode is available for non-"\
            "admin user groups.\n" % versioning.__longname__)

    def no_contents_found_for_operation(self, excp):
        """ Called when no contents were found for the current operation"""
        sys.stderr.write(u"Error: %s\n" % excp)

    def nothing_selected(self):
        """ Called when nothing has been select yet """
        sys.stderr.write(u"No type currently selected. Please use the" \
                         " 'types' command to\nget a list of types, or input" \
                         " your type by using the '--selector' flag.\n")

    def nothing_selected_filter(self):
        """ Called when nothing has been select after a filter set """
        sys.stderr.write(u"Nothing was found to match your provided filter.\n")

    def nothing_selected_set(self):
        """ Called when nothing has been select yet """
        sys.stderr.write(u"Nothing is selected or selection is read-only.\n")

    def no_differences_found(self, excp):
        """ Called when no difference is found in the current configuration """
        sys.stderr.write(u"Error: %s\n" % excp)

    def multiple_server_config_fail(self, excp):
        """Called when one or more servers failed to load given configuration"""
        sys.stderr.write(u"Error: %s\n" % excp)

    def multiple_server_config_input_file(self, excp):
        """Called when servers input file has incorrect information"""
        sys.stderr.write(u"Error: %s\n" % excp)

    def invalid_credentials(self, timeout):
        """ Called user has entered invalid credentials

        :param timeout: timeout given for failed login attempt
        :type timeout: int.
        """
        sys.stderr.write(u"Validating...")
        for _ in range(0, (int(str(timeout))+10)):
            time.sleep(1)
            sys.stderr.write(".")
        sys.stderr.write(u"\nError: Could not authenticate. Invalid " \
                         "credentials, or bad username/password.\n")

    def bios_unregistered_error(self):
        """ Called when ilo/bios unregistered error occurs """
        sys.stderr.write(u"\nERROR 100: Bios provider is unregistered. Please" \
        " refer to the documentation for details on this issue.\n")

    def error(self, msg, inner_except=None):
        """ Used for general error handling

        :param inner_except: raised exception to be logged
        :type inner_except: exception.
        """
        LOGGER.error(msg)
        if inner_except is not None:
            LOGGER.error(inner_except)

    def warn(self, msg, inner_except=None):
        """ Used for general warning handling

        :param inner_except: raised exception to be logged
        :type inner_except: exception.
        """
        LOGGER.warn(msg)
        if inner_except is not None:
            LOGGER.warn(inner_except)

    def printmsg(self, excp):
        """ Used for general print out handling """
        sys.stderr.write(u"%s\n" % excp)

    def retries_exhausted_attemps(self):
        """ Called when url retries have been exhausted """
        sys.stderr.write(u"\nError: Could not reach URL. Retries have been" \
                         " exhausted.\n")

    def print_out_json(self, content):
        """ Print out json content to std.out

        :param content: content to be printed out
        :type content: str.
        """
        sys.stdout.write(json.dumps(content, indent=2, \
                                                cls=redfish.ris.JSONEncoder))
        sys.stdout.write('\n')

    def print_out_json_ordered(self, content):
        """ Print out sorted json content to std.out

        :param content: content to be printed out
        :type content: str.
        """
        content = OrderedDict(sorted(content.items(), key=lambda x: x[0]))
        sys.stdout.write(json.dumps(content, indent=2, \
                                                cls=redfish.ris.JSONEncoder))
        sys.stdout.write('\n')

    def print_out_human_readable(self, content):
        """ Print out human readable content to std.out

        :param content: content to be printed out
        :type content: str.
        """
        self.pretty_human_readable(content, enterloop=True)
        sys.stdout.write('\n')

    def pretty_human_readable(self, content, indent=0, start=0, enterloop=False):
        """ Convert content to human readable and print out to std.out

        :param content: content to be printed out
        :type content: str.
        :param indent: indent string to be used as seperator
        :type indent: str.
        :param start: used to determine the indent level
        :type start: int.
        """
        space = '\n' + '\t' * indent + ' ' * start
        if isinstance(content, list):
            for item in content:
                if item is None:
                    continue

                self.pretty_human_readable(item, indent, start)

                if content.index(item) != (len(content) - 1):
                    sys.stdout.write(space)
        elif isinstance(content, dict):
            for key, value in content.iteritems():
                if space and not enterloop:
                    sys.stdout.write(space)

                enterloop=False
                sys.stdout.write(str(key) + '=')
                self.pretty_human_readable(value, indent,
                                           (start + len(key) + 2))
        else:
            content = content if isinstance(content, basestring) \
                                                            else str(content)

            content = '""' if len(content) == 0 else content
            sys.stdout.write(content.encode('utf-8'))

