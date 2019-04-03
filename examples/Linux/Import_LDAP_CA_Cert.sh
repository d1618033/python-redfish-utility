#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to import LDAP CA    #
#               certificate on following device:                  #
#                 Integrated Lights-Out 4 (iLO 4)                 #
#                 Integrated Lights-Out 5 (iLO 5)                 #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - v2.53 onwards                                #

runLocal(){
  ilorest certificate ca certfile.txt -u USER_LOGIN -p PASSWORD
  ilorest logout
}

runRemote(){
  ilorest certificate ca certfile.txt --url=$1 --user $2 --password $3
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Import_LDAP_CA_Cert.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Import_LDAP_CA_Cert.sh"
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