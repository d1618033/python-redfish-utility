#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to set the           #
#               persistent mouse and keyboard.                    #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #

runLocal(){
  ilorest select Manager. -u USER_LOGIN -p PASSWORD
  ilorest set Oem/Hpe/PersistentMouseKeyboardEnabled=False
  ilorest commit
  ilorest logout
}

runRemote(){
  ilorest select Manager. --url=$1 --user $2 --password $3
  ilorest set Oem/Hpe/PersistentMouseKeyboardEnabled=False
  ilorest commit
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Set_Persmouse_Status.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Set_Persmouse_Status.sh"
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