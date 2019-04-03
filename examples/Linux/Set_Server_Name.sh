#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP #

# Description: This is a sample bash script to set the host       #
#              server name.                                       #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - All versions.                                #

runLocal(){
  ilorest select Bios. -u USER_LOGIN -p PASSWORD
  ilorest set ServerName=MyServerName 
  ilorest commit
  ilorest logout
}

runRemote(){
  ilorest select Bios. --url=$1 --user $2 --password $3
  ilorest set ServerName=MyServerName 
  ilorest commit
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Set_Server_Name.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Set_Server_Name.sh"
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