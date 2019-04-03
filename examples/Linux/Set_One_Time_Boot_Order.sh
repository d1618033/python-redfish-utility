#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP #

# Description: This is a sample bash script to Set One Time Boot  #
#                 Order.                                          #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        and other values inside the quotation marks with values  #
#        that are appropriate for your environment.               #

#        "None" will set the boot device according to Server      #
#        Boot Order in iLO GUI.                                   #

#        iLO 4 version 1.40 or later and iLO 5 all versions:      #
#        This will take one boot device from "None", "Cd", "Hdd", #
#        "Usb", "Utilities", "Diags", "BiosSetup", "Pxe",         #
#        "UefiShell", "UefiTarget".                               #

#        The following boot options will only work in iLO 5:      #
#        "SDCard" and "UefiHttp",                                 #

#        You will need to replace the text "BOOT_CHOICE" inside   #
#        the quotation marks with the option that you want to     #
#        boot to.                                                 #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - All versions.                                #

runLocal(){
  ilorest login -u USER_LOGIN -p PASSWORD
  ilorest bootorder --onetimeboot=None
  ilorest commit
  ilorest logout
}

runRemote(){
  ilorest login $1 --user $2 --password $3
  ilorest bootorder --onetimeboot=None
  ilorest commit
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Set_One_Time_Boot_Order.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Set_One_Time_Boot_Order.sh"
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