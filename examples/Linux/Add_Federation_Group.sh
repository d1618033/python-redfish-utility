#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to add a Federation  #
#               group membership and grant associated privileges  #
#               on the following devices:                         #
#                 Integrated Lights-Out 4 (iLO 4)                 #
#                 Integrated Lights-Out 5 (iLO 5)                 #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        and other values inside the quotation marks with         #
#        values that are appropriate for your environment.        #

#        Firmware support information for this script:            #
#            iLO 4 - 1.40 or later                                #
#            iLO 5 - All versions                                 #

runLocal(){
  ilorest ilofederation add newfedname thisfedkey -u USER_LOGIN -p PASSWORD
  ilorest logout
}

runRemote(){
  ilorest ilofederation add newfedname thisfedkey --url=$1 --user $2 --password $3
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Add_Federation_Group.bat ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Add_Federation_Group.bat"
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