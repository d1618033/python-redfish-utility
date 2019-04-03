#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to toggle the UID    #
#               on the host server.                               #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        The Unit ID light will be flashing if the server is      #
#        engaged in an activity that can not or should not be     #
#        interrupted (such as updating iLO firmware or an active  #
#        Remote Console session).  This script will not change    #
#        the status of a flashing Unit ID light until the activity#
#        causing the flashing status is completed.                #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - All versions.                                #

runLocal(){
  ilorest select ComputerSystem. -u USER_LOGIN -p PASSWORD
  # Possible Values: None, Unknown, Lit, Blinking, Off.             #
  ilorest set IndicatorLED=Lit
  ilorest logout
}

runRemote(){
  ilorest select ComputerSystem. --url=$1 --user $2 --password $3
  # Possible Values: None, Unknown, Lit, Blinking, Off.             #
  ilorest set IndicatorLED=Lit
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: UID_Control.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  UID_Control.sh"
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