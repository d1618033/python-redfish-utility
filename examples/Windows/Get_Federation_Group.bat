::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to retrieve the     ::
::               privileges granted to a specified Federation      ::
::               group.                                            ::

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
ilorest select iLOFederationGroup. -u USER_LOGIN -p PASSWORD
ilorest get Privileges --filter Id=DEFAULT
ilorest logout
goto :exit
:remote
ilorest select iLOFederationGroup. --url=%1 --user %2 --password %3
ilorest get Privileges --filter Id=DEFAULT
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Get_Federation_Group.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Get_Federation_Group.bat

:exit