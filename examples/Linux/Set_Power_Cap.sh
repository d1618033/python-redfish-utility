#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to set the Power     #
#               Cap feature on the host server.                   #

#        The power cap values are returned and received in Watts. #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        and other values inside the quotation marks with values  #
#        that are appropriate for your environment.               #

#        Modification of power cap setting requires               #
#        Configure iLO privilege.                                 #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - All versions.                                #

runLocal(){
  ilorest select Power. -u USER_LOGIN -p PASSWORD
  ilorest set PowerControl/PowerLimit/LimitInWatts=None
  ilorest commit
  ilorest logout
}

runRemote(){
  ilorest select Power. --url=$1 --user $2 --password $3
  ilorest set PowerControl/PowerLimit/LimitInWatts=None
  ilorest commit
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Set_PowerCap.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Set_PowerCap.sh"
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
