#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to enable or disable #
#               brownout support.                                 #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #

runLocal(){
  ilorest select Power. -u USER_LOGIN -p PASSWORD
  # Disable brownout recovery                                     #
  ilorest set Oem/Hpe/BrownoutRecoveryEnabled=False
  # Enable  brownout recovery                                     #
  #ilorest set Oem/Hpe/BrownoutRecoveryEnabled=True
  ilorest list Oem/Hpe/BrownoutRecoveryEnabled
  ilorest commit
  ilorest logout
}

runRemote(){
  ilorest select Power. --url=$1 --user $2 --password $3
  # Disable brownout recovery                                     #
  ilorest set Oem/Hpe/BrownoutRecoveryEnabled=False
  # Enable  brownout recovery                                     #
  #ilorest set Oem/Hpe/BrownoutRecoveryEnabled=True
  ilorest list Oem/Hpe/BrownoutRecoveryEnabled
  ilorest commit
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Set_Brownout.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Set_Brownout.sh"
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