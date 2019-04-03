::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to start director   ::
::               test on following device:                         ::
::                 Integrated Lights-Out 4 (iLO 4)                 ::
::                 Integrated Lights-Out 5 (iLO 5)                 ::

:: Directory tests enable you to validate the configured directory ::
:: settings. The directory test results are reset when directory   ::
:: settings are saved, or when the directory tests are started.    ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        values with values that are appropriate for your         ::
::        environment.                                             ::

::        Firmware support information for this script:            ::
::            iLO 5 - All versions                                 ::
::            iLO 4 - v2.40 onwards                                ::

@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest select RemoteSupport. -u USER_LOGIN -p PASSWORD
ilorest set ProxySettings/Url=Web_Proxy_Server_Hostname_or_IP_address
ilorest set ProxySettings/Port=Web_Proxy_Server_Port
:: If your web proxy requires authentication,                      :: 
::  use the following ProxySettings/Username=,                     ::
::  and ProxySettings/Password= tags.                              ::
::ilorest set ProxySettings/Username=Web_Proxy_Server_Username
::ilorest set ProxySettings/Password=Web_Proxy_Server_Password
ilorest logout
goto :exit
:remote
ilorest select RemoteSupport. --url=%1 -u %2 -p %3
ilorest set ProxySettings/Url=Web_Proxy_Server_Hostname_or_IP_address
ilorest set ProxySettings/Port=Web_Proxy_Server_Port
:: If your web proxy requires authentication,                      :: 
::  use the following ProxySettings/Username=,                     ::
::  and ProxySettings/Password= tags.                              ::
::ilorest set ProxySettings/Username=Web_Proxy_Server_Username
::ilorest set ProxySettings/Password=Web_Proxy_Server_Password
goto :exit

:error
echo Usage:
echo        remote: ERS_DC_SetWebProxy.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  ERS_DC_SetWebProxy.bat

:exit