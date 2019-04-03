::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to return data about::
::               the user account named in the GET_USER command.   ::

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
ilorest select ManagerAccount. -u USER_LOGIN -p PASSWORD
:: The line below is for iLO 5                                     ::
ilorest list Oem/Hpe/Privileges --filter UserName=Administator
:: Uncomment the following line for iLO 4                          ::
::ilorest list Oem/Hp/Privileges --filter UserName=Administrator
ilorest logout
goto :exit
:remote
ilorest select ManagerAccount. --url %1 --user %2 --password %3
:: The line below is for iLO 5                                     ::
ilorest list Oem/Hpe/Privileges --filter UserName=Administator
:: Uncomment the following line for iLO 4                          ::
::ilorest list Oem/Hp/Privileges --filter UserName=Administrator
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Get_User.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Get_User.bat

:exit