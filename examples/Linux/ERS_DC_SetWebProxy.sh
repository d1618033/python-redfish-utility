#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to start director    #
#               test on following device:                         #
#                 Integrated Lights-Out 4 (iLO 4)                 #
#                 Integrated Lights-Out 5 (iLO 5)                 #

# Directory tests enable you to validate the configured directory #
# settings. The directory test results are reset when directory   #
# settings are saved, or when the directory tests are started.    #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - v2.40 onwards                                #

runLocal(){
  ilorest select RemoteSupport. -u USER_LOGIN -p PASSWORD
  ilorest set ProxySettings/Url=Web_Proxy_Server_Hostname_or_IP_address
  ilorest set ProxySettings/Port=Web_Proxy_Server_Port
  # If your web proxy requires authentication,                    # 
  #  use the following ProxySettings/Username=,                   #
  #  and ProxySettings/Password= tags.                            #
  #ilorest set ProxySettings/Username=Web_Proxy_Server_Username
  #ilorest set ProxySettings/Password=Web_Proxy_Server_Password
  ilorest logout
}

runRemote(){
  ilorest select RemoteSupport. --url=$1 --user $2 --password $3
  ilorest set ProxySettings/Url=Web_Proxy_Server_Hostname_or_IP_address
  ilorest set ProxySettings/Port=Web_Proxy_Server_Port
  # If your web proxy requires authentication,                    # 
  #  use the following ERS_WEB_PROXY_USERNAME,                    #
  #  and ERS_WEB_PROXY_PASSWORD tags.                             #
  #ilorest set ProxySettings/Username=Web_Proxy_Server_Username
  #ilorest set ProxySettings/Password=Web_Proxy_Server_Password
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: ERS_DC_SetWebProxy.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  ERS_DC_SetWebProxy.sh"
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