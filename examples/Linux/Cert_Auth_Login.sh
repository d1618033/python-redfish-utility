#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to test certificate  #
#               based login on the following devices:             #
#                 Integrated Lights-Out 5 (iLO 5) - v2.40+        #

# NOTE:  Verbose flag added for visibility                        #
# NOTE:  Local mode not applicable                                #
# NOTE:  For password protected private
#
# REQUIREMENTS:  - iLO 5 v2.40
#                - Set NTP Server on iLO and verify accurate time #
#                - "iLO Advanced Premium Security Edition" license#
#                - X509 SSL certificate signed with root CA key   #
#                - CAC/Smartcard Authentication Enabled           #
#                - Add root CA certificate to iLO                 #
#                - Map user CA certificate to target iLO          #
#                  management user.                               #
# GUIDE: 1. Generate root CA private key                          #
#           openssl genrsa -out testCA.key 4096                   #
#        2. Configure and set X509 SSL certificate by generating  #
#           a CSR from iLO and signing with private root CA key.  #
#           openssl req -x509 -new -nodes -key testCA.key         #
#           -sha256 -days 1024 -subj "/O=HPE/OU=R&D/CN=CA for     #
#           testing iLO authentication" -out testCA.crt
#        3. Add SSL certificate to iLO                            #
#           Security | CAC/Smartcard | Import Trusted CA          #
#           Certificates | Direct Import).                        #
#        4. Generate user rsa private key                         #
#           openssl genrsa -out user.key 4096                     #
#        5. Generate user root CA                                 #
#           openssl req -x509 -new -nodes -key user.key -sha256   #
#           -days 1825 -out testCA.pem
#        6. Generate user CA certificate                          #
#           openssl x509 -req -in user.csr -CA testCA.pem -CAkey  #
#           user.key -CAcreateserial -sha256 -days 1024 -out      #
#           user.pem                                              #
#        7. Add root CA certificate
#           Security | CAC/Smartcard | Import Trusted CA          #
#           Certificates                                          #
#        8. Add user CA certificate mapping to specified user     #
#           Security | Certificate Mappings | Authorized          #
#           Certificates | <iLO username>)                        #
#                                                                 #
#        Firmware support information for this script:            #
#            iLO 5 v2.40 (and above)                              #

runRemote(){
  ilorest login -v --url=$1 --user=$2 --privatecert=$3 --userrootcakey=$4 --usercacert=$5
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Cert_Auth_Login.sh ^<iLO url^> ^<iLO username^> ^<User Root CA Key^> ^<Root CA Certificate^> ^<User Certificate^>"
}

if [ "$#" -eq "5" ]
  runRemote
else
  error
fi