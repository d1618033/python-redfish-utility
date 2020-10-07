::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to modify a         ::
::               Federation group membership and associated        ::
::               privileges on Integrated Lights-Out(iLO).         ::
:: NOTE:  Some privileges may not be configurable based on the     ::
::        logged in user's privileges.

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        and other values inside the quotation marks with         ::
::        values that are appropriate for your environment.        ::

::        You might need to tailor this script for the firmware    ::
::        running on your Lights-Out device according to the       ::
::        information in "Firmware support information" comment(s).::

::        Firmware support information for this script:            ::
::            iLO 5 - All versions                                 ::
::            iLO 4 - 1.40 or later.                               ::

@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest select FederationGroup. -u USER_LOGIN -p PASSWORD
:: Set a variable as the group name to be used as a filter.        ::
set groupname="groupname"
:: The following settings tags are all optional. Any Federation    ::
::property not explicitly modified below will retain its old value.::
ilorest set Name=newgroupname --filter Id=%groupname%
ilorest set Key=newgroupkey --filter Id=%groupname%
ilorest set Privileges/HostBIOSConfigPriv=True --filter Id=%groupname%
ilorest set Privileges/HostNICConfigPriv=True --filter Id=%groupname%
ilorest set Privileges/HostStorageConfigPriv=True --filter Id=%groupname%
ilorest set Privileges/LoginPriv=True --filter Id=%groupname%
ilorest set Privileges/RemoteConsolePriv=True --filter Id=%groupname%
ilorest set Privileges/SystemRecoveryConfigPriv=True --filter Id=%groupname%
ilorest set Privileges/UserConfigPriv=True --filter Id=%groupname%
ilorest set Privileges/VirtualMediaPriv=True --filter Id=%groupname%
ilorest set Privileges/VirtualPowerAndResetPriv=True --filter Id=%groupname%
ilorest set Privileges/iLOConfigPriv=True --filter Id=%groupname%
ilorest commit
ilorest logout
goto :exit
:remote
ilorest select FederationGroup. --url=%1 -u %2 -p %3
:: set a variable as the group name to be used as a filter.        ::
set groupname="groupname"
:: The following settings tags are all optional. Any Federation    ::
::property not explicitly modified below will retain its old value.::
ilorest set Name=newgroupname --filter Id=%groupname%
ilorest set Key=newgroupkey --filter Id=%groupname%
ilorest set Privileges/HostBIOSConfigPriv=True --filter Id=%groupname%
ilorest set Privileges/HostNICConfigPriv=True --filter Id=%groupname%
ilorest set Privileges/HostStorageConfigPriv=True --filter Id=%groupname%
ilorest set Privileges/LoginPriv=True --filter Id=%groupname%
ilorest set Privileges/RemoteConsolePriv=True --filter Id=%groupname%
ilorest set Privileges/SystemRecoveryConfigPriv=True --filter Id=%groupname%
ilorest set Privileges/UserConfigPriv=True --filter Id=%groupname%
ilorest set Privileges/VirtualMediaPriv=True --filter Id=%groupname%
ilorest set Privileges/VirtualPowerAndResetPriv=True --filter Id=%groupname%
ilorest set Privileges/iLOConfigPriv=True --filter Id=%groupname%
ilorest commit
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Mod_Federation_Group.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Mod_Federation_Group.bat

:exit