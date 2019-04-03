#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to configure a set   #
#               of Remote Console hot-keys for iLO.               #

#               You will need to change the values in 
#               Hotkey_Config.json to match the values you want   #
#               to apply.

#        The KeySequence order in the HotKey_Config.json is:      #
#        Name=Ctrl-T, Name=Ctrl-U, Name=Ctrl-V, Name=Ctrl-W,      #
#        Name=Ctrl-X, and Name=Ctrl-Y                             #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        and other values inside the quotation marks with values  #
#        that are appropriate for your environment.               #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #


runLocal(){
  ilorest rawpatch Hotkey_Config.json -u USER_LOGIN -p PASSWORD
  ilorest logout
}

runRemote(){
  ilorest rawpatch Hotkey_Config.json --url=$1 --user $2 --password $3
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Get_VM_Status.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Get_VM_Status.sh"
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