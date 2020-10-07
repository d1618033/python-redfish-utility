#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description: This a sample batch script to delete an HPE SIM    #
#        Single Sign-On (SSO) server record by index.             #

# NOTE:  You will need to replace the values inside the quotation #
#        marks with values that are appropriate for your          #
#        environment.                                             #

#        You can determine the record index using                 #
#        Get_SSO_Settings.bat. As you remove records, the index of#
#        subsequent entries is reduced.                           #

#        Modification of SSO settings requires Configure iLO      #
#        privilege.                                               #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - All versions                                 #

runLocal(){
  ilorest singlesignon deleterecord "6" -u USER_LOGIN -p PASSWORD
  ilorest logout
}

runRemote(){
  ilorest singlesignon deleterecord "6" --url=$1 --user $2 --password $3
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: delete_sso_rec.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  delete_sso_rec.sh"
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