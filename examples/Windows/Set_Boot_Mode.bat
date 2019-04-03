::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description: This is a sample batch script to set the pending   ::
::              boot mode.                                         ::

::        Firmware support information for this script:            ::
::            iLO 5 - All versions                                 ::
::            iLO 4 - version 1.40 or later.                       ::

@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest select Bios.
:: Possible Values: LegacyBios or Uefi ::
ilorest set BootMode=Uefi
ilorest commit
ilorest logout
goto :exit
:remote
ilorest select Bios. --url=%1 -u %2 -p %3
:: Possible Values: LegacyBios or Uefi ::
ilorest set BootMode=Uefi
ilorest commit
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Set_Boot_Mode.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Set_Boot_Mode.bat

:exit