::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to return           ::
::               enclosure data for c-Class blade infrastructure   ::

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
ilorest select ServiceRoot. -u USER_LOGIN -p PASSWORD
:: The line below is for iLO 5 and up.                             ::
ilorest list Oem/Hpe/Manager/Blade
:: Uncomment the line below is you are using iLO 4.                ::
::ilorest list Oem/Hp/Manager/Blade
ilorest logout
goto :exit
:remote
ilorest select ServiceRoot. --url=%1 --user %2 --password %3
:: The line below is for iLO 5 and up.                             ::
ilorest list Oem/Hpe/Manager/Blade
:: Uncomment the line below is you are using iLO 4.                ::
::ilorest list Oem/Hp/Manager/Blade
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Get_OA_Info.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Get_OA_Info.bat

:exit