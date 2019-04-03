#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to return current    #
#               global settings.                                  #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #

runLocal(){
  ilorest --nologo login -u USER_LOGIN -p PASSWORD
  ilorest --nologo get Oem/Hpe/IdleConnectionTimeoutMinutes Oem/Hpe/iLOFunctionalityEnabled Oem/Hpe/RIBCLEnabled Oem/Hpe/WebGuiEnabled GraphicalConsole/ServiceEnabled Oem/Hpe/SerialCLIStatus Oem/Hpe/SerialCLIStatus Oem/Hpe/iLOIPduringPOSTEnabled Oem/Hpe/iLORBSUEnabled Oem/Hpe/VSPDlLoggingEnabled --selector=Manager.
  ilorest --nologo get Oem/Hpe/MinPasswordLength Oem/Hpe/AuthFailureLoggingThreshold Oem/Hpe/AuthFailureDelayTimeSeconds Oem/Hpe/AuthFailuresBeforeDelay --selector=AccountService.
  ilorest --nologo get IPMI/ProtocolEnabled Oem/Hpe/RemoteSyslogEnabled Oem/Hpe/RemoteSyslogPort Oem/Hpe/RemoteSyslogServer Oem/Hpe/AlertMailEnabled Oem/Hpe/AlertMailEmail Oem/Hpe/AlertMailSenderDomain Oem/Hpe/AlertMailSMTPPort Oem/Hpe/AlertMailSMTPServer VirtualMedia/ProtocolEnabled HTTPS/Port HTTP/Port KVMIP/Port VirtualMedia/Port SNMP/ProtocolEnabled SNMP/Port Oem/Hpe/SNMPtrapPort SSH/Port SSH/ProtocolEnabled IPMI/Port --selector=ManagerNetworkProtocol.
  ilorest --nologo get PropagateTimeToHost --selector=DateTime.
  ilorest --nologo logout
}

runRemote(){
  ilorest --nologo login -u USER_LOGIN -p PASSWORD
  ilorest --nologo get Oem/Hpe/IdleConnectionTimeoutMinutes Oem/Hpe/iLOFunctionalityEnabled Oem/Hpe/RIBCLEnabled Oem/Hpe/WebGuiEnabled GraphicalConsole/ServiceEnabled Oem/Hpe/SerialCLIStatus Oem/Hpe/SerialCLIStatus Oem/Hpe/iLOIPduringPOSTEnabled Oem/Hpe/iLORBSUEnabled Oem/Hpe/VSPDlLoggingEnabled --selector=Manager.
  ilorest --nologo get Oem/Hpe/MinPasswordLength Oem/Hpe/AuthFailureLoggingThreshold Oem/Hpe/AuthFailureDelayTimeSeconds Oem/Hpe/AuthFailuresBeforeDelay --selector=AccountService.
  ilorest --nologo get IPMI/ProtocolEnabled Oem/Hpe/RemoteSyslogEnabled Oem/Hpe/RemoteSyslogPort Oem/Hpe/RemoteSyslogServer Oem/Hpe/AlertMailEnabled Oem/Hpe/AlertMailEmail Oem/Hpe/AlertMailSenderDomain Oem/Hpe/AlertMailSMTPPort Oem/Hpe/AlertMailSMTPServer VirtualMedia/ProtocolEnabled HTTPS/Port HTTP/Port KVMIP/Port VirtualMedia/Port SNMP/ProtocolEnabled SNMP/Port Oem/Hpe/SNMPtrapPort SSH/Port SSH/ProtocolEnabled IPMI/Port --selector=ManagerNetworkProtocol.
  ilorest --nologo get PropagateTimeToHost --selector=DateTime.
  ilorest --nologo logout
}

error(){
  echo "Usage:"
  echo        "remote: Get_Global.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Get_Global.sh"
}

if [ "$#" -eq "3" ]
then 
  runRemote "$1" "$2" "$3"
elif [ "$#" -eq "0" ]
then
  runLocal
else
  error
fi