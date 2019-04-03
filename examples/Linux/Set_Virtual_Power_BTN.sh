#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP #

# Description: This is a sample bash script to perform the        #
#         following actions:                                      #
#	        - simulate physical press of the server power button    #
#	        - simulate physical press and hold of the server        #
#              power button                                       #
#	        - cold boot                                             #
#	        - warm boot                                             #

# NOTES:                                                          #
#      - You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #
#      - The user must have the virtual power and reset privilege #
#        to execute this command.                                 #

# Help:                                                           #
# PushPowerButton :                                               #
#        This PushPowerButton command is used to simulate a       #
#        physical press of the server power button.               #
# ColdBoot :                                                      #
#        The ColdBoot command forces a cold boot of the server,   #
#        if the server is currently on.                           #
# PressAndHold :                                                  #
#        This PressAndHold command is used to simulate a physical #
#        press and hold of the server power button.               #
# NOTE:  The above options should not be used together.           #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - All versions.                                #

runLocal(){
  ilorest login -u USER_LOGIN -p PASSWORD
  ilorest reboot PushPowerButton
  #ilorest reboot ColdBoot
  #ilorest reboot PressAndHold
  ilorest commit
  ilorest logout
}

runRemote(){
  ilorest login $1 --user $2 --password $3
  ilorest reboot PushPowerButton
  #ilorest reboot ColdBoot
  #ilorest reboot PressAndHold
  ilorest commit
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Set_Virtual_Power_BTN.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Set_Virtual_Power_BTN.sh"
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