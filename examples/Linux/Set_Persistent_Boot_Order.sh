#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to Set Persistent    #
#               Boot Order.                                       #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        and other values inside the quotation marks with values  #
#        that are appropriate for your environment.               #

#        This will take one or more boot devices from cdrom,      #
#        floppy, hdd, usb, or network. If you do not list every   #
#        option, the remaining options will be shifted towards    #
#        the bottom of the list.                                  #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - All versions. UEFI support added 1.40        #

#        iLO 4 version 1.40 or later                              #
#          Continuous and one time boot options:                  #
#              1.      None                                       #
#              2.      Cd                                         #
#              3.      Hdd                                        #
#              4.      Usb                                        #
#              5.      Utilities                                  #
#              6.      Diags                                      #
#              7.      BiosSetup                                  #
#              8.      Pxe                                        #
#              9.      UefiShell                                  #
#              10.     UefiTarget                                 #

#        iLO 5 all versions:                                      #
#          Continuous and one time boot options:                  #
#              1.      None                                       #
#              2.      Cd                                         #
#              3.      Hdd                                        #
#              4.      Usb                                        #
#              5.      SDCard                                     #
#              6.      Utilities                                  #
#              7.      Diags                                      #
#              8.      BiosSetup                                  #
#              9.      Pxe                                        #
#              10.     UefiShell                                  #
#              11.     UefiHttp                                   #
#              12.     UefiTarget                                 #

#      Assignment of Boot device names varies from system to      #
#        system and may change when the system reboots. Execute   #
#        Get_Persistent_Boot_Order.sh to determine the current    #
#        Boot device assignments on your system, and choose       #
#        from those for the DEVICE values in SET_PERSISTENT_BOOT. #

#      Note: FLOPPY drive boot is not supported from Gen9 onwards #
#            in Legacy and UEFI modes                             #

runLocal(){
  ilorest login -u USER_LOGIN -p PASSWORD
  ilorest bootorder [1,2,6] --commit
  ilorest logout
}

runRemote(){
  ilorest login $1 --user $2 --password $3
  ilorest bootorder [1,2,6] --commit
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Set_Persistent_Boot_Order.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Set_Persistent_Boot_Order.sh"
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