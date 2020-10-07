::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to enable FIPs mode.::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        values with values that are appropriate for your         ::
::        environment.                                             ::

::        All active connections (including Remote Console and     ::
::        Virtual Media sessions) to the Lights-Out device will be ::
::        dropped immediately when this script executes.           ::

::        Firmware support information for this script:            ::
::            iLO 5 - All versions                                 ::
::            iLO 4 - 1.20 or later                                ::

@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest set SecurityState=Production --selector=SecurityService. --commit -u USER_LOGIN -p PASSWORD
ilorest logout
goto :exit
:remote
ilorest set SecurityState=Production --selector=SecurityService. --commit --url=%1 -u %2 -p %3
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Set_FIPS_Enable.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Set_FIPS_Enable.bat

:exit