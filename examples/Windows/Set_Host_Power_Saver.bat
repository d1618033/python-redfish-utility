::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to set the Power    ::
::               Regulator feature on the host server in           ::
::               Integrated Lights-Out(iLO).                       ::

::               The values are:                                   ::
::               OsControl = OS Control Mode(Disabled Mode for iLO)::
::               StaticLowPower = Static Low Power Mode            ::
::               DynamicPowerSavings = Dynamic Power Savings Mode  ::
::               StaticHighPerf= Static High Performance Mode      ::

::               Some servers only support subset of the           ::
::               values.                                           ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        values with values that are appropriate for your         ::
::        environment.                                             ::


::        Firmware support information for this script:            ::
::            iLO 5 - All versions                                 ::
::            iLO 4 - All versions                                 ::

@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest select Bios. -u USER_LOGIN -p PASSWORD
ilorest set PowerRegulator=DynamicPowerSavings 
ilorest commit
ilorest logout
goto :exit
:remote
ilorest select Bios. --url=%1 -u %2 -p %3
ilorest set PowerRegulator=DynamicPowerSavings 
ilorest commit
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Set_Host_Power_Saver.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Set_Host_Power_Saver.bat

:exit