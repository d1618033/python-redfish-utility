::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP ::

:: Description: This a sample batch script to configure HPE SIM    ::
::              Single Sign-ON (SSO) settings on Integrated        ::
::              Lights-Out(iLO).                                   ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        and other values inside the quotation marks with values  ::
::        that are appropriate for your environment.               ::

::        HPE SIM Single Sign-On requires iLO Advanced or iLO      ::
::        Select license.                                          ::

::        Modification of SSO settings requires Configure iLO      ::
::        privilege.                                               ::

::        Firmware support information for this script:            ::
::            iLO 5 - All versions                                 ::
::            iLO 4 - All Versions                                 ::

@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest select SSO. -u USER_LOGIN -p PASSWORD
:: Specify the desired trust mode value                            ::
::  Options: TrustNone    (default)                                ::
::           TrustbyCert (recommended)                             ::
::           TrustbyName                                           ::
::           TrustAll                                              ::
ilorest set SSOsettings/SSOTrustMode=TrustbyCert

:::: Specify the privileges assigned to the user role              ::
ilorest set SSOsettings/UserPrivilege/LoginPriv=True
ilorest set SSOsettings/UserPrivilege/RemoteConsolePriv=False
ilorest set SSOsettings/UserPrivilege/VirtualPowerAndResetPriv=False
ilorest set SSOsettings/UserPrivilege/VirtualMediaPriv=False
ilorest set SSOsettings/UserPrivilege/iLOConfigPriv=Fls

:: Specify the privileges assigned to the operator role            ::
ilorest set SSOsettings/OperatorPrivilege/LoginPriv=True
ilorest set SSOsettings/OperatorPrivilege/RemoteConsolePriv=True
ilorest set SSOsettings/OperatorPrivilege/VirtualPowerAndResetPriv=True
ilorest set SSOsettings/OperatorPrivilege/VirtualMediaPriv=True
ilorest set SSOsettings/OperatorPrivilege/iLOConfigPriv=False

:: Specify the privileges assigned to the administrator role.      ::
ilorest set SSOsettings/AdminPrivilege/LoginPriv=True
ilorest set SSOsettings/AdminPrivilege/RemoteConsolePriv=True
ilorest set SSOsettings/AdminPrivilege/VirtualPowerAndResetPriv=True
ilorest set SSOsettings/AdminPrivilege/VirutalMediaPriv=True
ilorest set SSOsettings/AdminPrivilege/iLOConfigPriv=True

:: Add an SSO server record using indirect iLO import from         ::
:: the network name.                                               ::
::ilorest singlesignon importdns hpesim01.hpe.net

:: Add an SSO server certificate record using direct iLO           ::
:: import of valid data.                                           ::
::ilorest singlesignon importcert cert.txt
ilorest commit
ilorest logout
goto :exit
:remote
ilorest select SSO. --url=%1 -u %2 -p %3
:: Specify the desired trust mode value                            ::
::  Options: TrustNone    (default)                                ::
::           TrustbyCert (recommended)                             ::
::           TrustbyName                                           ::
::           TrustAll                                              ::
ilorest set SSOsettings/SSOTrustMode=TrustbyCert

:::: Specify the privileges assigned to the user role              ::
ilorest set SSOsettings/UserPrivilege/LoginPriv=True
ilorest set SSOsettings/UserPrivilege/RemoteConsolePriv=False
ilorest set SSOsettings/UserPrivilege/VirtualPowerAndResetPriv=False
ilorest set SSOsettings/UserPrivilege/VirtualMediaPriv=False
ilorest set SSOsettings/UserPrivilege/iLOConfigPriv=Fls

:: Specify the privileges assigned to the operator role            ::
ilorest set SSOsettings/OperatorPrivilege/LoginPriv=True
ilorest set SSOsettings/OperatorPrivilege/RemoteConsolePriv=True
ilorest set SSOsettings/OperatorPrivilege/VirtualPowerAndResetPriv=True
ilorest set SSOsettings/OperatorPrivilege/VirtualMediaPriv=True
ilorest set SSOsettings/OperatorPrivilege/iLOConfigPriv=False

:: Specify the privileges assigned to the administrator role.      ::
ilorest set SSOsettings/AdminPrivilege/LoginPriv=True
ilorest set SSOsettings/AdminPrivilege/RemoteConsolePriv=True
ilorest set SSOsettings/AdminPrivilege/VirtualPowerAndResetPriv=True
ilorest set SSOsettings/AdminPrivilege/VirutalMediaPriv=True
ilorest set SSOsettings/AdminPrivilege/iLOConfigPriv=True

:: Add an SSO server record using indirect iLO import from         ::
:: the network name.                                               ::
::ilorest singlesignon importdns hpesim01.hpe.net

:: Add an SSO server certificate record using direct iLO           ::
:: import of valid data.                                           ::
::ilorest singlesignon importcert cert.txt
ilorest commit
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Mod_SSO_Settings.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Mod_SSO_Settings.bat

:exit