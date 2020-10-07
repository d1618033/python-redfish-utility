::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to clear AHS        ::
::               data.                                             ::

::        This script was written for iLO 4 firmware version 1.00  ::
::        release.                                                 ::

::        Firmware support information for this script:            ::
::            iLO 4 - All versions.                                ::
::            iLO 5 - All versions.                                ::


@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest serverlogs --selectlog=AHS --clearlog
ilorest logout
goto :exit
:remote
ilorest serverlogs --selectlog=AHS --clearlog --url=%1 --user %2 --password %3
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Clear_AHS_Data.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Clear_AHS_Data.bat

:exit