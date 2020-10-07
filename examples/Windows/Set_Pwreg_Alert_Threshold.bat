::    RESTful Interface Tool Sample Script for HPE iLO Products    ::
::  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP ::

:: Description:  This is a sample XML script to set the power      ::
::               alert threshold for Integrated Lights-Out(iLO).   ::

::       The Trigger TYPE are:                                     ::
::           "Disabled"                                            ::
::           "PeakPowerConsumption" : Represents the 1/2-seconds   ::
::                    average power reading during the sample      ::
::           "AveragePowerConsumption" : Represents the mean power ::
::                    reading during the sample                    ::

:: NOTE:  You will need to replace the USER_LOGIN and PASSWORD     ::
::        and other values inside the quotation marks with values  ::
::        that are appropriate for your environment.               ::

::        Firmware support information for this script:            ::
::            iLO 5 - All versions                                 ::

@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 3 goto :remote
if %argC% EQU 0 goto :local
goto :error

:local
ilorest select Power. -u USER_LOGIN -p PASSWORD
ilorest set Oem/Hpe/SNMPPowerThresholdAlert/Trigger=PeakPowerConsumption
ilorest set Oem/Hpe/SNMPPowerThresholdAlert/ThresholdWatts=200
ilorest set Oem/Hpe/SNMPPowerThresholdAlert/DurationInMin=35
ilorest commit
ilorest logout
goto :exit
:remote
ilorest select Power. --url %1 --user %2 --password %3
ilorest set Oem/Hpe/SNMPPowerThresholdAlert/Trigger=PeakPowerConsumption
ilorest set Oem/Hpe/SNMPPowerThresholdAlert/ThresholdWatts=200
ilorest set Oem/Hpe/SNMPPowerThresholdAlert/DurationInMin=35
ilorest commit
ilorest logout
goto :exit

:error
echo Usage:
echo        remote: Set_Pwreg_Alert_Threshold.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>
echo        local:  Set_Pwreg_Alert_Threshold.bat

:exit