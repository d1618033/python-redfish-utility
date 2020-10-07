::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script that configures the ::
::               iLO Shared Network Port with a user defined VLAN  ::
::               ID.                                               ::

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
ilorest select EthernetInterface. -u USER_LOGIN -p PASSWORD
ilorest set Oem/Hpe/NICEnabled=True
ilorest set Oem/Hpe/SharedNetworkPortOptions/NIC=FlexibleLOM
ilorest set VLAN/VLANEnable=True
ilorest set VLAN/VLANDId=1
ilorest commit
ilorest logout
goto :exit

:remote
ilorest select EthernetInterface. --url %1 --user %2 --password %3
ilorest set Oem/Hpe/NICEnabled=True
ilorest set Oem/Hpe/SharedNetworkPortOptions/NIC=FlexibleLOM
ilorest set VLAN/VLANEnable=True
ilorest set VLAN/VLANDId=1
ilorest commit
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Mod_VLAN.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Mod_VLAN.bat

:exit