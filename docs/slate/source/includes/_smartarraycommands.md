## Smart Arrary Commands

The Smart Array commands are designed for use with HPE Gen10 servers.

<aside class="notice">
<ul>
<li>A Smart Array Capable controller capable of communicating with iLO is required.</li>
<li>Logical volume creation is determined on initialization of the controller at system startup. Therefore, invalid entries can only be determined after reboot.
</ul>
</aside>

### SmartArray command

> To list all available smart array controllers run the command without arguments.

<pre>
ilorest > <font color="#01a982">smartarray</font>
[1]&#58; Slot 0
</pre>

> To list all Existing Volume Unique Identifier's for logical drives for all controllers run the command including the `--logicaldrives` option. Drives which are pending will instead show "Pending Drive" for the Volume Unique Identifier (this will be available after the system has been rebooted and the drive has been successfully created.). The information is presented such that the controller slot number is noted first, followed by all associated logical drives to that controller.

<pre>
iLOrest > login
Discovering data...Done
ilorest > <font color="#01a982">smartarray --logicaldrives</font>
[1]&#58; Slot 0
Logical Drives&#58;
[1]&#58; 600508B1001C599DE361257397F69972
[2]&#58; Pending drive
[3]&#58; Pending drive
</pre>

> To list all physical drives for all available controllers, run the command with the `--physicaldrives` option. The controller will be provided first followed by drive information (as associated to that controller). Drive information is in the format, [Controller Port (Internal)]:[Box]:[Bay]. 

<pre>
iLOrest > login
Discovering data...Done
ilorest > <font color="#01a982">smartarray --physicaldrives</font>
[1]&#58; Slot 0
Physical Drives&#58;
[1]&#58; 1I:3:4
[2]&#58; 1I:3:3
[3]&#58; 1I:3:2
[4]&#58; 1I:3:1
[5]&#58; 2I:3:5
[6]&#58; 2I:3:6
</pre>

> To return a JSON formatted response including controller settings, as well as physical and logical drives information on the selected controller, include the `--controller` option followed by the number in brackets associated to the controller.

