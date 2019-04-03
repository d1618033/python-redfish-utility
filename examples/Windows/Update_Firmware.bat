::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to update the       ::
::               Integrated Lights-Out(iLO) firmware.              ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        values with values that are appropriate for your         ::
::        environment and you will need to change the value of the ::
::        IMAGE_LOCATION to point to the new binary firmware image ::
::        you wish to use for the firmware update.                 ::
::        The Unit ID light flashes when the server is engaged in  ::

::        an activity that can not or should not be interrupted    ::
::        (such as updating iLO firmware or an active Remote       ::
::        Console session).  The Unit ID light should flash while  ::
::        this script is updating the firmware.                    ::
::        The Lights-Out device will automatically reset itself to ::
::        have the new firmware take effect at the end of the      ::
::        firmware flash.                                          ::

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
ilorest login -u USER_LOGIN -p PASSWORD
ilorest firmwareupdate https://IMAGE_LOCATION.bin
::  Use the line below instead if your server uses TPM:            ::
::ilorest firmwareupdate https://IMAGE_LOCATION.bin --tpmenabled -u USER_LOGIN -p PASSWORD
ilorest logout
goto :exit
:remote
ilorest login %1 -u %2 -p %3
ilorest firmwareupdate https://IMAGE_LOCATION.bin
::  Use the line below instead if your server uses TPM:            ::
::ilorest firmwareupdate https://IMAGE_LOCATION.bin --tpmenabled --url=%1 -u %2 -p %3
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Update_Firmware.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Update_Firmware.bat

:exit