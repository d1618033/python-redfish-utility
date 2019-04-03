::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to enable or disable::
::               AHS logging.                                      ::

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
ilorest select ActiveHealthSystem
:: Possible Values: Set to "Enable" or "False". ::
ilorest set AHSEnabled=True --commit 
ilorest logout
goto :exit
:remote
ilorest select ActiveHealthSystem --url=%1 -u %2 -p %3
:: Possible Values: Set to "True" or "False". ::
ilorest set AHSEnabled=True --commit 
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Set_Boot_Mode.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Set_Boot_Mode.bat

:exit