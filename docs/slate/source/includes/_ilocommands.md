## iLO Commands

This section includes advanced functions for manipulating iLO using the RESTful Interface Tool. These commands include operations such as turning the server hardware on and off, resetting iLO, and updating firmware.

iLO commands that are supported for a specific HPE server generation:
+ certificate: Gen10 with limited functionality for Gen9
+ fwintegritycheck: Gen10
+ iloclone: Gen10
+ sigrecompute: Gen9

### Certificate command

<aside class="notice">
<ul>
<li>Please make sure the order of arguments is correct. The parameters are extracted base on their position in the arguments list.</li>
<li>Use the singlesignon command to import single sign on certificates.</li>
</ul>
</aside>

> Certificate example commands:

> Generate an https certificate signing request.

> ![Certificate Example 1](images/examples/certificate_ex1.png "Certificate example 1")


> Import auth CA certificate.

> ![Certificate Example 2](images/examples/certificate_ex2.png "Certificate example 2")


> Import auth CRL certificate.

> ![Certificate Example 3](images/examples/certificate_ex3.png "Certificate example 3")



#### Syntax

certificate *[Optional Parameters]*

#### Description

Command for importing iLO and login authorization certificates, and generating iLO certificate signing requests.


#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-f FILENAME, --filename=FILENAME**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.


#### Inputs
None



#### Outputs
None

### Clearrestapistate command

> Clearrestapistate example commands:

> Clear the persistent RESTful API state.

> ![Clearrestapistate Example 1](images/examples/clearrestapistate_ex2.png "Clearrestapistate example 1")



#### Syntax

clearrestapistate *[Optional Parameters]*

#### Description
Clear the persistent RESTful API state.


#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.


#### Inputs
None


#### Outputs
None

### Disableilofunctionality command

> Disableilofunctionality example commands:

> Disable iLO functionality on the current logged in server.

> ![Disableilofunctionality Example 1](images/examples/disableilofunctionality_ex1.png "Disableilofunctionality example 1")  



#### Syntax

disableilofunctionality *[Optional Parameters]*

#### Description
Disable iLO functionality on the current logged in server.


#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.


#### Inputs
None


#### Outputs
None


### Eskm command

> Eskm example commands:

> Clear the ESKM logs.

> ![Eskm Example 1](images/examples/eskm_ex1.png "Eskm example 1")


> Test the ESKM connections.

> ![Eskm Example 2](images/examples/eskm_ex2.png "Eskm example 2")

#### Syntax

eskm *[Optional Parameters]*

#### Description
Command for all ESKM available actions.


#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.


#### Inputs
None


#### Outputs
None


### Factorydefaults command

> Factorydefaults example commands:

> Reset iLO to factory defaults in the current loggen in server.

> ![Factorydefaults Example 1](images/examples/factorydefaults_ex1.png "Factorydefaults example 1")


#### Syntax

factorydefaults *[Optional Parameters]*

#### Description
Reset iLO to factory defaults in the current logged in server.


#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.


#### Inputs
None



#### Outputs
None


### Fwintegritycheck command

> Fwintegritycheck example commands:

> Perform a firmware integrity check on the current logged in server.

> ![Fwintegritycheck Example 1](images/examples/fwintegritycheck_ex1.png "Fwintegritycheck example 1")


#### Syntax

fwintegritycheck *[Optional Parameters]*

#### Description
Perform a firmware integrity check on the current logged in server.


#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.


#### Inputs
None


#### Outputs
None


### Reboot command

> Reboot example commands:

> If the server is currently off, the reboot On command can be used to turn the server on. The reboot command logs the user out of the server.

> ![Reboot Example 1](images/examples/reboot_ex1.png "Reboot example 1")


> If the server has been turned on, the reboot ForceOff command can be used to turn the server off immediately. 

<aside class="notice">
The reboot command logs the user out of the server.
</aside>

> ![Reboot Example 2](images/examples/reboot_ex2.png "Reboot example 2")


> If the server is currently on, the reboot ForceRestart command can be used to turn the server off immediately and then start again. 


> ![Reboot Example 3](images/examples/reboot_ex3.png "Reboot example 3")



