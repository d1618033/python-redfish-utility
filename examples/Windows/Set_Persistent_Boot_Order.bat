::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014-2020 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample batch script to Set Persistent   ::
::               Boot Order.                                       ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        and other values inside the quotation marks with values  ::
::        that are appropriate for your environment.               ::

::        This will take one or more boot devices from cdrom,      ::
::        floppy, hdd, usb, or network. If you do not list every   ::
::        option, the remaining options will be shifted towards    ::
::        the bottom of the list.                                  ::

::        Firmware support information for this script:            ::
::            iLO 5 - All versions                                 ::
::            iLO 4 - All versions. UEFI support added 1.40        ::

::        iLO 4 version 1.40 or later                              ::
::          Continuous and one time boot options:                  ::
::              1.      None                                       ::
::              2.      Cd                                         ::
::              3.      Hdd                                        ::
::              4.      Usb                                        ::
::              5.      Utilities                                  ::
::              6.      Diags                                      ::
::              7.      BiosSetup                                  ::
::              8.      Pxe                                        ::
::              9.      UefiShell                                  ::
::              10.     UefiTarget                                 ::

::        iLO 5 all versions:                                      ::
::          Continuous and one time boot options:                  ::
::              1.      None                                       ::
::              2.      Cd                                         ::
::              3.      Hdd                                        ::
::              4.      Usb                                        ::
::              5.      SDCard                                     ::
::              6.      Utilities                                  ::
::              7.      Diags                                      ::
::              8.      BiosSetup                                  ::
::              9.      Pxe                                        ::
::              10.     UefiShell                                  ::
::              11.     UefiHttp                                   ::
::              12.     UefiTarget                                 ::

::      Assignment of Boot device names varies from system to      ::
::        system and may change when the system reboots. Execute   ::
::        Get_Persistent_Boot_Order.bat to determine the current   ::
::        Boot device assignments on your system, and choose       ::
::        from those for the DEVICE values in SET_PERSISTENT_BOOT. ::

::      Note: FLOPPY drive boot is not supported from Gen9 onwards ::
::            in Legacy and UEFI modes                             ::

@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest login -u USER_LOGIN -p PASSWORD
ilorest bootorder [1,2,6] --commit
ilorest logout
goto :exit
:remote
ilorest login %1 -u %2 -p %3
ilorest bootorder [1,2,6] --commit
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Set_Persistent_Boot_Order.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Set_Persistent_Boot_Order.bat

:exit
