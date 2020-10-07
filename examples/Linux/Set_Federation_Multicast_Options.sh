#!/bin/bash

#    RESTful Interface Tool Sample Script for HPE iLO Products    #
#  Copyright 2014, 2020 Hewlett Packard Enterprise Development LP #

# Description:  This is a sample bash script to set the           #
#        Federation multicast options.                            #

# NOTE:  You will need to replace the USER_LOGIN and PASSWORD     #
#        values with values that are appropriate for your         #
#        environment.                                             #

#        Modification of Federation multicast settings requires   #
#        Configure iLO privilege.                                 #

#        Firmware support information for this script:            #
#            iLO 5 - All versions                                 #


runLocal(){
  ilorest select Manager. -u USER_LOGIN -p PASSWORD
  ilorest set Oem/Hpe/FederationConfig/iLOFederationManagerment=Enabled
  # Notes:                                                          #
  # Disabling multicast discovery or announcements will             #
  #    disable iLO Federation features.                             #

  #    All devices in a Federation group should have the same       #
  #    scope and TTL to avoid problems with peer discovery.         #

  ilorest set Oem/Hpe/FederationConfig/MulticastDiscoveryEnabled=Enabled
  # Valid values for MulticastAnnouncementInterval are              #
  #    "Disabled", "30", "60", "120", "300", "600",                 #
  #    "900", and "1800".  Numeric values are in seconds.           #
  ilorest set Oem/Hpe/FederationConfig/MulticastAnnouncementInterval=30
  # Valid values for IPv6MulticastScope are                         #
  #    "Link", "Site", and "Organization".                          #
  ilorest set Oem/Hpe/FederationConfig/IPv6MulticastScope=Site
  # MulticastTimeToLive may have any value between 1 and 255.       #
  ilorest set Oem/Hpe/FederationConfig/MulticastTimeToLive=255
  ilorest commit
  ilorest logout
}

runRemote(){
  ilorest select Manager. --url=$1 --user $2 --password $3
  ilorest set Oem/Hpe/FederationConfig/iLOFederationManagerment=Enabled
  # Notes:                                                          #
  # Disabling multicast discovery or announcements will             #
  #    disable iLO Federation features.                             #

  #    All devices in a Federation group should have the same       #
  #    scope and TTL to avoid problems with peer discovery.         #

  ilorest set Oem/Hpe/FederationConfig/MulticastDiscoveryEnabled=Enabled
  # Valid values for MulticastAnnouncementInterval are              #
  #    "Disabled", "30", "60", "120", "300", "600",                 #
  #    "900", and "1800".  Numeric values are in seconds.           #
  ilorest set Oem/Hpe/FederationConfig/MulticastAnnouncementInterval=30
  # Valid values for IPv6MulticastScope are                         #
  #    "Link", "Site", and "Organization".                          #
  ilorest set Oem/Hpe/FederationConfig/IPv6MulticastScope=Site
  # MulticastTimeToLive may have any value between 1 and 255.       #
  ilorest set Oem/Hpe/FederationConfig/MulticastTimeToLive=255
  ilorest commit
  ilorest logout
}

error(){
  echo "Usage:"
  echo        "remote: Set_Federation_Multicast_Options.sh ^<iLO url^> ^<iLO username^>  ^<iLO password^>"
  echo        "local:  Set_Federation_Multicast_Options.sh"
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