> If the server is currently on, the reboot Nmi command can be used to generate a non-maskable interrupt to cause an immediate system halt. 


```
ilorest > reboot Nmi -username -p password --url=xx.xx.xx.xx
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext

The session will be now be terminated.
Please wait for the server to boot completely its operations to login again.
Generating interrupt in 3 seconds...
The operation completed successfully.
Logging session out.
```

> The reboot PushPowerButton command can be used to simulate physically pressing the power button on the server. If the server is off, this command will turn the server on. If the server is on, this command will turn the server off. 


> ![Reboot Example 4](images/examples/reboot_ex4.png "Reboot example 4")


#### Syntax

reboot *[Reboot Type] [Optional Parameters]*

#### Description

Run this command to turn the system on, perform an immediate non-graceful shutdown, perform an immediate non-graceful shutdown followed by a restart of the system, generate a non-maskable interrupt and cause an immediate system halt, or simulate the pressing of the physical power button on the system.

#### Parameters

- **On**

Use this reboot type to turn the system on. If the system is already on, this has no effect.

- **ForceOff**

Use this reboot type to cause the system to perform an immediate non-graceful shutdown.

- **ForceRestart**

Use this reboot type to perform an immediate non-graceful shutdown followed by a restart of the system.

- **Nmi**

Use this reboot type to generate a non-maskable interrupt to cause an immediate system halt.

- **PushPowerButton**

Use this reboot type to simulate the pressing of the physical power button on this system.

- **Press**

Simulates the pressing of the physical power button on this system.

- **PressAndHold**

Simulates pressing and holding of the power button on this systems.

- **ColdBoot**

Immidiately removes power from the server, followed by a restart of the system.

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--includelogs**

You can optionally choose to set the **includelogs** flag. Doing so will include logs in the data retrieval process.

- **--confirm**

Optionally include to request user confirmation for reboot.

#### Inputs

None

#### Outputs

None

### Sendtest command

> Sendtest example commands:

> Send syslog test to the current logged in server.

> ![Sendtest Example 1](images/examples/sendtest_ex1.png "Sendtest example 1")


> Send alert mail test to the current logged in server.

> ![Sendtest Example 2](images/examples/sendtest_ex2.png "Sendtest example 2")


> Send SNMP test alert to the current logged in server.

> ![Sendtest Example 3](images/examples/sendtest_ex3.png "Sendtest example 3")


#### Syntax

sendtest *[Command] [Optional Parameters]*

#### Description

Command for sending various tests to iLO.



#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.


#### Inputs
None


#### Outputs
None


### Serverlogs command

> Serverlogs example commands:

> Download the AHS logs from the logged in server.

> ![Serverlogs Example 1](images/examples/serverlogs_ex1.png "Serverlogs example 1")


> Insert customized string if required for AHS log to be downloaded. (AHS LOGS ONLY FEATURE IN REMOTE MODE)

> ![Serverlogs Example 2](images/examples/serverlogs_ex2.png "Serverlogs example 2")


> Clear the AHS logs from the logged in server.

> ![Serverlogs Example 3](images/examples/serverlogs_ex3.png "Serverlogs example 3")


> Download the IEL logs from the logged in server.

> ![Serverlogs Example 4](images/examples/serverlogs_ex4.png "Serverlogs example 4")


> Download the IML logs from the logged in server.

> ![Serverlogs Example 5](images/examples/serverlogs_ex5.png "Serverlogs example 5")


> Insert entry in the IML logs from the logged in server. (IML LOGS ONLY FEATURE)

> ![Serverlogs Example 6](images/examples/serverlogs_ex6.png "Serverlogs example 6")


#### Syntax

serverlogs *[Log_Selection] [Optional Parameters]*

#### Description

Download and perform log operations.

<aside class="warning">Please use the default name when downloading AHS logs, do not include the -f parameter.</aside>

#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-f FILENAME, --filename=FILENAME**

Use this flag if you wish to use a different filename than the default one. The default filename is ilorest.json.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--filter=FILTER**

Optionally set a filter value for a filter attribute. This uses the provided filter for the currently selected type. 

