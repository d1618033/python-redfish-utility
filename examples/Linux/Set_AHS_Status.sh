#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to enable or disable #
#               AHS logging.                                      #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - All versions.                                # 

runLocal(){
  ilorest select ActiveHealthSystem -u USER_LOGIN -p PASSWORD
  # Possible Values: Set to "Enable" or "False". #
  ilorest set AHSEnabled=True --commit 
  ilorest logout
}

runRemote(){
  ilorest select ActiveHealthSystem --url=$1 --user $2 --password $3
  # Possible Values: Set to "Enable" or "False". #
  ilorest set AHSEnabled=True --commit 
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Set_Boot_Mode.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Set_Boot_Mode.sh"
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