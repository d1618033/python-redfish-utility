#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to toggle the power  #
#               on the host server in which one of the following  #
#               devices is executing:                             #
#                 Integrated Lights-Out 5 (iLO 5)                 #
#                 Integrated Lights-Out 4 (iLO 4)                 #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        This script will use the ACPI Power Button function to   #
#        attempt to gracefully shutdown the host operating system #
#        (if your OS supports and is configured for graceful      #
#        shutdown) before it powers off the server.               #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - All versions.                                #

runLocal(){
  ilorest reboot PushPowerButton -u USER_LOGIN -p PASSWORD
  ilorest logout
}

runRemote(){
  ilorest reboot PushPowerButton --url=$1 --user $2 --password $3
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Set_Host_Power.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Set_Host_Power.sh"
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