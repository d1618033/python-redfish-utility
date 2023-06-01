## StorageController Commands (previously smartarray command)

The Storage Controller commands are designed for use with HPE Gen10 and later servers.

<aside class="notice">
<ul>
<li>A Smart Array Capable controller capable of communicating with iLO is required.</li>
<li>Logical volume creation is determined on initialization of the controller at system startup. Therefore, invalid entries can only be determined after reboot.
</ul>
</aside>

### Clearcontrollerconfig Command

> Clearcontrollerconfig example commands:

> To clear a controller configuration run the command including the `--controller` option specifying the controller to clear.

<pre>
ilorest > <span style="color: #01a982; ">clearcontrollerconfig --controller=1</span>
One or more properties were changed an will not take effect until system is reset.
</pre>

<p class="fake_header">Syntax</p>
clearcontrollerconfig *[Optional Parameters]*

<p class="fake_header">Description</p>
Clears smart array controller configuration.

<p class="fake_header">Parameters</p>

- **-h, --help**

Including the help flag will display help for the command.

- **--controller=CONTROLLER**

Use this flag to select the corresponding controller.

<p class="fake_header">Login Parameters</p>

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.


- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. Using this flag when not logged in will have no effect.

<p class="fake_header">Input</p>
None

<p class="fake_header">Output</p>
None

### CreateVolume Command (previously Createlogicaldrive Command)

> Createvolume example commands:

> To create a quick logical drive run the command with the following arguments: The type of creation as quickdrive, the raid level, the number of drives to use, the type of drive to use, the drive interface type, and the drive location. Also include the `--controller` option selecting the controller the drive will be created on. See the options list for possible values of these and more.

<pre>

ilorest > <span style="color: #01a982; ">createlogicaldrive quickdrive Raid0 1 SSD SAS --locationtype=Internal --controller="Slot 0"</span>

One or more properties were changed an will not take effect until system is reset.
</pre>

> To create a custom logical drive run the command with the following arguments: The type of creation as customdrive, the raid level, and the physicaldrive drive location. Also include the `--controller` option selecting the controller the drive will be created on. See the options list for possible values of these and more.

<pre>
iLOrest > login
Discovering data...Done

ilorest > <span style="color: #01a982; ">createlogicaldrive customdrive Raid5 1E:1:2 --controller=1 --name=ANewVolume --spare-drives=2 --capacityGiB=100 --legacy-boot=Primary --accelerator-type=ControllerCache --sparetye=Dedicated</span>

One or more properties were changed an will not take effect until system is reset.
</pre>

> To create a volume run the command with the following arguments: The type of creation as volume, the raid level, the drive location. Also include the --controller option selecting the controller the drive will be created on. See the options list for possible values of these and more.

<pre>
ilorest > <span style="color: #01a982; ">createlogicaldrive volume RAID0 1D:0:0 --DisplayName Name1 --iOPerfModeEnabled False --ReadCachePolicy ReadAhead --WriteCachePolicy ProtectedWriteBack --WriteHoleProtectionPolicy Yes --sparedrives 1E:0:0 --capacitygib 1000 --controller=0 --storageid=DE00900</span>
Operation completed successfully
</pre>

<aside class="notice">
For iLO6 onwards, there is no need to reboot after creating a volume.
But for iLO5, it requires a reboot after creating the volumes. If the drives are not present after a full reboot, run the results command to check for errors in the configuration.
</aside>

<p class="fake_header">Syntax</p>

createvolume *[SUBCOMMAND]* *[Optional Parameters]*

<p class="fake_header">Description</p>
Creates a new volume on the selected controller.

<p class="fake_header">SUBCOMMAND</p>

* Either QuickDrive or CustomDrive for iLO5(Gen10/Gen10Plus)
* Volume for Gen11(iLO6)

<p class="fake_header">Parameters</p>

- **-h, --help**

Including the help flag will display help for the command.

- **--DisplayName**

Drive display name (usable for volume subcommand)

