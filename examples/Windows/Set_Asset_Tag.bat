::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to set the asset    ::
::               tag, asset tag limited to 32 characters.          ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        values with values that are appropriate for your         ::
::        environment.                                             ::

::        Firmware support information for this script:            ::
::            iLO 5 - All versions                                 ::
::            iLO 4 - 1.05 or later.                               ::

@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest select Bios.
:: Enter a string to set the asset tag, or an empty string         ::
:: to clear the asset tag.                                         ::
ilorest set ServerAssetTag="Asset Tag" 
ilorest commit 
ilorest logout
goto :exit
:remote
ilorest select Bios. --url=%1 -u %2 -p %3
:: Enter a string to set the asset tag, or an empty string         ::
:: to clear the asset tag.                                         ::
ilorest set ServerAssetTag="Asset Tag"
ilorest commit
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Set_Asset_Tag.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Set_Asset_Tag.bat

:exit