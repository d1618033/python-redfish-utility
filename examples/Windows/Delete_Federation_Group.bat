::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to delete a         ::
::               Federation group membership on the following      ::
::               devices:                                          ::
::                 Integrated Lights-Out 4 (iLO 4)                 ::
::                 Integrated Lights-Out 5 (iLO 5)                 ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        and other values inside the quotation marks with         ::
::        values that are appropriate for your environment.        ::

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
ilorest ilofederation delete federationname
ilorest logout
goto :exit
:remote
ilorest ilofederation delete federationname --url=%1 --user %2 --password %3
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Delete_Federation_Group.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Delete_Federation_Group.bat

:exit