<aside class="notice">
Use this flag to narrow down your results. For example, selecting a common type might return multiple objects that are all of that type. If you want to modify the properties of only one of those objects, use the filter flag to narrow down results based on properties Usage: --filter [ATTRIBUTE]=[VALUE].
</aside>

- **-j, --json**

Optionally include this flag if you wish to change the displayed output to JSON format. Preserving the JSON data structure makes the information easier to parse.

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. Using this flag when not logged in will have no effect.

- **--selectlog=SERVICE**

Read log from the given log service. Options: IML, IEL or AHS.


- **-c, --clearlog, -m MAINMES, --maintenancemessage=MAINMES**

Clears the logs for a the selected option. Maintenance message to be inserted into the log. (IML LOGS ONLY FEATURE)

- **--customiseAHS=CUSTOMISEAHS**
 
Allows customized AHS log data to be downloaded.

- **--downloadallahs**

Allows complete AHS log data to be downloaded.

- **--directorypath=DIRECTORYPATH**
Directory path for the ahs file.

- **---m MAINMES, --maintenancemessage=MAINMES**

Maintenance message to be inserted into the log. (IML LOGS ONLY FEATURE)

- **--mpfile=MPFILENAME**

Use the provided filename to obtain server information.

- **-o OUTDIRECTORY, --outputdirectory=OUTDIRECTORY**

Use the provided directory to output data for multiple server downloads.

- **--mplog=MPLOG**

Used to indicate the logs to be downloaded on multiple servers. Allowable values: IEL, IML, AHS, all or combination of any two.


#### Inputs
None


#### Outputs
None



### iLOReset command

> iLOReset example commands:

> Use this command to reset iLO on the currently logged in server. This will turn iLO off and on again.

> ![iLOReset Example 1](images/examples/iloreset_ex1.png "iLOReset example 1")

#### Syntax

iloreset *[Optional Parameters]*

#### Description

Run this command to reset iLO on the currently logged in server.

#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.


#### Inputs

None

#### Outputs

None

### Firmware update command

> Firmware update example commands:

> The firmwareupdate command updates the firmware for iLO. After the server was logged into, the firmware update at the given location was used to update the firmware. After the update was completed, iLO was reset and the session was terminated. 

<aside class="notice">
iLO does not always reset after a firmware update.
</aside>

> ![Firmware update Example 1](images/examples/firmwareupdate_ex1.png "Firmware update example 1")


#### Syntax

Firmwareupdate *[URI] [Optional Parameters]*

#### Description

Use this command to update the firmware via URI.

<aside class="notice">The firmware update command is only supported in <b>iLO 2.20</b> or higher.</aside>

#### Parameters

- **URI**

Point the **firmwareupdate** command towards the .bin file that holds the file for the firmware update.

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--includelogs**

You can optionally choose to set the **includelogs** flag. Doing so will include logs in the data retrieval process.

- **--tpmenabled**

Use this flag if the server you are currently logged into has a TPM chip installed.

#### Inputs

File

Input a URI pointing to a `.bin` file to perform the `firmwareupdate` command. The .bin file should hold the file needed to perform the firmware update.

#### Outputs

None

### Iloaccounts command

> Iloaccounts example commands:

> Add an iLO user account the current logged in server.

> ![Iloaccounts Example 1](images/examples/iloaccounts_ex1.png "Iloaccounts example 1")


> Get the ID and login name information for the iLO user accounts.

> ![Iloaccounts Example 2](images/examples/iloaccounts_ex2.png "Iloaccounts example 2")


> Change the password of an account.

> ![Iloaccounts Example 3](images/examples/iloaccounts_ex3.png "Iloaccounts example 3")


> Delete an iLO account.

> ![Iloaccounts Example 4](images/examples/iloaccounts_ex4.png "Iloaccounts example 4")



#### Syntax

iloaccounts *[COMMAND] [OPTIONS]*

#### Description
- LOGINNAME:  The account name, not used to login.
- USERNAME: The account username name, used to login. 
- PASSWORD:  The account password, used to login.
- Id: The number associated with an iLO user account.

	<aside class="notice">
    Please make sure the order of arguments is correct. The
	parameters are extracted based on their position in the arguments list.
	Only privileges available to the logged in account can be set to the new account.
    </aside>



#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--noremoteconsolepriv**

