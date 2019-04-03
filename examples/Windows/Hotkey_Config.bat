::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to configure a set  ::
::               of Remote Console hot-keys for iLO.               ::

::               You will need to change the values in 
::               Hotkey_Config.json to match the values you want   ::
::               to apply.

::        The KeySequence order in the HotKey_Config.json is:      ::
::        Name=Ctrl-T, Name=Ctrl-U, Name=Ctrl-V, Name=Ctrl-W,      ::
::        Name=Ctrl-X, and Name=Ctrl-Y                             ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        and other values inside the quotation marks with values  ::
::        that are appropriate for your environment.               ::

::        Firmware support information for this script:            ::
::            iLO 5 - All versions                                 ::

@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest rawpatch Hotkey_Config.json -u USER_LOGIN -p PASSWORD
ilorest logout
goto :exit
:remote
ilorest rawpatch Hotkey_Config.json --url %1 --user %2 --password %3
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Hotkey_Config.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  HotkeyConfig.bat

:exit