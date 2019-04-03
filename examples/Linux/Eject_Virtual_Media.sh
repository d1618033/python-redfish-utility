#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to eject virtual     #
#               media                                             #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - All versions.                                #

runLocal(){
  #Id specifies the Virtual Media device target. The possible values#
  # are 1 or 2. 1 is for Floppy or USBStick and 2 is for CD DVD.    #
  ilorest virtualmedia Id --remove -u USER_LOGIN -p PASSWORD
  ilorest logout
}

runRemote(){
  #Id specifies the Virtual Media device target. The possible values#
  # are 1 or 2. 1 is for Floppy or USBStick and 2 is for CD DVD.    #
  ilorest virtualmedia Id --remove --url=$1 --user $2 --password $3
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Eject_Virtual_Media.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Eject_Virtual_Media.sh"
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