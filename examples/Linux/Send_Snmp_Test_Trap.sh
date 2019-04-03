#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample batch script to send a test      #
# SNMP trap to the alert destinations configured for the iLO      #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - version 2.10 or later.                       #

runLocal(){
  ilorest sendtest snmpalert -u USER_LOGIN -p PASSWORD
  ilorest logout
}

runRemote(){
  ilorest sendtest snmpalert --url=$1 --user $2 --password $3
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Send_Snmp_Test_Trap.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Send_Snmp_Test_Trap.sh"
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