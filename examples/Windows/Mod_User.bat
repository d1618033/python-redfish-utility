::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample bash script to modify an         ::
::               existing password and privileges in the database  ::
::               of iLO users.                                     ::

:: NOTE:  You will need to replace the values inside the script    ::
::        with values that are appropriate for your environment.   ::

::        Either use the accout Username, or the account ID.       ::
::        These values can be found with the iloaccounts command   ::
::        Privileges are referenced with with the numbers listed   ::
::        below.                                                   ::

::                      PRIVILEGES:                                ::
::        1: Login                                                 ::
::        2: Remote Console                                        ::
::        3: User Config                                           ::
::        4: iLO Config                                            ::
::        5: Virtual Media                                         ::
::        6: Virtual Power and Reset                               ::

::        iLO 5 added privileges:                                  ::
::        7: Host NIC Config                                       ::
::        8: Host Bios Config                                      ::
::        9: Host Storage Config                                   ::
::        10: System Recovery Config                               ::

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
ilorest iloaccounts changepass ilousername newpassword
ilorest iloaccounts modify ilousername --addprivs 4,5,6 --removeprivs 2
ilorest logout
goto :exit
:remote
ilorest iloaccounts changepass ilousername newpassword --url %1 --user %2 --password %3 
ilorest iloaccounts modify ilousername --addprivs 4,5,6 --removeprivs 2
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Mod_User.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Mod_User.bat

:exit

