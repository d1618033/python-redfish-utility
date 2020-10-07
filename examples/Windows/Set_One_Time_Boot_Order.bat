::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP ::

:: Description: This is a sample batch script to Set One Time Boot ::
::                 Order.                                          ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        and other values inside the quotation marks with values  ::
::        that are appropriate for your environment.               ::

::        "None" will set the boot device according to Server      ::
::        Boot Order in iLO GUI.                                   ::

::        iLO 4 version 1.40 or later and iLO 5 all versions:      ::
::        This will take one boot device from "None", "Cd", "Hdd", ::
::        "Usb", "Utilities", "Diags", "BiosSetup", "Pxe",         ::
::        "UefiShell", "UefiTarget".                               ::

::        The following boot options will only work in iLO 5:      ::
::        "SDCard" and "UefiHttp",                                 ::

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
ilorest login -u USER_LOGIN -p PASSWORD
ilorest bootorder --onetimeboot=Utilities
ilorest commit
ilorest logout
goto :exit
:remote
ilorest login %1 -u %2 -p %3
ilorest bootorder --onetimeboot=Utilities
ilorest commit
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Set_One_Time_Boot_Order.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Set_One_Time_Boot_Order.bat

:exit