Optionally include this flag if you wish to set the remote console privileges to false.

- **--noiloconfigpriv**     

Optionally include this flag if you wish to set the ilo config privileges to false.

- **--novirtualmediapriv**  

Optionally include this flag if you wish to set the virtual media privileges to false.

- **--nouserconfigpriv**    

Optionally include this flag if you wish to set the userconfig privileges to false.

- **--novirtualprpriv**     

Optionally include this flag if you wish to set the virtual power and reset privileges to false.

- **--nologinpriv**         

Optionally include this flag if you wish to set the login privileges to false.

- **--nobiosconfigpriv**    

Optionally include this flag if you wish to set the host BIOS config privileges to false. Only available on gen10 servers.

- **--nonicconfigpriv**     

Optionally include this flag if you wish to set the host NIC config privileges to false. Only available on gen10 servers.

- **--nohoststorageconfigpriv** 

Optionally include this flag if you wish to set the host storage config privileges to false. Only available on gen10 servers.

- **--nosysrecoveryconfigpriv** 

Optionally include this flag if you wish to set the system recovery config privileges to false. Only available on gen10 servers.


#### Inputs
None


#### Outputs
None


### Iloclone command

> Iloclone  example commands:

> Create a clone file from the current logged in server.

> ![Iloclone Example 1](images/examples/iloclone_ex1.png "Iloclone example 1")


> Load the saved clone file to currently logged in server.

> ![Iloclone Example 2](images/examples/iloclone_ex2.png "Iloclone example 2")


#### Syntax

iloclone *[Optional Parameters]*

#### Description

Clone the iLO config of the currently logged in server and copy it to the server in the arguments.

<aside class="notice">
This command is only available in local mode. During clone load, login using an iLO account with full privileges (such as the Administrator account) to ensure all items are cloned successfully.
</aside>


#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-f FILENAME, --filename=FILENAME**
                        
Use this flag if you wish to use a different filename than the default one. The default filename is clone.json.

- **--ssocert=SSOCERT**

Use this flag during iloclone save if you wish to import a SSO certificate to the server to be cloned. Add the sso cert file or URL to be used to the working directory before running clone load.

- **--httpscert=HTTPSCERT**

Use this flag during iloclone save if you wish to import a SSO certificate to the server to be cloned. Add the https cert file to be used to the working directory before running clone load.

- **--uniqueitemoverride**

Override the measures stoppping the tool from writing over items that are system unique. 

- **-e ENCRYPTION, --encryption=ENCRYPTION**

Optionally include this flag to encrypt/decrypt a file using the key provided.


#### Inputs
None


#### Outputs
None


### Ilofederation command

<aside class="notice">
Please make sure the order of arguments is correct. The parameters are extracted based on their position in the arguments list. The federation key must be 8 characters or greater.
</aside>

> Ilofederation example commands:

> Descriptions:
> +  *FEDERATIONNAME*: The name (Id) of the federation group. 
> +  *KEY*:  The key required to join the federation.

> Add an iLO federation group to the current logged in server.

> ![Ilofederation Example 1](images/examples/ilofederation_ex1.png "Ilofederation example 1")


> See a list of federations on the system.

> ![Ilofederation Example 2](images/examples/ilofederation_ex2.png "Ilofederation example 2")  


> Change the key of an iLO federation group.

> ![Ilofederation Example 3](images/examples/ilofederation_ex3.png "Ilofederation example 3")


> Delete an iLO federation group.

> ![Ilofederation Example 4](images/examples/ilofederation_ex4.png "Ilofederation example 4")





#### Syntax

ilofederation *[Optional Parameters]*

#### Description
Adds / deletes an iLO federaion group on the currently logged in server.



#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--noremoteconsolepriv**

Optionally include this flag if you wish to set the remote console privileges to false.

- **--noiloconfigpriv**

Optionally include this flag if you wish to set the ilo config privileges to false.

- **--novirtualmediapriv**  

Optionally include this flag if you wish to set the virtual media privileges to false.

- **--nouserconfigpriv**    

Optionally include this flag if you wish to set the userconfig privileges to false.

- **--novirtualprpriv**     

Optionally include this flag if you wish to set the virtual power and reset privileges to false.

