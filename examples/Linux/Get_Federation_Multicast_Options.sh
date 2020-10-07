#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to retrieve the      #
#        current Federation multicast options.                    #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - version 1.40 or later.                       #

runLocal(){
  ilorest select Manager. -u USER_LOGIN -p PASSWORD
  # The line below is for iLO 5 and up.                           #
  ilorest list Oem/Hpe/FederationConfig

  #Uncomment the line below is you are using iLO 4.               #
  #ilorest list Oem/Hp/FederationConfig
  ilorest logout
}

runRemote(){
  ilorest select Manager. --url=$1 --user $2 --password $3
  # The line below is for iLO 5 and up.                           #
  ilorest list Oem/Hpe/FederationConfig

  #Uncomment the line below is you are using iLO 4.               #
  #ilorest list Oem/Hp/FederationConfig
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Get_Federation_Multicast_Options.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Get_Federation_Multicast_Options.sh"
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