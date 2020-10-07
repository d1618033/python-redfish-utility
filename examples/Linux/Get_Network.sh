#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to return current    #
#               network settings.                                 #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - All versions.                                #

runLocal(){
  ilorest login -u USER_LOGIN -p PASSWORD
  # The line below is for iLO 5 and up.                           #
  ilorest get --selector=ManagerNetworkProtocol
  # Uncomment the line below is you are using iLO 4.              #
  #ilorest get --selector=ManagerNetworkService
  ilorest logout
}

runRemote(){
  ilorest login $1 --user $2 --password $3
  # The line below is for iLO 5 and up.                           #
  ilorest get --selector=ManagerNetworkProtocol
  # Uncomment the line below is you are using iLO 4.              #
  #ilorest get --selector=ManagerNetworkService
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Get_Network.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Get_Network.sh"
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