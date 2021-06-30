#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to test login        #
#               on the following devices:                         #
#                 Integrated Lights-Out 5 (iLO 5)                 #
#                 Integrated Lights-Out 4 (iLO 4)                 #

# NOTE:  Verbose flag added for visibility                        #
# NOTE:  Authentication is not performed in production mode       #
#        (default); if a username and password are included then  #
#        the configuration will default to an internal,           #
#        unauthenticated user account. Higher security modes,     #
#        if configured, require a valid iLO management username   #
#        and password to connect.                                 #

#        Firmware support information for this script:            #
#            iLO 4 and 5 - All versions                           #

runLocal(){
  ilorest login -v --user $1 --password $2
  ilorest logout
}

runRemote(){
  ilorest login -v --url=$1 --user $2 --password $3
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Basic_Auth_Login.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Basic_Auth_Login.sh ^<iLO username^> ^<iLO password^>"
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