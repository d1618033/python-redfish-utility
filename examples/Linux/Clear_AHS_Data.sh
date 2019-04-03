#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to clear AHS         #
#               data.                                             #

#        Firmware support information for this script:            #
#            iLO 4 - All versions.                                #
#            iLO 5 - All versions.                                #


runLocal(){
  ilorest serverlogs --selectlog=AHS --clearlog -u USER_LOGIN -p PASSWORD
  ilorest logout
}

runRemote(){
  ilorest serverlogs --selectlog=AHS --clearlog --url=$1 --user $2 --password $3
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Clear_AHS_Data.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Clear_AHS_Data.sh"
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