- **--iOPerfModeEnabled**

Either True or False. (usable for volume subcommand)

- **--ReadCachePolicy**

Either ReadAhead or Off. (usable for volume subcommand)

- **--WriteCachePolicy**

Either Off, WriteThrough, ProtectedWriteBack or UnprotectedWriteBack. (usable for volume subcommand)

- **--WriteHoleProtectionPolicy**

Either Yes or No (usable for volume subcommand)

- **--sparedrives**

Specify Spare Drives if needed for create volume. Has to be different than main drive where volume is getting created. (usable for volume subcommand)

- **--raid-level**
  
Use this to specify one of the raid levels  
  Raid0, Raid1, Raid1ADM, Raid10, Raid10ADM, Raid5, Raid50, Raid6, Raid60  
  
  
- **--media-type**  
  
Either SSD or HDD
  
  
- **--interface-type**  

Should be SAS, SATA or NVMe
  
    
- **--drive-location**
  
Either Internal or External  
  

- **spare-type**
  
Either Dedicated or Roaming  
  
- **--accelerator-type**
  
Either ControllerCache, IOBypass or None  
  

- **paritytype**
  
Either Default or Rapid


- **--controller=CONTROLLER**

Use this flag to select the corresponding controller.

- **--storageid=STORAGEID**

Use this flag to select the corresponding Storage Id. This is applicable for iLO 6 only.

- **-n DRIVENAME, --name=DRIVENAME**

Optionally include to set the drive name (usable in custom creation only).

- **--spare-drives=SPAREDRIVES**

Optionally include to set the spare drives by the physical drive's drive Location (usable in custom creation only).

- **--capacitygib=CAPACITYGIB**

Optionally include to set the capacity of the drive in GiB (usable in custom creation only, use -1 for max size).

- **--spare-type=SPARETYPE**

Optionally include to choose the spare drive type (usable in custom creation only).

- **--accelerator-type=ACCELERATORTYPE**

Optionally include to choose the accelerator type.

- **--legacy-boot=LEGACYBOOT**

Optionally include to choose the legacy boot priority (usable in custom creation only).

- **--capacityBlocks=CAPACITYBLOCKS**

Optionally include to choose the capacity in blocks (use -1 for max size, usable in custom creation only).

- **--paritygroupcount=PARITYGROUP**

Optionally include to include the number of parity groups to use (only valid for certain RAID levels).

- **--paritytype=PARITYTYPE**

Optionally include to choose the parity initialization type (usable in custom creation only).

- **--block-size-bytes=BLOCKSIZE**

Optionally include to choose the block size of the disk drive (usable in custom creation only).

- **--strip-size-bytes=STRIPSIZE**

Optionally include to choose the strip size in bytes (usable in custom creation only).

- **--stripe-size-bytes=STRIPESIZE**

Optionally include to choose the stripe size in bytes (usable in custom creation only).

<p class="fake_header">Login Parameters</p>

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. Using this flag when not logged in will have no effect.

<p class="fake_header">Input</p>
None


<p class="fake_header">Output</p>
None

### Deletevolume Command (previously Deletelogicaldrive Command)

> Deletevolume example commands:

> To delete multiple volumes by drive location include the drive location of the drive you wish to delete. Also include the `--controller` option specifying the controller to use. You can specify multiple drives as well as a comma separated list.

> In case of iLO 6, --storageid tag is mandatory.

<aside class="notice">
A Volume Unique Identifier must be available to delete a volume. Pending drives may not be deleted.
</aside>

<pre>
ilorest > <span style="color: #01a982; ">deletevolume --controller=1 1</span>
Are you sure you would like to continue deleting drive 004D56ABPEYHC0ARH951TK A39C? (y/n)
Setting volume 004D56ABPEYHC0ARH951TK A39C for deletion
One or more properties were changed and will not take effect until system is reset.
</pre>


> To delete all volumes on a controller include the`--controller` option specifying the controller to perform the operation on and the `--all` option.

