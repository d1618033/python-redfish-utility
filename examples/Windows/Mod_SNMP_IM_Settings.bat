::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to configure the    ::
::               SNMP and Insight Manager integration settings.    ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        and other values inside the quotation marks with values  ::
::        that are appropriate for your environment.               ::

::        Firmware support information for this script:            ::
::            iLO 5 - All versions                                 ::
::            iLO 4 - All versions.                                ::

@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest login -u USER_LOGIN -p PASSWORD
ilorest save --selector=iLOSnmpService. -f snmpsettings.json
echo Change the values that you would like to change in the 'snmpsettings.json' then press Enter.
pause
echo Your changes to the SNMP settings will be uploaded and iLO will restart.
ilorest load -f snmpsettings.json
ilorest logout
goto :exit

:remote
ilorest login %1 --user %2 --password %3
ilorest save --selector=iLOSnmpService. -f snmpsettings.json
echo Change the values that you would like to change in the 'snmpsettings.json' then press Enter.
pause
echo Your changes to the SNMP settings will be uploaded and iLO will restart.
ilorest load -f snmpsettings.json
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Mod_SNMP_IM_Settings.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Mod_SNMP_IM_Settings.bat

:exit