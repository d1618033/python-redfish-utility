#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to configure the     #
#               network settings for Integrated Lights-Out(iLO).  #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        and other values inside the quotation marks with values  #
#        that are appropriate for your environment.               #

#        Double check all values before executing this script.    #
#        Incorrect or mismatched network settings may cause you   #
#        to lose the ability to connect to your Lights-Out device.#

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #
#            iLO 4 - All versions.                                #

runLocal(){
  ilorest login -u USER_LOGIN -p PASSWORD
  ilorest save --selector=EthernetInterface. --filter Id=1 -f networksettings.json
  echo "Change the values that you would like to change in the 'networksettings.json' then press Enter."
  read -rsp $'Press any key to continue...\n' -n1
  echo "Your changes to the network settings will be uploaded and iLO will restart."
  ilorest load -f networksettings.json
  ilorest logout
}

runRemote(){
  ilorest login $1 --user $2 --password $3
  ilorest save --selector=EthernetInterface. --filter Id=1 -f networksettings.json
  echo "Change the values that you would like to change in the 'networksettings.json' then press Enter."
  read -rsp $'Press any key to continue...\n' -n1
  echo "Your changes to the network settings will be uploaded and iLO will restart."
  ilorest load -f networksettings.json
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Mod_Network_Settings.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Mod_Network_Settings.sh"
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