<pre> 
ilorest > <font color="#01a982">smartarray --controller=1</font>
{
  "CurrentParallelSurfaceScanCount": 1, 
  "DataGuard": "Disabled", 
  "DegradedPerformanceOptimization": "Disabled", 
  "DriveWriteCache": "Disabled", 
  "ElevatorSort": "Enabled", 
  "EncryptionConfiguration": "None", 
  "EncryptionEULA": null, 
  "ExpandPriority": "Medium", 
  "FlexibleLatencySchedulerSetting": "Default", 
  "InconsistencyRepairPolicy": "Disabled", 
  "Location": "Slot 0", 
  "LocationFormat": "PCISlot", 
  "LogicalDrives": [
    {
      "CapacityBlocks": 1172058032, 
      "ParityGroupCount": 0, 
      "SpareRebuildMode": null, 
      "Raid": "Raid0", 
      "LogicalDriveNumber": 1, 
      "Accelerator": "ControllerCache", 
      "BlockSizeBytes": 512, 
      "CapacityGiB": 558, 
      "SpareDrives": [], 
      "DriveLocationFormat": "ControllerPort:Box:Bay", 
      "LogicalDriveName": "004D56ABPEYHC0ARH951TK A39C", 
      "VolumeUniqueIdentifier": "600508B1001C599DE361257397F69972", 
      "StripeSizeBytes": 262144, 
      "StripSizeBytes": 262144, 
      "DataDrives": [
        "1I:3:2"
      ]
  ...
</pre>

> To return a JSON formatted response regarding the settings and attributes of the selected physical drive on the selected controller include the `--controller` option specifying the controller and the `--pdrive` option specifying the physical drive number in brackets.

<pre>
ilorest > <font color="#01a982">smartarray --controller=1 --pdrive=1</font>
{
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

> To return a JSON formatted response regarding the settings and attributes of the selected logical drive on the selected controller include the `--controller` option specifying the controller and the `--ldrive` option specifying the logical drive number in brackets.

<pre>
iLOrest > <font color="#01a982">smartarray --controller=1 --ldrive=1</font>
{
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



#### Syntax

Smartarray *[Optional Parameters]*

#### Description

Discovers all storage controllers installed in the server and managed by the SmartStorage.  




#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--controller=CONTROLLER**

Use this flag to select the corresponding controller.

- **--physicaldrives**

Use this flag to return the physical drives for the controller selected.

- **--logicaldrives**

Use this flag to return the logical drives for the controller selected.

- **--pdrive=PDRIVE**

Use this flag to select the corresponding physical disk.

- **--ldrive=LDRIVE**

Use this flag to select the corresponding logical disk.


#### Inputs
None 

#### Outputs
None 



### Clearcontrollerconfig command

> Clearcontrollerconfig example commands:

<aside class="notice">
By default all available smart array controllers are included. Use '--controller' to target a specific index or slot for clearing controller configuration.
</aside>

> To clear a controller configuration run the command including the `--controller` option specifying the controller to clear.

<pre> 
ilorest > <font color="#01a982">clearcontrollerconfig --controller=1</font>
One or more properties were changed an will not take effect until system is reset.
</pre>

> To clear controller configuration on all available smart array controllers use `--all`.

<pre> 
ilorest > <font color="#01a982">clearcontrollerconfig --all</font>
Are you sure you would like to clear all available smart array controller configurations? (y/n) <font color="#01a982"> y </font>
One or more properties were changed an will not take effect until system is reset.
</pre>

#### Syntax
clearcontrollerconfig *[Optional Parameters]*

#### Description
Clears smart array controller configuration.


#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--controller=CONTROLLER**

Use this flag to select the corresponding controller.

- **--all**

Use this flag to factory reset all controllers.

- **--force**

Use this flag to override the "are you sure?" text when clearing configurations on all available smart array controllers. 


#### Inputs
None



#### Outputs
None



### Createlogicaldrive command

<aside class="notice">
The createlogicaldrive command requires a reboot before creating the logical drives. If the drives are not present after a full reboot, run the results command to check for errors in the configuration.
</aside>

> Createlogicaldrive example commands:

> To create a quick logical drive run the command with the following arguments: The type of creation as quickdrive, the raid level, the number of drives to use, the type of drive to use, the drive interface type, and the drive location. Also include the `--controller` option selecting the controller the drive will be created on. See the options list for possible values of these and more.

<pre> 
ilorest > <font color="#01a982">createlogicaldrive quickdrive Raid0 2 HDD SATA Internal --controller=1</font>
One or more properties were changed an will not take effect until system is reset.
</pre>

> To create a custom logical drive run the command with the following arguments: The type of creation as customdrive, the raid level, and the physicaldrive index(s). Also include the `--controller` option selecting the controller the drive will be created on. See the options list for possible values of these and more.

<pre> 
iLOrest > login
Discovering data...Done
ilorest > <font color="#01a982">createlogicaldrive customdrive Raid5 2,3,4,5,6 --controller=1 --name=ANewLogicalDrive --spare-drives=2 --capacityGiB=100 --legacy-boot=Primary --accelerator-type=ControllerCache --spare-type=Dedicated</font>
One or more properties were changed an will not take effect until system is reset.
</pre>

#### Syntax

createlogicaldrive *[Optional Parameters]*

#### Description
Creates a new logical drive on the selected controller.

Options:
- raid-level:             Raid0, Raid1, Raid1ADM, Raid10, Raid10ADM, Raid5, Raid50, Raid6, Raid60
- media-type:             SSD,HDD
- interface-type:         SAS, SATA
- drive-location:         Internal, External
- --spare-type:           Dedicated, Roaming
- --accelerator-type:     ControllerCache, IOBypass, None
- --paritytype:           Default, Rapid


#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--controller=CONTROLLER**

Use this flag to select the corresponding controller.

- **-n DRIVENAME, --name=DRIVENAME**

Optionally include to set the drive name (usable in custom creation only).

- **--spare-drives=SPAREDRIVES**

Optionally include to set the spare drives by the physical drive's index (usable in custom creation only).

- **--capacityGiB=CAPACITYGIB**

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


#### Inputs
None


#### Outputs
None 

### Deletelogicaldrive command

> Deletelogicaldrive example commands:



> To delete multiple logical drives by index include the index of the drive you wish to delete. Also include the `--controller` option specifying the controller to use. You can specify multiple drives as well as a comma separated list.

<aside class="notice">
A Volume Unique Identifier must be available to delete a logical drive. Pending drives may not be deleted.
</aside>

<pre> 
ilorest > <font color="#01a982">deletelogicaldrive --controller=1 1</font>
Are you sure you would like to continue deleting drive 004D56ABPEYHC0ARH951TK A39C? (y/n)
Setting logical drive 004D56ABPEYHC0ARH951TK A39C for deletion
One or more properties were changed and will not take effect until system is reset.
</pre>


> To delete all logical drives on a controller include the`--controller` option specifying the controller to perform the operation on and the `--all` option.

<pre> 
iLOrest > login
Discovering data...Done
ilorest > deletelogicaldrive --controller=1 <font color="#01a982">--all</font>
[200] The operation completed successfully.
</pre>



#### Syntax

deletelogicaldrive *[Optional Parameters]*

#### Description
Deletes logical drives from the selected controller.




#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--controller=CONTROLLER**

Use this flag to select the corresponding controller.

- **--all**

Use this flag to delete all logical drives on a controller.

- **--force**

Use this flag to override the "are you sure?" text when deleting a logical drive. 


#### Inputs
None 


#### Outputs
None 


### Drivesanitize command

> Drivesanitize example commands:

> To sanitize a physical drive pass its index along with the `--controller` option to dpecify which controller to perform the operation on.

<pre> 
ilorest > drivesanitize --controller=1 <font color="#01a982">1</font>
Setting physical drive 1I:3:4 for sanitization
One or more properties were changed and will not take effect until system is reset.
Sanitization will occur on the next system reboot.
</pre>

> To sanitize multiple physical drives pass the indexes as a comma separated list along with the `--controller` option to dpecify which controller to perform the operation on.

<pre> 
ilorest > drivesanitize --controller=1 <font color="#01a982">2,3,4</font>
Setting physical drive 1I:3:3 for sanitization
Setting physical drive 1I:3:2 for sanitization
Setting physical drive 1I:3:1 for sanitization
One or more properties were changed and will not take effect until system is reset.
Sanitization will occur on the next system reboot.
</pre>


#### Syntax

drivesanitize *[Optional Parameters]*

#### Description
Erase/Sanitizes physical drives.




#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--controller=CONTROLLER**

Use this flag to select the corresponding controller.

- **--reboot**

Include this flag to perform a coldboot command function after completion of operations and monitor sanitization.

- **--all**

Use this flag to sanitize all physical drives on a controller.



#### Inputs
None 

#### Outputs
None 


### Factoryresetcontroller command

> Factoryresetcontroller example commands:

<aside class="notice">
By default all available smart array controllers are included. Use '--controller' to target a specific index or slot for a factory reset.
</aside>

> To factory reset a controller run this command and specify it's index with the `--controller` option.

<pre> 
ilorest > <font color="#01a982">factoryresetcontroller --controller=1</font>
One or more properties were changed and will not take effect until system is reset.
</pre>

> To factory reset all controllers `--all` option.

<pre> 
ilorest > <font color="#01a982">factoryresetcontroller --all</font>
Are you sure you would like to factory reset all available smart array controllers? (y/n) <font color="#01a982">y</font>
[1]: Slot 0 - has been reset to factory defaults.
[2]: Slot 1 - has been reset to factory defaults.
[3]: Slot 3 - has been reset to factory defaults.
</pre>

#### Syntax

factoryresetcontroller *[Optional Parameters]*

#### Description
Restores a controller to factory defaults.




#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--controller=CONTROLLER**

Use this flag to select the corresponding controller.

- **--all**

Use this flag to factory reset all controllers.

- **--force**

Use this flag to override the "are you sure?" text when performing a factory reset to selected smart array controllers. 


#### Inputs
None 


#### Outputs
None 
