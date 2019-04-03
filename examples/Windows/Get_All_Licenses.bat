::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to get the license  ::
::               information.                                      ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        and other values inside the quotation marks with values  ::
::        that are appropriate for your environment.               ::

::        Firmware support information for this script:            ::
::            iLO 5 - All versions                                 ::
::            iLO 4 - version 1.20 and above                       ::

@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest get License --selector=iLOLicense.  -u USER_LOGIN -p PASSWORD
ilorest logout
goto :exit
:remote
ilorest get License --selector=iLOLicense.  --url=%1 -u %2 -p %3
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Get_All_Licenses.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Get_All_Licenses.bat

:exit