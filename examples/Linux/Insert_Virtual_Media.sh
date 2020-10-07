#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to insert a virtual  #
#               media image.                                      #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment. You will also need to replace the           #
#        http://xx.xx.xx.xx/images/media.iso with the location of #
#        the virtual media you want to mount.                     #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - All versions.                                #

runLocal(){
  ilorest virtualmedia 2 http://xx.xx.xx.xx/images/media.iso -u USER_LOGIN -p PASSWORD
  ilorest logout
}

runRemote(){
  ilorest virtualmedia 2 http://xx.xx.xx.xx/images/media.iso --url=$1 --user $2 --password $3
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Insert_Virtual_Media.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Insert_Virtual_Media.sh"
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