# Use case Examples and Macro Commands

The command catalog provided by the RESTful Interface Tool enables a wide variety of options to manipulate and work with the server. Multiple commands chained together have the potential to provide higher-level functionality and meet any needs that arise depending on the task at hand. Some of the more common commands, such as the `bootorder` command, have already been built into the command catalog. The `bootorder` example below shows how the available commands in the command catalog can be combined to manipulate the order of boot devices.

## Changing Bootorder example

The `bootorder` command is made up of a list of select, get, and set commands. In order to demonstrate the order of these events, the `bootorder` command is manually stepped through one step at a time to show that it only uses other provided commands to perform its task.

![Bootorder Example 1](images/BootOrder_1.png "BootOrder example 1")

First the server is logged into, and the `select` and `get` commands are performed on the `Bios` type and the `BootMode` property, respectively.

![Bootorder Example 2](images/BootOrder_2.png "BootOrder example 2")

Next the `select` and `get` commands are used to retrieve the `BootSourceOverrideSupported` property of the `ComputerSystem` type.

<aside class="notice">All of these operations, such as <b>select</b> and <b>get</b>, are already implemented in the RESTful Interface Tool.</aside>

![Bootorder Example 3](images/BootOrder_3.png "BootOrder example 3")

If the `bootmode` retrieved earlier is UEFI, then the `UefiTargetBootSourceOverrideSupported` property (one time boot settings) is retrieved with the get command. If the `bootmode` is not UEFI, then the one time boot settings would have been set to `None`.

![Bootorder Example 4](images/BootOrder_4.png "BootOrder example 4")

If this is not a one time boot or a continuous boot, and the `disable boot` flag has not been set, then the `HpServerBootSettings` type is selected with the `select` command, and the `PersistentBootConfigOrder` property is retrieved with the `get` command.

![Bootorder Example 5](images/BootOrder_5.png "BootOrder example 5")

Then, using this information along with the specified boot order provided in the command, the new boot order is updated using the `set` command.

![Bootorder Example 6](images/BootOrder_6.png "BootOrder example 6")

After making all the changes to the boot order, the changes are finally committed with the commit command.

All of the commands shown here are executed the same way in the actual `bootorder` command, and are called in the same order to execute the `bootorder` command. You can write your own scripts to combine commands just like bootorder did, to use the provided commands in the RESTful Interface Tool for higher level functionality.

## Changing BIOS Administrator Password example

This example shows how the set password command on a Gen9 system is just a few set commands.

The `Bios` type has two properties that both need to be used to change the administrator password, `AdminPassword` and `OldAdminPassword`. `AdminPassword` is the new password you want to change to, and `OldAdminPassword` is the current password you have.

<aside class="notice">If there is no current password, you must include <b>OldAdminPassword=””</b>.</aside>

![BIOS Password Example 1](images/BIOSPassword_1.png "BIOS Password Example 1")

If you perform a `get` command to find the current `AdminPassword` and `OldAdminPassword` values, you will notice that their values are listed as `None`, regardless of what their actual values are, as seen above.

![BIOS Password Example 2](images/BIOSPassword_2.png "BIOS Password Example 2")

In order to change the administrator password, you need to set the `AdminPassword` (the new value you want) and the `OldAdminPassword` (what the admin password was before), as well as include the `–biospassword` flag if the system is iLO 4.

<aside class="notice">The <b>biospassword</b> value is the same as the <b>OldAdminPassword</b> value.</aside>

![BIOS Password Example 3](images/BIOSPassword_3.png "BIOS Password Example 3")

After you’ve set the values for `AdminPassword` and `OldAdminPassword`, you need to commit your changes and reboot your server:

<aside class="notice">To change the administrator password, <b>AdminPassword</b> and <b>OldAdminPassword</b> MUST be set in the same line.</aside>

![BIOS Password Example 4](images/BIOSPassword_4.png "BIOS Password Example 4")

Then when you log into the server again, the BIOS password will have been updated to the new value. However, you cannot see the values for `AdminPassword` or `OldAdminPassword`.

## Disabling the Trusted Platform Module (TPM) on servers example

