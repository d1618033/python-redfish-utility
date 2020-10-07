#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to configure a       #
#               security text message in the iLO Login Banner.    #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #

runLocal(){
  ilorest select SecurityService. -u USER_LOGIN -p PASSWORD
  # Set to "True" or "False". If set to false, security message is#
  # removed.                                                      #
  ilorest set LoginSecurityBanner/IsEnabled=True
  ilorest commit
  # Enter the text of the message between                         #
  #'"LoginSecurityBanner/SecurityMessage=' and ' " '              #
  ilorest set "LoginSecurityBanner/SecurityMessage=This is a private system. It is to be used solely by authorized users and may be monitored for all lawful purposes. By accessing this system, you are consenting to such monitoring."
  ilorest commit
  ilorest logout
}

runRemote(){
  ilorest select SecurityService. --url=$1 --user $2 --password $3
  # Set to "True" or "False". If set to false, security message is#
  # removed.                                                      #
  ilorest set LoginSecurityBanner/IsEnabled=True
  ilorest commit
  # Enter the text of the message between                         #
  #'"LoginSecurityBanner/SecurityMessage=' and ' " '              #
  ilorest set "LoginSecurityBanner/SecurityMessage=This is a private system. It is to be used solely by authorized users and may be monitored for all lawful purposes. By accessing this system, you are consenting to such monitoring."
  ilorest commit
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Set_Security_Msg.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Set_Security_Msg.sh"
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