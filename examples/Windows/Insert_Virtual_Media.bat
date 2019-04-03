::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to insert a virtual ::
::               media image.                                      ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        values with values that are appropriate for your         ::
::        environment. You will also need to replace the           ::
::        http://xx.xx.xx.xx/images/media.iso with the location of ::
::        the virtual media you want to mount.                     ::

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
ilorest virtualmedia 2 http://xx.xx.xx.xx/images/media.iso -u USER_LOGIN -p PASSWORD
ilorest logout
goto :exit
:remote
ilorest virtualmedia 2 http://xx.xx.xx.xx/images/media.iso --url=%1 -u %2 -p %3
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Insert_Virtual_Media.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Insert_Virtual_Media.bat

:exit