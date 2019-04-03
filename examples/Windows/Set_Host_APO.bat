::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to set the automatic::
::               power on and power on delay settings of the       ::
::               server.                                           ::

::               The iLO 4 Version 1.30 or later values and        ::
::               iLO 5 all versions are:                           ::
::         AlwaysPowerOn = APO Always Power On                     ::
::        AlwaysPowerOff = APO Always Remain Off                   ::
::      RestoreLastState = APO Restore Last Power State            ::

:: NOTE: Restore option is the default setting for ML, DL, and     ::
::       SL servers. It is not available on BL servers.            ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        values with values that are appropriate for your         ::
::        environment.                                             ::

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
ilorest select Bios. -u USER_LOGIN -p PASSWORD
ilorest set AutoPowerOn=RestoreLastState
ilorest commit
ilorest logout
goto :exit
:remote
ilorest select Bios. --url=%1 -u %2 -p %3
ilorest set AutoPowerOn=RestoreLastState
ilorest commit
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Set_Host_APO.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Set_Host_APO.bat

:exit