- **--nologinpriv**

Optionally include this flag if you wish to set the login privileges to false.

- **--nobiosconfigpriv**

Optionally include this flag if you wish to set the host BIOS config privileges to false. Only available on gen10 servers.

- **--nonicconfigpriv**

Optionally include this flag if you wish to set the host NIC config privileges to false. Only available on gen10 servers.
 
 - **--nohoststorageconfigpriv** 
 
 Optionally include this flag if you wish to set the host storage config privileges to false. Only available on gen10 servers.
 
 - **--nosysrecoveryconfigpriv**
 
 Optionally include this flag if you wish to set the system recovery config privileges to false. Only available on gen10 servers.


#### Inputs
None


#### Outputs
None



### Ilolicense command

> Ilolicense example commands:

> Set an iLO license on the current logged in server.

> ![Ilolicense Example 1](images/examples/ilolicense_ex1.png "Ilolicense example 1")




#### Syntax

ilolicense *[LICENSE_KEY] [OPTIONS]*

#### Description
Set an iLO license on the current logged in server.



#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

#### Inputs
None


#### Outputs
None


### Serverstate command

> Serverstate example commands:

> Here we use the serverstate command without any parameters, which tells use the current state of the server.

> ![Serverstate Example 1](images/examples/serverstate_ex1.png "Serverstate example 1")


> Here, serverstate is used along with login information to login and return the serverstate in one step.

> ![Serverstate Example 2](images/examples/serverstate_ex2.png "Serverstate example 2")



#### Syntax

serverstate *[Optional Parameter]*

#### Description

Returns the current state of the server.

#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

#### Inputs

None

#### Outputs

None


### Sigrecompute command

> Sigrecompute  example commands:

> Recalculate the signature on the computers configuration.

> ![Sigrecompute Example 1](images/examples/sigrecompute_ex1.png "Sigrecompute example 1")


> Log in to the computer and recalculate the signature.

> ![Sigrecompute Example 2](images/examples/sigrecompute_ex2.png "Sigrecompute example 2")




#### Syntax

sigrecompute *[OPTIONS]*

#### Description
Recalculate the signature on the computers configuration.

<aside class="notice">
The sigrecompute command is not available on Redfish systems.
</aside>


#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

#### Inputs
None


#### Outputs
None 


### Singlesignon command

> Singlesignon  example commands:

> Delete a specific SSO record.

> ![Singlesignon Example 1](images/examples/singlesignon_ex1.png "Singlesignon example 1")


> Delete all SSO records.

> ![Singlesignon Example 2](images/examples/singlesignon_ex2.png "Singlesignon example 2")


> Import a DNS name.

> ![Singlesignon Example 3](images/examples/singlesignon_ex3.png "Singlesignon example 3")


> Import certificate from URI or file.

> ![Singlesignon Example 4](images/examples/singlesignon_ex4.png "Singlesignon example 4")


#### Syntax

Singlesignon *[OPTIONS]*

#### Description

Command for all single sign on available actions.



#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

#### Inputs
None


#### Outputs
None 


### Virtualmedia command

> Virtualmedia  example commands:

> Insert virtual media and set to boot on next restart.

> ![Virtualmedia Example 1](images/examples/virtualmedia_ex1.png "Virtualmedia example 1")  


> Run without arguments to view the available virtual media sources.

> ![Virtualmedia Example 2](images/examples/virtualmedia_ex2.png "Virtualmedia example 2") 


> Remove current inserted media.

> ![Virtualmedia Example 3](images/examples/virtualmedia_ex3.png "Virtualmedia example 3")


#### Syntax

virtualmedia *[ID] [URI] [OPTIONS]*

#### Description

Command for inserting and removing virtual media.



#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--reboot=REBOOT**

Use this flag to perform a reboot command function after completion of operations.  For help with parameters and descriptions regarding the reboot flag, run help reboot.

- **--remove**

Use this flag to remove the media from the selection.

- **--bootnextreset**

Use this flag if you wish to boot from the image on next server reboot. 

<aside class="notice">
The image will be ejected automatically on the second server reboot so that the server does not boot to this image twice.
</aside>

#### Inputs
None 

#### Outputs
None 
