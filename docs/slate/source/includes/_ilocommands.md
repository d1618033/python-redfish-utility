## iLO Commands

This section includes advanced functions for manipulating iLO using the RESTful Interface Tool. These commands include operations such as turning the server hardware on and off, resetting iLO, and updating firmware.

### Certificate command

> Certificate example commands:


#### Syntax

certificate *[Optional Parameters]*

#### Description



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



#### Outputs

### Clearrestapistate command

> Clearrestapistate example commands:


#### Syntax

clearrestapistate *[Optional Parameters]*

#### Description
Clear the persistent REST API state.


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



#### Outputs

### Disableilofunctionality command

> Disableilofunctionality example commands:


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



#### Outputs


### Eskm command

> Eskm example commands:


#### Syntax

eskm *[Optional Parameters]*

#### Description



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



#### Outputs


### Factorydefaults command

> Factorydefaults example commands:


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



#### Outputs



### Fwintegritycheck command

> Fwintegritycheck example commands:


#### Syntax

fwintegritycheck *[Optional Parameters]*

#### Description



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



#### Outputs



### Reboot command

> Reboot example commands:

> If the server is currently off, the reboot On command can be used to turn the server on. The reboot command logs the user out of the server.

```
ilorest > reboot On -u username -p password --url=xx.xx.xx.xx
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext

Session will now be terminated.
Please wait for the server to boot completely to login again.
Turning on the server in 3 seconds...
The operation completed successfully.
Logging session out.
```

> If the server has been turned on, the reboot ForceOff command can be used to turn the server off immediately. Note that the reboot command logs the user out of the server.

```
ilorest > reboot ForceOff -u username -p password --url=xx.xx.xx.xx
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext

Session will now be terminated.
Please wait for the server to boot completely to login again.
Turning on the server in 3 seconds...
The operation completed successfully.
Logging session out.
```

> If the server is currently on, the reboot ForceRestart command can be used to turn the server off immediately and then start again. Note that the reboot command logs the user out of the server. 

```
ilorest > reboot ForceRestart -u username -p password --url=xx.xx.xx.xx
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext

After the server is rebooted the session will be terminated.
Please wait for the server to boot completely to login again.
Rebooting server in 3 seconds...
The operation completed successfully.
Logging session out.
```

> If the server is currently on, the reboot Nmi command can be used to generate a non-maskable interrupt to cause an immediate system halt. Note that the reboot command logs the user out of the server.

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

> The reboot PushPowerButton command can be used to simulate physically pressing the power button on the server. If the server is off, this command will turn the server on. If the server is on, this command will turn the server off. Note that the reboot command logs the user out of the server.

```
ilorest > reboot PushPowerButton -u username -p password --url=xx.xx.xx.xx
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext

Server is powering off the session will be terminated.
Please wait for the server to boot completely its operation to login again.
Powering off the server in 3 seconds...
The operation completed successfully.
Logging session out.
```


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

#### Inputs

None

#### Outputs

None

### Sendtest command

> Sendtest example commands:


#### Syntax

sendtest *[Command] [Optional Parameters]*

#### Description



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



#### Outputs


### serverlogs command

> serverlogs example commands:


#### Syntax

serverlogs *[Log_Selection] [Optional Parameters]*

#### Description



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

Optionally set a filter value for a filter attribute. This uses the provided filter for the currently selected type. Note: Use this flag to narrow down your results. For example, selecting a common type might return multiple objects that are all of that type. If you want to modify the properties of only one of those objects, use the filter flag to narrow down results based on properties Usage: --filter [ATTRIBUTE]=[VALUE]

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


#### Inputs



#### Outputs




### iLOReset command

> iLOReset example commands:

> Use this command to reset iLO on the currently logged in server. This will turn iLO off and on again.

```
ilorest > iloreset -u username -p password --url=xx.xx.xx.xx
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext

After ilo resets the session will be terminated.
Please wait for iLO to initialize completely before loggin-in again.
This process may take up to 3 minutes.

An iLO reset is in progress.	
Logging session out.
```

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

> The firmwareupdate command updates the firmware for iLO. After the server was logged into, the firmware update at the given location was used to update the firmware. After the update was completed, iLO was reset and the session was terminated. Note that iLO does not always reset after a firmware update.

```
ilorest > firmwareupdate https://fileurl/file.bin -u username -p password --url=xx.xx.xx.xx
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext
The operation completed successfully.
Starting upgrading process...

Updating: \

Firmware update has completed and iLO may reset.
If iLO resets the session will be terminated.
Please wait for iLO to initialize completely before logging in again.
A reboot may be required for firmware changes to take effect.
Logging session out.
```



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


#### Syntax

iloaccounts *[COMMAND] [OPTIONS]*

#### Description
- LOGINNAME:  The account name, not used to login.
- USERNAME: The account username name, used to login. 
- PASSWORD:  The account password, used to login.
- Id: The number associated with an iLO user account.

	NOTE: please make sure the order of arguments is correct. The
	parameters are extracted based on their position in the arguments list.
	Only privileges available to the logged in account can be set to the new account.



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



#### Outputs


### Iloclone command

> Iloclone  example commands:


#### Syntax

iloclone *[Optional Parameters]*

#### Description



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


#### Inputs



#### Outputs



### Ilofederation command

> Ilofederation example commands:


#### Syntax

ilofederation *[Optional Parameters]*

#### Description



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



#### Outputs



### Ilolicense command

> ilolicense  example commands:


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



#### Outputs





### Serverstate command

> Serverstate example commands:

> Here we use the serverstate command without any parameters, which tells use the current state of the server.

```
ilorest > serverstate

The server is currently in state: InPostDiscoveryComplete
```

> Here, serverstate is used along with login information to login and return the serverstate in one step.

```
ilorest > serverstate –u user –p password –url=xx.xx.xx.xx

Discovering data from iLO…Done

WARNING: Cache is activated. Session keys are stored in plaintext. 

The server is currently in state: InPostDiscoveryComplete
```


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


#### Syntax

sigrecompute *[OPTIONS]*

#### Description
Recalculate the signature on the computers configuration.


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



#### Outputs


### Singlesignon command

> Singlesignon  example commands:


#### Syntax

Singlesignon *[OPTIONS]*

#### Description


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



#### Outputs



### Virtualmedia command

> Virtualmedia  example commands:


#### Syntax

virtualmedia *[ID] [URI] [OPTIONS]*

#### Description


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

Use this flag if you wish to boot from the image on next server reboot. NOTE: The image will be ejected automatically on the second server reboot so that the server does not boot to this image twice.

#### Inputs



#### Outputs


