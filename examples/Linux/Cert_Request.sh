#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2019 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample batch script to get a certificate#
#               signing request from following devices:           #
#                 Integrated Lights-Out 5 (iLO 5)                 #
#                 Integrated Lights-Out 4 (iLO 4)                 #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#                        Use ilorest Tool                         #

#        Default:                                                 #
#           If default is chosen, then run the script with just   #
#           the CERTIFICATE_SIGNING_REQUEST tag, and the following#
#           will be used for generating the certificate:          #
#             Country Name: "US"                                  #
#             State: "Texas"                                      #
#             Locality: "Houston"                                 #
#             Organization: "Hewlett Packard Enterprise"          #
#             Organization Unit: "ISS"                            #
#             Common Name: The Fully Qualified Domain Name        #
#                          of this iLO subsystem.                 #
#        Custom:                                                  #
#           All tags are required except CSR_ORGANIZATIONAL_UNIT. #
#           If the script is run with missing any of the required #
#           tags, then the default will be used for the missing   #
#           tag. If the tag is required and the tag is left blank,#
#            there will be an error running the script.           #

#        Firmware support information for this script:            #
#         iLO 4 - Default: all versions                           #
#                 Custom csr: 1.10 or later                       #

runLocal(){
  ilorest certificate csr orgname orgunit commonname UnitedStates Texas Houston -u USER_LOGIN -p PASSWORD
  ilorest logout
}

runRemote(){
  ilorest certificate csr orgname orgunit commonname UnitedStates Texas Houston --url=$1 --user $2 --password $3
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Cert_Request.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Cert_Request.sh"
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