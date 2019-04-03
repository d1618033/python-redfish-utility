#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP #

# Description: This a sample bash script to retrieve the HPE SIM  #
#          Single Sign-On (SSO) settings.                         #

# NOTE:  You will need to replace the values inside the quotation #
#        marks with values that are appropriate for your          #
#        environment.                                             #

#        HPE SIM Single Sign-On requires iLO Advanced or iLO      #
#        Select license.                                          #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - All versions.                                #

runLocal(){
  ilorest get SSOsettings --selector=SSO. -u USER_LOGIN -p PASSWORD
  ilorest logout
}

runRemote(){
  ilorest get SSOsettings --selector=SSO. --url=$1 --user $2 --password $3
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Get_SSO_Settings.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Get_SSO_Settings.sh"
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