<pre>
iLOrest > login
Discovering data...Done
ilorest > deletevolume --controller=1 <span style="color: #01a982; ">--all</span>
[200] The operation completed successfully.
</pre>

<p class="fake_header">Syntax</p>

deletevolume *[Optional Parameters]*

<p class="fake_header">Description</p>
Deletes volumes from the selected controller.

<p class="fake_header">Parameters</p>

- **-h, --help**

Including the help flag will display help for the command.

- **--controller=CONTROLLER**

Use this flag to select the corresponding controller.

- **--storageid=STORAGEID**

Use this flag to select the corresponding Storage Id. This is applicable for iLO 6 only.

- **--all**

Use this flag to delete all volumes on a controller.

- **--force**

Use this flag to override the "are you sure?" text when deleting a volume.

<p class="fake_header">Login Parameters</p>

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. Using this flag when not logged in will have no effect.

<p class="fake_header">Input</p>
None

<p class="fake_header">Output</p>
None

### Drivesanitize Command

> Drivesanitize example commands:

> To sanitize a physical drive pass its drive location along with the `--controller` option to specify which controller to perform the operation on.
> In case of iLO 6, --storageid tag is mandatory.

<pre>
ilorest > drivesanitize --controller=0 1I:3:4 --mediatype="HDD"
Setting physical drive 1I:3:4 for sanitization
One or more properties were changed and will not take effect until system is reset.
Sanitization will occur on the next system reboot.
</pre>

> To sanitize multiple physical drives pass the location as a comma separated list along with the `--controller` option to specify which controller to perform the operation on.

<pre>
ilorest > drivesanitize --controller=<span style="color: #01a982; ">0 1I:3:3,1I:3:2,1I:3:1 --mediatype="HDD"</span>
Setting physical drive 1I:3:3 for sanitization
Setting physical drive 1I:3:2 for sanitization
Setting physical drive 1I:3:1 for sanitization
One or more properties were changed and will not take effect until system is reset.
Sanitization will occur on the next system reboot.
</pre>

>Use the --status tag to check the status of Sanitization. This is only applicable for iLO 6.

<pre>
ilorest > drivesanitize 1I:1:1 --controller=1 --storageid=DE00900 --mediatype="HDD" --status </span>
The drive is in Sanitizing state, 25 percent complete.
</pre>

>Once the process in 100% complete, use the --drivereset tag to reset the drive. This is only applicable for iLO 6

<pre>
ilorest > drivesanitize 1I:1:1 --controller=1 --storageid=DE00900 --mediatype="HDD" --drivereset </span>
DriveReset path and payload: /redfish/v1/Systems/1/Storage/DE00A000/Drives/8/Actions/Drive.Reset, {"ResetType": "ForceOn"}
</pre>

<p class="fake_header">Syntax</p>

drivesanitize *[Optional Parameters]*

<p class="fake_header">Description</p>
Erase/Sanitizes physical drives.

<p class="fake_header">Parameters</p>

- **-h, --help**

Including the help flag will display help for the command.

- **--controller=CONTROLLER**

Use this flag to select the corresponding controller.

- **--storageid=STORAGEID**

Use this flag to select the corresponding Storage Id. This is applicable for iLO 6 only.

- **--status**

Use this flag to check sanitization status of a controller. This is applicable for iLO 6 only.

- **--drivereset**

Use this flag to reset physical drives on a controller. This is applicable for iLO 6 only.

- **--mediatype=HDD/SSD**

Use this flag to indicate if the drive is HDD or SSD.  This is mandatory option.

- **--reboot**

Include this flag to perform a coldboot command function after completion of operations and monitor sanitization.

- **--all**

Use this flag to sanitize all physical drives on a controller.

<p class="fake_header">Login Parameters</p>

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. Using this flag when not logged in will have no effect.

<p class="fake_header">Input</p>
None

<p class="fake_header">Output</p>
None

### Factoryresetcontroller Command

> Factoryresetcontroller example commands:

