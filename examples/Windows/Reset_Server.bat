::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to power cycle (off ::
::               and then back on) the host server in which the    ::
::               Integrated Lights-Out(iLO) is operating.          ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        values with values that are appropriate for your         ::
::        environment.                                             ::

::        This script will NOT attempt to gracefully shutdown the  ::
::        host operating system before it powers off the server.   ::

::        If graceful shutdown is needed (if your OS supports it), ::
::        use the Set_Host_Power.bat script to attempt a graceful  ::
::        shutdown of the OS before powering off the server and    ::
::        then use the Set_Host_Power.bat scrip again to turn the  ::
::        server back on.                                          ::

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
ilorest reboot ForceRestart -u USER_LOGIN -p PASSWORD
ilorest logout
goto :exit
:remote
ilorest reboot ForceRestart --url=%1 -u %2 -p %3
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Reset_Server.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Reset_Server.bat

:exit