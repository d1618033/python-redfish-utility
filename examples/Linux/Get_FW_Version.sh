#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to return the        #
#               version of firmware currently running .           #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - All versions.                                #

runLocal(){
  ilorest select Manager. -u USER_LOGIN -p PASSWORD
  #The line below is for iLO 5                                    #
  ilorest list Oem/Hpe/Firmware/Current/VersionString
  # Uncomment the following line for iLO 4                        #
  #ilorest list Oem/Hp/Firmware/Current/VersionString
  ilorest logout
}

runRemote(){
  ilorest select Manager. --url=$1 --user $2 --password $3
  #The line below is for iLO 5                                    #
  ilorest list Oem/Hpe/Firmware/Current/VersionString
  # Uncomment the following line for iLO 4                        #
  #ilorest list Oem/Hp/Firmware/Current/VersionString
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Get_FW_Version.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Get_FW_Version.sh"
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