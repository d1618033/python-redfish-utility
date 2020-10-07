::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to start directory  ::
::               test on following device:                         ::
::                 Integrated Lights-Out 5 (iLO 5)                 ::

:: Directory tests enable you to validate the configured directory ::
:: settings. The directory test results are reset when directory   ::
:: settings are saved, or when the directory tests are started.    ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        values with values that are appropriate for your         ::
::        environment.                                             ::

::        Firmware support information for this script:            ::
::            iLO 5 - All versions                                 ::
 

@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest directory test start -u USER_LOGIN -p PASSWORD
ilorest logout
goto :exit

:remote
ilorest directory test start --url=%1 --user %2 --password %3
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Start_Directory_Test.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Start_Directory_Test.bat

:exit