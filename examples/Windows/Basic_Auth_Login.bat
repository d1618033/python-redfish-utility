::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample bash script to test login        ::
::               on the following devices:                         ::
::                 Integrated Lights-Out 5 (iLO 5)                 ::
::                 Integrated Lights-Out 4 (iLO 4)                 ::

:: NOTE:  Verbose flag added for visibility                        ::
:: NOTE:  Authentication is not performed in production mode       ::
::        (default); if a username and password are included then  ::
::        the configuration will default to an internal,           ::
::        unauthenticated user account. Higher security modes,     ::
::        if configured, require a valid iLO management username   ::
::        and password to connect.                                 ::

::        Firmware support information for this script:            ::
::            iLO 4 and 5 - All versions                           ::

@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest login -v
ilorest logout
goto :exit
:remote
ilorest login -v --url=%1 --user %2 --password %3
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Basic_Auth_Login.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Basic_Auth_Login.bat

:exit