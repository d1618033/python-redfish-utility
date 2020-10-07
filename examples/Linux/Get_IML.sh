#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description: This is a sample bash script to retrieve the       #
#              Integrated Management Log.                         #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - All versions.                                #

runLocal(){
  ilorest serverlogs --selectlog=IML -f IMLlog.txt -u USER_LOGIN -p PASSWORD
  ilorest logout
}

runRemote(){
  ilorest serverlogs --selectlog=IML -f IMLlog.txt --url=$1 --user $2 --password $3
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Get_IML.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Get_IML.sh"
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