#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description: This a sample bash script to configure Computer    #
#              Lock settings on:                                  #
#                 Integrated Lights-Out 5 (iLO 5)                 #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        and other values inside the quotation marks with values  #
#        that are appropriate for your environment.               #

#        Modification of Computer Lock settings requires Configure#
#        iLO privilege.                                           #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #

runLocal(){
  ilorest select Manager. -u USER_LOGIN -p PASSWORD
  # To set default Windows Computer Lock keys combination:        #
  ilorest set Oem/Hpe/IntegratedRemoteConsole/LockKey/LockOption=Windows

  # To configure custom Computer Lock keys combination uncomment  #
  # the lines below.                                              #
  #ilorest set Oem/Hpe/IntegratedRemoteConsole/LockKey/LockOption=Custom
  #ilorest set Oem/Hpe/IntegratedRemoteConsole/LockKey/CustomKeySequence="[L_GUI,l,NONE,NONE,NONE]"

  # To disable Computer Lock feature:                             #
  #ilorest set Oem/Hpe/IntegratedRemoteConsole/LockKey/LockOption=Disabled
  ilorest commit
  ilorest logout
}

runRemote(){
  ilorest select Manager. --clearlog --url=$1 --user $2 --password $3
  # To set default Windows Computer Lock keys combination:          #
  ilorest set Oem/Hpe/IntegratedRemoteConsole/LockKey/LockOption=Windows

  # To configure custom Computer Lock keys combination uncomment  #
  # the lines below.                                              #
  #ilorest set Oem/Hpe/IntegratedRemoteConsole/LockKey/LockOption=Custom
  #ilorest set Oem/Hpe/IntegratedRemoteConsole/LockKey/CustomKeySequence="[L_GUI,l,NONE,NONE,NONE]"

  # To disable Computer Lock feature:                               #
  #ilorest set Oem/Hpe/IntegratedRemoteConsole/LockKey/LockOption=Disabled
  ilorest commit
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Computer_Lock_Config.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Computer_Lock_Config.sh"
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