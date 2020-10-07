::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to eject virtual    ::
::               media                                             ::

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
::Id specifies the Virtual Media device target. The possible values::
:: are 1 or 2. 1 is for Floppy or USBStick and 2 is for CD DVD.    ::
ilorest virtualmedia Id --remove -u USER_LOGIN -p PASSWORD
ilorest logout
goto :exit
:remote
::Id specifies the Virtual Media device target. The possible values::
:: are 1 or 2. 1 is for Floppy or USBStick and 2 is for CD DVD.    ::
ilorest virtualmedia Id --remove --url=%1 -u %2 -p %3
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Eject_Virtual_Media.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Eject_Virtual_Media.bat

:exit