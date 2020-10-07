#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to update the        #
#               language pack of following devices:               #
#                 Integrated Lights-Out 4 (iLO 4)                 #
#                 Integrated Lights-Out 5 (iLO 5)                 #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment and you will need to change the value of the #
#        component=/lpk to point to the language pack you wish to #
#        use for the language pack update.                        #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - 1.20 or later.                               #

runLocal(){
  ilorest login -u USER_LOGIN -p PASSWORD
  ilorest uploadcomp --component=/lang_ja_130.lpk --update_target
  ilorest logout
}

runRemote(){
  ilorest login $1 --user $2 --password $3
  ilorest uploadcomp --component=/lang_ja_130.lpk --update_target
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Update_Language.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Update_Language.sh"
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