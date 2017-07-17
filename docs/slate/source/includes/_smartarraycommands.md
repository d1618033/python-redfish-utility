## Smart Arrary Commands



### Clearcontrollerconfig command

> Clearcontrollerconfig example commands:


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

Use this flag to sanitize all physical drives on a controller.


#### Inputs



#### Outputs



### Createlogicaldrive command

> Createlogicaldrive example commands:


#### Syntax

createlogicaldrive *[Optional Parameters]*

#### Description
Creates a new logical drive on the selected controller.



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

- **--accelerator-type=ACCELERATORTYPE*

Optionally include to choose the accelerator type.

- **--legacy-boot=LEGACYBOOT**

Optionally include to choose the legacy boot priority (usable in custom creation only).

- **--capacityBlocks=CAPACITYBLOCKS**

Optionally include to choose the capacity in blocks (use -1 for max size, usable in custom creation only).

- **--paritygroupcount=PARITYGROUP*

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



#### Outputs

### Deletelogicaldrive command

> Deletelogicaldrive example commands:


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


#### Inputs



#### Outputs


### Drivesanitize command

> Drivesanitize example commands:


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



#### Outputs


### Factoryresetcontroller command

> Factoryresetcontroller example commands:


#### Syntax

factoryresetcontroller *[Optional Parameters]*

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


#### Inputs



#### Outputs



### Smartarray command

> Smartarray example commands:


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



#### Outputs




