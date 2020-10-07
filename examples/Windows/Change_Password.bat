::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to change a user's  ::
::               password in the database of local users on        ::
::               following devices:                                ::
::                 Integrated Lights-Out 4 (iLO 4)                 ::
::                 Integrated Lights-Out 5 (iLO 5)                 ::

:: NOTE:  You will need to replace the values inside the quote     ::
::        marks with values that are appropriate for your          ::
::        environment.                                             ::

@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest iloaccounts changepass "username" "password"
ilorest logout
goto :exit
:remote
ilorest iloaccounts changepass "username" "password" --url=%1 --user %2 --password %3
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Change_Password.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Change_Password.bat

:exit