> To factory reset a controller run this command and specify it's index with the `--controller` option.
> In case of iLO 6, --storageid tag is mandatory.

<pre>
ilorest > <span style="color: #01a982; ">factoryresetcontroller --controller=1</span>
One or more properties were changed and will not take effect until system is reset.
</pre>

> To factory reset a controller on Gen 11 server run the command with --resettype with options either resetall or preservevolumes followed by --storageid.

<pre>
ilorest > <span style="color: #01a982; ">factoryresetcontroller --resettype resetall --storageid DE000100</span>
Operation completed successfully
</pre>

> To factory reset all controllers run this command and include the `--all` option.

<pre>
ilorest > factoryresetcontroller <span style="color: #01a982; ">--all</span>
One or more properties were changed and will not take effect until system is reset.
</pre>

<p class="fake_header">Syntax</p>

factoryresetcontroller *[Optional Parameters]*

<p class="fake_header">Description</p>
Restores a controller to factory defaults.

<p class="fake_header">Parameters</p>

- **-h, --help**

Including the help flag will display help for the command.

- **--reset_type**

Either ResetAll or PreserveVolumes (Usable in iLO6/Gen11 servers)

- **--controller=CONTROLLER**

Use this flag to select the corresponding controller.

- **--storageid=STORAGEID**

Use this flag to select the corresponding Storage Id. This is applicable for iLO 6 only.

<p class="fake_header">Login Parameters</p>

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. Using this flag when not logged in will have no effect.

<p class="fake_header">Input</p>
None


<p class="fake_header">Output</p>
None

### StorageController Command (previously Smartarray Command)

> In case of iLO 6, --storageid tag is mandatory.

> To list all available storage controllers run the command without arguments.

<pre>
ilorest > <span style="color: #01a982; ">storagecontroller</span>
[1]&#58; Slot 0
</pre>

> To list all Existing Volume Unique Identifier's for logical drives for all controllers run the command including the `--volumes` option. Drives which are pending will instead show "Pending Drive" for the Volume Unique Identifier (this will be available after the system has been rebooted and the drive has been successfully created.). The information is presented such that the controller slot number is noted first, followed by all associated volumes to that controller.

<pre>
iLOrest > login
Discovering data...Done
ilorest > <span style="color: #01a982; ">storagecontroller --volumes</span>
[1]&#58; Slot 0
Volumes&#58;
[1]&#58; 600508B1001C599DE361257397F69972
[2]&#58; Pending drive
[3]&#58; Pending drive
</pre>

> To list all physical drives for all available controllers, run the command with the `--physicaldrives` option. The controller will be provided first followed by drive information (as associated to that controller). Drive information is in the format, [Controller Port (Internal)]:[Box]:[Bay].

<pre>
iLOrest > login
Discovering data...Done
ilorest > <span style="color: #01a982; ">storagecontroller --physicaldrives</span>
[1]&#58; Slot 0
Physical Drives&#58;
[1]&#58; 1I:3:4
[2]&#58; 1I:3:3
[3]&#58; 1I:3:2
[4]&#58; 1I:3:1
[5]&#58; 2I:3:5
[6]&#58; 2I:3:6
</pre>

> To return a response including controller settings, as well as physical drives and volumes information on the selected controller, include the `--controller` option followed by the number in brackets associated to the controller.

<pre>
ilorest > <span style="color: #01a982; ">storagecontroller --controller=0</span>
Selected option(s): #StorageCollection.StorageCollection
------------------------------------------------
Controller Info
------------------------------------------------
Id: 0
Name: HPE Smart Array SR308i-p Gen11
FirmwareVersion: 5.32
Manufacturer: HPE
Model: HPE Smart Array SR308i-p Gen11
PartNumber: 830826-001
SerialNumber: PZDLCX1GFG002O
SKU: 836269-001
Status: {'Health': 'Critical', 'State': 'Enabled'}
SupportedDeviceProtocols: ['SAS', 'SATA']
SupportedControllerProtocols: ['PCIe']
ILOREST return code: 0
</pre>

