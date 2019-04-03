::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to update the       ::
::               language pack of following devices:               ::
::                 Integrated Lights-Out 4 (iLO 4)                 ::
::                 Integrated Lights-Out 5 (iLO 5)                 ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        values with values that are appropriate for your         ::
::        environment and you will need to change the value of the ::
::        component=\lpk to point to the language pack you wish to ::
::        use for the language pack update.                        ::

::        Firmware support information for this script:            ::
::            iLO 5 - All versions                                 ::
::            iLO 4 - 1.20 or later.                               ::

@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest login -u USER_LOGIN -p PASSWORD
ilorest uploadcomp --component=C:\lang_ja_130.lpk --update_target
ilorest logout
goto :exit
:remote
ilorest login %1 --user %2 --password %3
ilorest uploadcomp --component=C:\lang_ja_130.lpk --update_target
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Update_Language.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Update_Language.bat

:exit