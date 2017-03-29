## iLO Commands

This section includes advanced functions for manipulating iLO using the RESTful Interface Tool. These commands include operations such as turning the server hardware on and off, resetting iLO, and updating firmware.

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
