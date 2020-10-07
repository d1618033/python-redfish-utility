#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to change a user's   #
#               password in the database of local users on        #
#               following devices:                                #
#                 Integrated Lights-Out 4 (iLO 4)                 #
#                 Integrated Lights-Out 5 (iLO 5)                 #

# NOTE:  You will need to replace the values inside the quote     #
#        marks with values that are appropriate for your          #
#        environment.                                             #

runLocal(){
  ilorest iloaccounts changepass USERNAME NEWPASSWORD -u USER_LOGIN -p PASSWORD
  ilorest logout
}

runRemote(){
  ilorest iloaccounts changepass USERNAME NEWPASSWORD --url=$1 --user $2 --password $3
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Change_Password.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Change_Password.sh"
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