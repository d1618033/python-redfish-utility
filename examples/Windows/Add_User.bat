::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP ::

::      Description: This is a sample batch script to add an iLO   ::
::                   account to the server either locally or       ::
::                   remotely using the RESTful Interface Tool.    ::

::      Note: In order to use this script remotely include the     ::
::            iLO URL you wish to perform the operation on along   ::
::            with valid iLO credentials for that system in the    ::
::            command line otherwise it will be ran locally.       ::
::            Usage: Add_User.bat 10.0.0.100 username password     ::

::            You will need to replace NEWUSERNAME,                ::
::            NEWACCOUNTNAME, and PASSWORD with values that are    ::
::            appropriate for your environment.                    ::

::            This script was designed to be ran with iLOREST 2.0  ::
::            or greater. Note some account privileges are only    ::
::            available on later iLO firmware versions.            ::

::            Privileges:                                          ::
::                Priv : option                                    ::
::      Firmware supported for iLOREST 2.3 and greater:            ::
::          iLO 4 version 2.10 and greater                         ::
::          iLO 5 all versions                                     ::
::      Firmware supported for iLOREST 2.0 to 2.2:                 ::
::          iLO 4 version 2.00 and greater                         ::
::          iLO 5 all versions                                     ::

@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest iloaccounts add testUser testAccount testPass
ilorest logout
goto :exit
:remote
ilorest iloaccounts add testUser testAccount testPass --url=%1 --user %2 --password %3
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Add_User.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Add_User.bat

:exit