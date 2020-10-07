#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description: This is a sample bash script to set the pending    #
#              boot mode.                                         #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - version 1.40 or later.                       #

runLocal(){
  ilorest select Bios. -u USER_LOGIN -p PASSWORD
  # Possible Values: LegacyBios or Uefi #
  ilorest set BootMode=Uefi
  ilorest commit
  ilorest logout
}

runRemote(){
  ilorest select Bios. --url=$1 --user $2 --password $3
  # Possible Values: LegacyBios or Uefi #
  ilorest set BootMode=Uefi
  ilorest commit
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