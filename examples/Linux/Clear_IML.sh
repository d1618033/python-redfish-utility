#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample batch script to clear the server #
#               IML log from following devices:                   #
#                 Integrated Lights-Out 4 (iLO 4)                 #
#                 Integrated Lights-Out 5 (iLO 5)                 #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - All versions                                 #

runLocal(){
  ilorest serverlogs --selectlog=IML --clearlog -u USER_LOGIN -p PASSWORD
  ilorest logout
}

runRemote(){
  ilorest serverlogs --selectlog=IML --clearlog --url=$1 --user $2 --password $3
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Clear_IML.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Clear_IML.sh"
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