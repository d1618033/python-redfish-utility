::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description: This is a sample batch script to set the default   ::
::              Administrator account password using iLOREST.EXE.  ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        and other values inside the quotation marks with values  ::
::        that are appropriate for your environment.               ::

::        Use this script with iLOREST to install a known password ::
::        for the Administrator account.  iLOREST requires that you::
::        log into Windows or Linux with administrator or root     ::
::        credentials.                                             ::

::        Note that this assumes that there is an Administrator    ::
::        account because it is not intended to create one.  The   ::
::        LOGIN credentials are ignored when used with HPONCFG.    ::

::        After this script has been used successfully with iLOREST::
::        you may login using the credentials: "Administrator" and ::
::        "password".                                              ::

::        Firmware support information for this script:            ::
::            iLO 5 - All versions.                                ::
::            iLO 4 - All versions.                                ::
@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest iloaccounts changepass Administrator password
ilorest logout
goto :exit
:remote
ilorest iloaccounts changepass Administrator password --url=%1 --user %2 --password %3
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Administrator_reset_pw.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Administrator_reset_pw.bat

:exit