![TPM Example](images/TPM_disable.png "TPM Example")

> **Above:** When the server is rebooted, the **TpmState** is changed from **PresentEnabled** to **PresentDisabled**.

If you need to disable TPM on a group of servers, you can use a set of commands in RESTful Interface Tool. For example, if you are installing SPPs and OSs on bare-metal servers, and you need to disable TPM prior to starting installation.


### Enable the TPM on servers

![TPM Example](images/TPM_enable.png "TPM Example")


To enable the TPM, you can set the `TpmState` to `PresentEnabled`. **See side example**.

<aside class="notice">When you are disabling or enabling TPM, depending on the TPM chip type on the server, the TPM visibility might be <b>Tpm2Visibility</b> or <b>TpmVisibility</b>.</aside>


## Finding iLO MAC address

Finding the iLO MAC address is not implemented in the RESTful Interface Tool, but is easily reached by a set of `select` and `list` commands

![MAC Address Example 1](images/MacAddress1.png "Mac Address example 1")

First login to the server. Then `select` the `EthernetInterfaces.` type.

![MAC Address Example 2](images/MacAddress2.png "Mac Address example 2")

Now using the `list` command, list the `name`, `macaddress`, and `status` values with the filter of the value `Name` starting with Manager.


## Setting Active iLO NIC

> Use this for gen10 servers.

```json
{
	"path": "/redfish/v1/Managers/1/EthernetInterfaces/1",
	"body": {
		"Oem": { 
			"Hpe": { 
				"NICEnabled": true
			}
		}
   	 }
}
```

> Use this for gen9 servers.

```json
{
	"path": "/redfish/v1/Managers/1/EthernetInterfaces/1",
	"body": {
		"Oem": { 
			"Hp": { 
				"NICEnabled": true
			}
		}
   	 }
}
```
To set the iLO NIC, First login to the server. Then use a `rawpatch` command 

![NIC Example 1](images/NIC.png "Mac Address example 1")


To set the NIC, first login to the server. Then we will be using a `rawpatch` command

## Setting iLO Timezone

In setting the iLO Timezone, we will be using both a rawpost and commands.

![Timezone Example 1](images/timezone1.png "Time Zone example 1")

First we login and select the HpeiLODateTime. type. If using Gen9, select the HpiLODateTime type instead. We then `list` the `TimeZoneList`. 

Now scroll around looking for the timezone that is wanted. In the case of the example, we will be using US/Hawaii. Take note of the index associated with the Name.(2 in the case of US/Hawaii)

![Timezone Example 2](images/timezone2.png "Time Zone example 2")

Finally, we `set` the Index to 2. Check the status to make sure the change is queued and finally make sure to `commit` to finalize the changes.

## Getting Powermetric Average

First login to the server.

![Power Example 1](images/power.png "Powermetric example 1")

Next `select` the Power. type. Finally `list` powercontrol. The powermetric average is represented by the `AverageConsumedWatts` value.

## Getting Encryption Settings

To get the encryption settings, first login to the server

![Encryption Setting Example 1](images/encryptionsettings.png "Encryption Setting example 1")

Then `select` the `HpeSmartStorageArrayControllerCollection` type. If on a `Gen9` server select `HpSmartStorageArrayControllerCollection` instead.

In the provided example, many of the resources for the encryption setting are not available. If available there will be values of `Name`, `Model`, `SerialNumber`, `EncryptionBootPasswordSet`, `EncryptionCryptoOfficerPasswordSet`, `EncrpytionLocalKeyCacheEnabled`, `EncryptionMixedVolumesEnabled`,`EncryptionPhyiscalDriveCount`,`EncryptionRecoveryParamsSet`,`EncryptionStandaloneModeEnabled`, and/or `EncryptionUserPasswordSet`.

## Updating the HPE iLO license key

```json
{
	"path": "/rest/v1/Managers/1/LicenseService",
    "body": {
        "LicenseKey": "license key"
    }
}
```

