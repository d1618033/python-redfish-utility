::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to configure the    ::
::         virtual media port functionality on iLO.                ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        and other values inside the quotation marks with values  ::
::        that are appropriate for your environment.               ::

:: Help:                                                           ::
:: VirutalMedia/Port=:                                             ::
::       The VirutalMedia/Port= value specifies TCP port number    ::
::       on which Virtual Media Service listens. Change of port    ::
::       value results in reset of iLO.                            ::

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
ilorest select ManagerNetworkProtocol. -u USER_LOGIN -p PASSWORD
ilorest set VirutalMedia/Port=17988
ilorest commit
ilorest logout
goto :exit

:remote
ilorest select ManagerNetworkProtocol. --url %1 --user %2 --password %3
ilorest set VirutalMedia/Port=17988
ilorest commit
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Mod_VM_Port_Settings.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Mod_VM_Port_Settings.bat

:exit