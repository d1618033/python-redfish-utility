::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to apply the license::
::               key for the Integrated Lights-Out Advanced Pack.  ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        values with values that are appropriate for your         ::
::        environment.                                             ::

::        You will need to replace the sample value for the KEY    ::
::        with the value from your iLO Advanced Pack.              ::
::        The iLO Advanced Pack is licensed to a single server.    ::
::        You may not use the same individual license key on more  ::
::        than one server.                                         ::

::        Contact your Account Representative for information on   ::
::        Volume Licensing or Master License Agreements if you     ::
::        want to use the same key for multiple servers.           ::

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
ilorest ilolicense XXXXX-XXXXX-XXXXX-XXXXX-XXXXX -u USER_LOGIN -p PASSWORD
ilorest logout
goto :exit
:remote
ilorest ilolicense XXXXX-XXXXX-XXXXX-XXXXX-XXXXX --url=%1 -u %2 -p %3
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: License.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  License.bat

:exit