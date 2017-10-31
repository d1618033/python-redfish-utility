## Smart Arrary Commands

The Smart Array commands are designed for use with HPE Gen10 servers.



### Clearcontrollerconfig command

> Clearcontrollerconfig example commands:

> To clear a controller config.

> ![Clearcontrollerconfig 1](images/examples/clearcontrollerconfig_ex1.png "Clearcontrollerconfig example 1")


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
None



#### Outputs
None



### Createlogicaldrive command

<aside class="notice">
The createlogicaldrive command requires a reboot before the logical drives can be created. If the drives are not present after a full reboot, run the results command to check for errors in the configuration
</aside>

> Createlogicaldrive example commands:

> To create a quick logical drive.

> ![Createlogicaldrive 1](images/examples/createlogicaldrive_ex1.png "Createlogicaldrive example 1")


> To create a custom logical drive.

> ![Createlogicaldrive 2](images/examples/createlogicaldrive_ex2.png "Createlogicaldrive example 2")


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
None


#### Outputs
None 

### Deletelogicaldrive command

> Deletelogicaldrive example commands:

> To delete multiple logical drives by index.

> ![Deletelogicaldrive Example 1](images/examples/deletelogicaldrive_ex1.png "Deletelogicaldrive example 1")


> To delete all logical drives on a controller.

> ![Deletelogicaldrive Example 2](images/examples/deletelogicaldrive_ex2.png "Deletelogicaldrive example 2")


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

> To sanitize a physical drive by index.

> ![Drivesanitize Example 1](images/examples/drivesanitize_ex1.png "Drivesanitize example 1")


> To sanitize multiple drives by index.

> ![Drivesanitize Example 2](images/examples/drivesanitize_ex2.png "Drivesanitize example 2")



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

> To factory reset a controller by index.

> ![Factoryresetcontroller Example 1](images/examples/factoryresetcontroller_ex1.png "Factoryresetcontroller example 1")


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
None 


#### Outputs
None 



### Smartarray command

> Smartarray example commands:

> Run without arguments for the current list of smart array controllers.

> ![Smartarray 1](images/examples/smartarray_ex1.png "Smartarray example 1")


> To get more details on a specific controller select it by index.

> ![Smartarray 2](images/examples/smartarray_ex2.png "Smartarray example 2")


> Get a list of all physical drives for the each controller.

> ![Smartarray 3](images/examples/smartarray_ex3.png "Smartarray example 3")


> Get details about a specific drive for a specific controller.

> ![Smartarray 4](images/examples/smartarray_ex4.png "Smartarray example 4")

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



