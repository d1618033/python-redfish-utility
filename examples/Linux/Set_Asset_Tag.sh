#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to set the asset     #
#               tag, asset tag limited to 32 characters.          #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - 1.05 or later.                               #

runLocal(){
  ilorest select Bios. -u USER_LOGIN -p PASSWORD
  # Enter a string to set the asset tag, or an empty string         #
  # to clear the asset tag.                                         #
  ilorest set ServerAssetTag="Asset Tag" 
  ilorest commit 
  ilorest logout
}

runRemote(){
  ilorest select Bios. --url=$1 --user $2 --password $3
  # Enter a string to set the asset tag, or an empty string         #
  # to clear the asset tag.                                         #
  ilorest set ServerAssetTag="Asset Tag" 
  ilorest commit 
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Set_Asset_Tag.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Set_Asset_Tag.sh"
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