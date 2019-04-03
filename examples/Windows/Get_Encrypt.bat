::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to return current   ::
::               encryption settings.                              ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        values with values that are appropriate for your         ::
::        environment.                                             ::

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
ilorest list --selector=SmartStorageArrayController. -u USER_LOGIN -p PASSWORD
ilorest logout
goto :exit
:remote
ilorest list --selector=SmartStorageArrayController. --url=%1 -u %2 -p %3
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Get_Encrypt.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Get_Encrypt.bat

:exit