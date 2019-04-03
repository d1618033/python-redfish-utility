::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description: This a sample batch script to add an HPE SIM Single::
::              Sign-On (SSO) server record to the end of the      ::
::              database on:                                       ::
::                 Integrated Lights-Out 4 (iLO 4)                 ::
::                 Integrated Lights-Out 5 (iLO 5)                 ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        and other values inside the quotation marks with values  ::
::        that are appropriate for your environment.               ::

::        There are three alternatives to perform this operation:  ::
::        1) Add record by name.                                   ::
::        2) Add record by indirect import.                        ::
::        3) Add record by direct certificate import.              ::

::        HPE SIM Single Sign-On requires iLO Advanced or iLO      ::
::        Select license.                                          ::

::        Modification of SSO settings requires Configure iLO      ::
::        privilege.                                               ::

::        Firmware support information for this script:            ::
::            iLO 5 - All versions                                 ::
::            iLO 4 - All versions                                 ::

:: There are three alternatives to add an SSO server record,       ::
:: shown below. To use them, un-comment the desired                ::
:: implementation and populate the appropriate data.               ::

@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest login -u USER_LOGIN -p PASSWORD
:: Alternative 1: add an HPE SIM SSO server record by              ::
::                indirect import. iLO indirectly imports the      ::
::                encoded certificate by requesting it from        ::
::                the specified network name.                      ::
ilorest singlesignon importdns hpesim01.hpe.net
:: Alternative 2: add an HPE SIM SSO server record by direct       ::
::                certificate import. The x.509 DER encoded        ::
::                certificate data you specify is added by         ::
::                iLO.                                             ::
::ilorest singlesignon importcert cert.txt
ilorest logout
goto :exit
:remote
ilorest login --url=%1 --user %2 --password %3
:: Alternative 1: add an HPE SIM SSO server record by              ::
::                indirect import. iLO indirectly imports the      ::
::                encoded certificate by requesting it from        ::
::                the specified network name.                      ::
ilorest singlesignon importdns hpesim01.hpe.net
:: Alternative 2: add an HPE SIM SSO server record by direct       ::
::                certificate import. The x.509 DER encoded        ::
::                certificate data you specify is added by         ::
::                iLO.                                             ::
::ilorest singlesignon importcert cert.txt
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: add_sso_rec.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  add_sso_rec.bat

:exit