::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to set the Power    ::
::               Cap feature on the host server.                   ::

::        The power cap values are returned and received in Watts. ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        and other values inside the quotation marks with values  ::
::        that are appropriate for your environment. Your server   ::
::        needs to support power limiting.                         ::

::        Modification of power cap setting requires               ::
::        Configure iLO privilege.                                 ::

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
ilorestselect Power. -u USER_LOGIN -p PASSWORD
ilorest set PowerControl/PowerLimit/LimitInWatts=None
ilorest commit
ilorest logout
goto :exit
:remote
ilorest select Power. --url %1 --user %2 --password %3
ilorest set PowerControl/PowerLimit/LimitInWatts=None
ilorest commit
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Set_PowerCap.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Set_PowerCap.bat

:exit