::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to set the          ::
::               persistent mouse and keyboard.                    ::

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
ilorest select Manager. -u USER_LOGIN -p PASSWORD
ilorest set Oem/Hpe/PersistentMouseKeyboardEnabled=False
ilorest commit
ilorest logout
goto :exit
:remote
ilorest select Manager. --url=%1 -u %2 -p %3
ilorest set Oem/Hpe/PersistentMouseKeyboardEnabled=False
ilorest commit
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Set_Persmouse_Status.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Set_PersMouse_Status.bat

:exit