#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to update the        #
#               Integrated Lights-Out(iLO) firmware.              #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment and you will need to change the value of the #
#        IMAGE_LOCATION to point to the new binary firmware image #
#        you wish to use for the firmware update.                 #
#        The Unit ID light flashes when the server is engaged in  #

#        an activity that can not or should not be interrupted    #
#        (such as updating iLO firmware or an active Remote       #
#        Console session).  The Unit ID light should flash while  #
#        this script is updating the firmware.                    #
#        The Lights-Out device will automatically reset itself to #
#        have the new firmware take effect at the end of the      #
#        firmware flash.                                          #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - All versions                                 #

runLocal(){
  ilorest login -u USER_LOGIN -p PASSWORD
  firmwareupdate https://IMAGE_LOCATION.bin
  #  Use the line below instead if your server uses TPM:          #
  #ilorest firmwareupdate https://IMAGE_LOCATION.bin --tpmenabled
  ilorest logout
}

runRemote(){
  ilorest login $1 --user $2 --password $3
  firmwareupdate https://IMAGE_LOCATION.bin
  #  Use the line below instead if your server uses TPM:          #
  #ilorest firmwareupdate https://IMAGE_LOCATION.bin --tpmenabled
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Update_Firmware.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Update_Firmware.sh"
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