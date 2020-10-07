::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to get LDAP CA      ::
::               certificate status on following device:           ::
::                 Integrated Lights-Out 4 (iLO 4)                 ::
::                 Integrated Lights-Out 5 (iLO 5)                 ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        values with values that are appropriate for your         ::
::        environment.                                             ::

::        Firmware support information for this script:            ::
::            iLO 5 - All versions                                 ::
::            iLO 4 - v2.53 onwards                                ::

@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest select ServiceRoot. -u USER_LOGIN -p PASSWORD
:: The line below is for iLO 5 and up.                             ::
ilorest list Oem/Hpe/Sessions/LDAPAuthLicenced
:: Uncomment the line below is you are using iLO 4.                ::
::ilorest list Oem/Hp/Sessions/LDAPAuthLicenced
ilorest logout
goto :exit
:remote
ilorest select ServiceRoot. --url=%1 --user %2 --password %3
:: The line below is for iLO 5 and up.                             ::
ilorest list Oem/Hpe/Sessions/LDAPAuthLicenced
:: Uncomment the line below is you are using iLO 4.                ::
::ilorest list Oem/Hp/Sessions/LDAPAuthLicenced
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Get_LDAP_CA_Cert_Status.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Get_LDAP_CA_Cert_Status.bat

:exit