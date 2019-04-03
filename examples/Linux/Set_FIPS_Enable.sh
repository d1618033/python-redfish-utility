#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to enable FIPs mode. #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        All active connections (including Remote Console and     #
#        Virtual Media sessions) to the Lights-Out device will be #
#        dropped immediately when this script executes.           #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - 1.20 or later                                #

runLocal(){
  ilorest set SecurityState=Production --selector=SecurityService. --commit -u USER_LOGIN -p PASSWORD
  ilorest logout
}

runRemote(){
  ilorest set SecurityState=Production --selector=SecurityService. --commit --url=$1 --user $2 --password $3
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Set_FIPS_Enable.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Set_FIPS_Enable.sh"
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