> To return a JSON formatted response regarding the settings and attributes of the selected physical drive on the selected controller include the `--controller` option specifying the controller and the `--pdrive` option specifying the physical drive number in brackets.

<pre>
ilorest > <span style="color: #01a982; ">storagecontroller --controller=0 --pdrive=1I:3:4 -j</span>
{
  "Controller": "Slot=3 - HPE Smart Array SR308i-p Gen11",
  "BlockSizeBytes": 512,
  "CapacityGB": 400,
  "CapacityLogicalBlocks": 781422768,
  "CapacityMiB": 381554,
  "CarrierApplicationVersion": "11",
  "CarrierAuthenticationStatus": "OK",
  "CurrentTemperatureCelsius": 41,
  "DiskDriveStatusReasons": [
    "None"
  ],
  "DiskDriveUse": "Raw",
  "EncryptedDrive": false,
  "FirmwareVersion": {
    "Current": {
      "VersionString": "HPD3"
    }
  },
  "InterfaceSpeedMbps": 12000,
  "InterfaceType": "SAS",
  "LegacyBootPriority": "Primary",
  "Location": "1I:3:4",
  "LocationFormat": "ControllerPort:Box:Bay",
  "MaximumTemperatureCelsius": 46,
  "MediaType": "SSD",
  "Model": "MO0400JEFPA",
  "PowerOnHours": 5943,
  "SSDEnduranceUtilizationPercentage": 0,
  "SerialNumber": "0QV2MS1A",
  "Status": {
    "State": "Enabled",
    "Health": "OK"
  },
  "UncorrectedReadErrors": 0,
  "UncorrectedWriteErrors": 0
}
</pre>

> To return a JSON formatted response regarding the settings and attributes of the selected volume on the selected controller include the `--controller` option specifying the controller and the `--ldrive` option specifying the volume number in brackets.

<pre>
iLOrest > <span style="color: #01a982; ">storagecontroller --controller=0 --ldrive=1 -j</span>
{
  "Controller": "Slot=3 - HPE Smart Array SR308i-p Gen11",
  "Accelerator": "ControllerCache",
  "BlockSizeBytes": 512,
  "CapacityBlocks": 1172058032,
  "CapacityGiB": 558,
  "DataDrives": [
    "1I:3:2"
  ],
  "DriveLocationFormat": "ControllerPort:Box:Bay",
  "LegacyBootPriority": "None",
  "LogicalDriveName": "004D56ABPEYHC0ARH951TK A39C",
  "LogicalDriveNumber": 1,
  "ParityGroupCount": 0,
  "Raid": "Raid0",
  "SpareDrives": [],
  "SpareRebuildMode": null,
  "StripSizeBytes": 262144,
  "StripeSizeBytes": 262144,
  "VolumeUniqueIdentifier": "600508B1001C599DE361257397F69972"
}
</pre>



<p class="fake_header">Syntax</p>

Smartarray *[Optional Parameters]*

<p class="fake_header">Description</p>

Discovers all storage controllers installed in the server and managed by the SmartStorage.  

<p class="fake_header">Parameters</p>

- **-h, --help**

Including the help flag will display help for the command.

- **--storageid=STORAGEID, --storage_id=STORAGEID**

Use this flag to select the corresponding storage id. This is applicable for iLO 6 only.

- **--controller=CONTROLLER**

Use this flag to select the corresponding controller.

- **--volumes**

Use this flag to list the volumes.

- **--volume=VOLUMEID**

Use this flag to print volume information specifying volume id.

- **-j, --json**

Use this flag to output in JSON format.

- **--physicaldrives**

Use this flag to return the physical drives for the controller selected.

- **--pdrive=PDRIVE_LOCATION**

Use this flag to select the corresponding physical disk.

<p class="fake_header">Login Parameters</p>

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. Using this flag when not logged in will have no effect.

<p class="fake_header">Input</p>
None

<p class="fake_header">Output</p>
None