To update an iLO license key, use the `rawpost` command. For more information, see [RawPost command](#rawpost-command).

The following is an example of the JSON to include when using the `rawpost` command.

To delete an iLO license, use the `rawdelete` command. For more information, see [RawDelete command](#rawdelete-command). The following is an example of the JSON to include when using the `rawdelete` command:

`rawdelete /rest/v1/Managers/1/LicenseService`

## Deploying a Service Pack for ProLiant (SPP)

```json
{
    "path": "/rest/v1/Managers/1/VirtualMedia/2",
    "body": {
        "Action": "InsertVirtualMedia",
        "Target": "/OEM/Hp",
        "Image": "http://xx.xxx.xxx.xxx:xx/spp.iso
    }
}
```
	

To deploy a SPP, use the rawpost command. For more information, see [RawPost command](#rawpost-command).

`ilorest -v --nologo rawpost virtualmedia.json --url=xx.xx.xx.xxx --user=Admin --password=password`

The following is an example of the JSON to include when using the `rawpost` command.


# Script Examples

## Selecting and getting properties from a type.

```
:: selectget.bat [URI] [USERNAME] [PASSWORD] 
@echo off

set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% LSS 3 goto :failCondition
goto :main

:failCondition
@echo Usage:
@echo selectget.bat [URI] [USERNAME] [PASSWORD]
goto :EOF

:main
@echo *****************************************
@echo ************* Logging in... *************
@echo *****************************************
ilorest.exe login %1 -u %2 -p %3
@echo *****************************************
@echo ******* selecting Bios type... ********
@echo *****************************************
ilorest.exe select Bios.
@echo *****************************************
@echo ********** getting BootMode... **********
@echo *****************************************
ilorest.exe get 
pause
```

This is a batch file that logs into a remote server, selects the `Bios` type, and gets the `BootMode` value.

## Saving and Loading a File Using File-Based Editing Mode

```
:: saveload.bat [SELECTOR] [FILENAME]
:: Specify a type with the SELECTOR tag, and
:: save to a file called FILENAME
@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% LSS 2 goto :failCondition
goto :main

:failCondition
@echo Usage:
@echo saveload.bat [SELECTOR] [FILENAME]
@echo specify a type with the SELECTOR tag, and
@echo save to a file called FILENAME
goto :EOF

:main
ilorest.exe login
ilorest.exe save --selector=%1 --json -f %2
@echo Edit the file, then:
pause
ilorest.exe load -f %2
```

This is a file-based edit mode helper for RESTful Interface Tool.

1. Run to download selected type to a file called `ilorest.json.`

2. Edit the `ilorest.json` file to make changes.

3. Press any key running batch program to continue with program, uploading the newly edited program to the server.

## Change secureboot settings

```
@echo off

if "%1"=="True" goto passcondition
if "%1"=="False" goto passcondition
if "%1"=="true" goto passcondition
if "%1"=="false" goto passcondition
goto :failcondition

:passCondition
set argC=0
for %%x in (%*) do Set /A argC+=1

if %argC% == 0 goto :failcondition
if %argC% == 1 goto :local
if %argC% == 4 goto :remote
goto :failcondition

:failcondition
@echo Usage:
@echo Param 1: True or False
@echo.
@echo Remote Only Parameters:
@echo    (optional) Param 2: IP Address for ILO
@echo    (optional) Param 3: ILO Username
@echo    (optional) Param 4: ILO Password
goto :EOF

:local
@echo.
@echo *******************************************
@echo *********** Initiating script *************
@echo *******************************************
@echo.
ilorest.exe login
ilorest.exe set SecureBootEnable=%1 --selector HpSecureBoot. --commit
goto :finalcomment

:remote
@echo.
@echo *******************************************
@echo *********** Initiating script *************
@echo *******************************************
@echo.
ilorest.exe set SecureBootEnable=%1 --url %2 -u %3 -p %4 --selector HpSecureBoot. --commit

:finalcomment
@echo.
@echo ********************************************
@echo ********** Done applying changes ***********
@echo ********************************************

pause
```

This is a batch file that enables you to change the secure boot settings quickly.

**Usage:**

- Param 1: `True` or `False`

- (optional) Param 2: IP address for iLO

- (optional) Param 3: iLO username

- (optional) Param 4: iLO password
