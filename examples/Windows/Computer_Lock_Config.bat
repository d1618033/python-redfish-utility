::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014-2020 Hewlett Packard Enterprise Development LP ::

:: Description: This a sample batch script to configure Computer   ::
::              Lock settings on:                                  ::
::                 Integrated Lights-Out 5 (iLO 5)                 ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        and other values inside the quotation marks with values  ::
::        that are appropriate for your environment.               ::

::        Modification of Computer Lock settings requires Configure::
::        iLO privilege.                                           ::

::        Firmware support information for this script:            ::
::            iLO 5 - All versions                                 ::


@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest select Manager. -u USER_LOGIN -p PASSWORD
:: To set default Windows Computer Lock keys combination:          ::
ilorest set Oem/Hpe/IntegratedRemoteConsole/LockKey/LockOption=Windows

:: To configure custom Computer Lock keys combination uncomment    ::
:: the lines below.                                                ::
::ilorest set Oem/Hpe/IntegratedRemoteConsole/LockKey/LockOption=Custom
::ilorest set Oem/Hpe/IntegratedRemoteConsole/LockKey/CustomKeySequence="[L_GUI,l,NONE,NONE,NONE]"

:: To disable Computer Lock feature:                               ::
::ilorest set Oem/Hpe/IntegratedRemoteConsole/LockKey/LockOption=Disabled
ilorest commit
ilorest logout
goto :exit
:remote
ilorest select Manager. --url=%1 --user %2 --password %3
:: To set default Windows Computer Lock keys combination:          ::
ilorest set Oem/Hpe/IntegratedRemoteConsole/LockKey/LockOption=Windows

:: To configure custom Computer Lock keys combination uncomment    ::
:: the lines below.                                                ::
::ilorest set Oem/Hpe/IntegratedRemoteConsole/LockKey/LockOption=Custom
::ilorest set Oem/Hpe/IntegratedRemoteConsole/LockKey/CustomKeySequence="[L_GUI,l,NONE,NONE,NONE]"

:: To disable Computer Lock feature:                               ::
::ilorest set Oem/Hpe/IntegratedRemoteConsole/LockKey/LockOption=Disabled
ilorest commit
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Computer_Lock_Config.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Computer_Lock_Config.bat

:exit
