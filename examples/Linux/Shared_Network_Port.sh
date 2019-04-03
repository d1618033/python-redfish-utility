#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP #

# Description: This is a sample bash script that configures       #
#              Lights-Out device to pass network traffic on the   #
#              shared host network port.  Change                  #
#              NICEnabled value to "True" to use the              #
#              Lights-Out device NIC.  On servers that do not     #
#              support this feature, this script generates an     #
#              error.                                             #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        The feature is only offered on selected hosts            #

#        After this script executes, Lights-Out device will be    #
#        reset for the changes to take place.                     #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #

runLocal(){
  ilorest select EthernetInterface. -u USER_LOGIN -p PASSWORD
  ilorest set Oem/Hpe/NICEnabled=True --filter Id=1
  ilorest commit
  ilorest logout
}

runRemote(){
  ilorest select EthernetInterface. --url=$1 --user $2 --password $3
  ilorest set Oem/Hpe/NICEnabled=True --filter Id=1
  ilorest commit
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Shared_Network_Port.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Shared_Network_Port.sh"
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