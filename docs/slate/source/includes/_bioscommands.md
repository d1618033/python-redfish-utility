## BIOS commands

This section details usage and examples of RESTful Interface Tool commands related to configuring BIOS settings. These commands do things such as view and change the boot order, reset the BIOS configuration to the default settings, and configure iSCSI settings.

### Bootorder command

> Bootorder example commands:

> In this example, the boot order was not specified first. The current persistent boot order is listed. Other options, such as continuous and one time boot options, as well as continuous and one time boot UEFI options are also displayed. Next, we call bootorder with a specified list. This sets the boot order to **Generic.USB.1.1, HD.Emb.8.2., NIC.LOM.1.1.IPV6, NIC.LOM.1.1.IPV4,HD.Emb.8.1**. The commit flag will commit the changes, otherwise changes are not saved.

```
ilorest > login xx.xx.xx.xx -u username -p password 
Discovering data from iLO...Done 
WARNING: Cache is activated session keys are stored in plaintext 
ilorest > bootorder 

Current Persistent Boot Order: 
1. HD.Emb.8.2 
2. Generic.USB.1.1 
3. NIC.LOM.1.1.IPv4 
4. NIC.LOM.1.1.IPv6 
5. HD.Emb.8.1

Continuous and one time boot options: 
1. None 
2. Cd 
3. Hdd 
4. Usb 
5. Utilities 
6. Diags 
7. BiosSetup 
8. Pxe 
9. UefiShell 

Continuous and one time boot uefi options: 
1. HD.Emb.8.2 
2. Generic.USB.1.1 
3. NIC.LOM.1.1.IPv4 
4. NIC.LOM.1.1.IPv6 
5. HD.Emb.8.1

ilorest > bootorder [2,1,4] --commit
```

> Here the one time boot order was changed so that the next time the server boots it will boot from the hard drive.

```
ilorest > login xx.xx.xx.xx –u username –p password
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext
ilorest > bootorder --onetimeboot=Hdd --biospassword=BIOSPASSWORD --commit
Committing changes...
The operation completed successfully.
Logging session out.
```

> Here the continuous boot option was changed so that it will keep attempting to boot from the cd drive.

```
ilorest > login xx.xx.xx.xx –u username –p password
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext
ilorest > bootorder --continuousboot=Cd --biospassword=BIOSPASSWORD --commit
Committing changes...
The operation completed successfully.
Logging session out.
```

> To turn off any continuous or one-time boot options that have been configured, include the disablebootflag option. 

```
ilorest > login xx.xx.xx.xx –u username –p password
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext
ilorest > bootorder --disablebootflag --commit
Committing changes...
The operation completed successfully.
Logging session out.
```


#### Syntax

bootorder *[Boot Order] [Optional Parameters]*

#### Description

Run this command without arguments to display current boot order. Otherwise, run it with commands to change the order of booting, to perform a one-time boot, to perform a continuous bout, or disable continuous boot or one-time boot options.

#### Parameters

- **Boot Order**

The boot order can be specified as a list of numbers. If omitted, displays the current boot order. See examples below for usage and syntax.

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--commit**

Use this flag when you are ready to commit all the changes for the current selection. Including the **--commit** flag will log you out of the server after the command is run. Some changes made in this way will be updated instantly, while others will be reflected the next time the server is started.

- **--biospassword=BIOSPASSWORD**

Select this flag to input a BIOS password. Include this flag if second-level BIOS authentication is needed for the command to execute.

- **--reboot=REBOOT**

Use this flag to perform a reboot command function after completion of operations. For help with parameters and descriptions regarding the reboot flag, run `help reboot`.

- **--onetimeboot=ONETIMEBOOT**

Use this flag to configure a one-time boot option. Using this flag will prioritize the provided boot source only on the very next time the server is booted.

- **--continuousboot=CONTINUOUSBOOT**

Use this flag to enable a continuous boot option. Using this flag will cause the system to boot to the selected device every time the system boots.

- **--disablebootflag**

Use this to disable either continuous or one-time boot modes.

- **--securebootkeys=SECUREBOOT**

Use this flag to perform actions on secure boot keys.Possible values include defaultkeys: resets all keys to default,deletekeys: deletes all keys, deletepk: deletes all product keys.

#### Inputs

None

#### Outputs

None

### BiosDefaults command

> BiosDefaults example commands:

> Here after the server was logged into, the biosdefaults command resets the BIOS settings to their default values. Note that some changes will not be applied until the system is reset.

```
ilorest > biosdefaults -u username -p password --url=xx.xx.xx.xx --biospassword=BIOSPASSWORD
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext
Resetting the current logged in servers BIOS settings to defaults.
One or more properties were changed and will not take effect until system is reset.
```

> Here after the server was logged into, the biosdefaults command reset the BIOS settings to their default values. The reboot flag was included so that some changes requiring a reboot will be reflected.

```
ilorest > biosdefaults -u username -p password --url=xx.xx.xx.xx --biospassword=BIOSPASSWORD --reboot=ForceRestart
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext
Resetting the current logged in servers BIOS settings to defaults.
One or more properties were changed and will not take effect until system is reset.

After the server is rebooted the session will be terminated.
Please wait for the server to boot completely to login again.
Rebooting server in 3 seconds...
The operation completed successfully.
Logging session out.
```


#### Syntax

biosdefaults *[Optional Parameters]*

#### Description

Run this command to set the BIOS settings of the currently logged in server back to the default settings.

#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--biospassword=BIOSPASSWORD**

Select this flag to input a BIOS password. Include this flag if second-level BIOS authentication is needed for the command to execute.

- **--reboot=REBOOT**

Use this flag to perform a reboot command function after completion of operations. For help with parameters and descriptions regarding the reboot flag, run `help reboot`.

- **--userdefaults**

Sets bios to user defaults instead of factory defaults.

- **--manufacturingdefaults**

Sets bios to manufacturer defaults instead of factory defaults.

#### Inputs

None

#### Outputs

None

### iSCSIConfig command

> iSCSIConfig example commands:

> Using the iscsiconfig command without any flags will display the current ISCSI configuration, including ISCSI initiator name and currently configured boot entries.

```
ilorest > login xx.xx.xx.xx –u username –p password
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext
ilorest > iscsiconfig

Iscsi Initiator Name: "iqn.1986-03.com.hp:uefi-P89 "

Available iSCSI Boot Network Interfaces:
[1] Embedded LOM 1 Port 1 : Port 1 - HP Ethernet 1Gb 4-port 331i Adapter
[2] Embedded LOM 1 Port 2 : Port 2 - HP Ethernet 1Gb 4-port 331i Adapter
[3] Embedded LOM 1 Port 3 : Port 3 - HP Ethernet 1Gb 4-port 331i Adapter
[4] Embedded LOM 1 Port 4 : Port 4 - HP Ethernet 1Gb 4-port 331i Adapter
```

> Use the list flag to retrieve the current configured iscsi boot attempts. If none are configured, as seen above, then you will see all sections with a message stating **Not Added**.

```
ilorest > iscsiconfig --list –u username –p password --url=xx.xx.xx.xx.xx
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext
Current iSCSI Attempts:
[
  {
    "Not Added": {}
  },
  {
    "Not Added": {}
  },
  {
    "Not Added": {}
  },
  {
    "Not Added": {}
  }
]
```

> The add [2] flag was included here to add a boot attempt. The [2] entry here causes the server to add a boot attempt with the **iSCSINicSource NicBoot** value of 2. Thus, the [2] supplied here caused a new entry to be added with **iSCSINicSource** value **NicBoot2**. Note that the 2 inputted here is not the attempt number, as opposed to "iscsiconfig --delete 2" which does *delete the 2nd boot attempt.*

```
ilorest > iscsiconfig --add [2] –u username –p password --url=xx.xx.xx.xx --biospassword=BIOSPASSWORD
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext
One or more properties were changed and will not take effect until system is reset.
ilorest > iscsiconfig --list
Current iSCSI Attempts:
[
  {
    "Embedded LOM 1 Port 1 : Port 1 - Broadcom NetXtreme Gigabit Ethernet (BCM57
19)": {
      "Attempt 1": {
        "iSCSIConnectTimeoutMS": 0,
        "iSCSIChapUsername": null,
        "iSCSIChapSecret": null,
        "iSCSIInitiatorGateway": "0.0.0.0",
        "iSCSINicSource": "NicBoot2",
        "iSCSITargetInfoViaDHCP": true,
        "iSCSIBootAttemptName": "1",
        "iSCSIChapType": "OneWay",
        "iSCSITargetIpAddress": "0.0.0.0",
        "iSCSIIpAddressType": "IPv4",
        "UEFIDevicePath": null
      }
    }
  },
  {
    "Not Added": {}
  },
  {
    "Not Added": {}
  },
  {
    "Not Added": {}
  }
]
```

> Here we first added a boot attempt, then decided to modify some properties. We do this by first writing the **iscsiconfig** properties to a file called **output.txt** using the –f flag. Note that the results will only be written to the file is the --list flag is included as well.

```
ilorest > iscsiconfig --add [1] –u username –p password --url=xx.xx.xx.xx --biospassword=BIOSPASSWORD
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext
One or more properties were changed and will not take effect until system is reset.
ilorest > iscsiconfig --list –f output.txt
Results written out to 'output.txt'
ilorest > iscsiconfig --modify output.txt --biospassword=BIOSPASSWORD
One or more properties were changed and will not take effect until system is reset.

Original file:
[
  {
    "Embedded LOM 1 Port 1 : Port 1 - Broadcom NetXtreme Gigabit Ethernet (BCM5719)": {
      "Attempt 1": {
        "iSCSIConnectTimeoutMS": 0,
        "iSCSIChapUsername": null,
        "iSCSIChapSecret": null,
        "iSCSIInitiatorGateway": "0.0.0.0",
        "iSCSINicSource": "NicBoot1",
        "iSCSITargetInfoViaDHCP": true,
        "iSCSIBootAttemptName": "1",
        "iSCSIChapType": "OneWay",
        "iSCSITargetIpAddress": "0.0.0.0",
        "iSCSIIpAddressType": "IPv4",
        "UEFIDevicePath": null
      }

    }
  }, 
  {
    "Not Added": {}
  }, 
  {
    "Not Added": {}
  }, 
  {
    "Not Added": {}
  }
]

Modified File
[
  {
    "Embedded LOM 1 Port 1 : Port 1 - Broadcom NetXtreme Gigabit Ethernet (BCM5719)": {
      "Attempt 1": {
        "iSCSIConnectTimeoutMS": 0,
        "iSCSIChapUsername": null,
        "iSCSIChapSecret": null,
        "iSCSIInitiatorGateway": "0.0.0.0",
        "iSCSINicSource": "NicBoot1",
        "iSCSITargetInfoViaDHCP": false,
        "iSCSIBootAttemptName": "1",
        "iSCSIChapType": "OneWay",
        "iSCSITargetIpAddress": "0.0.0.0",
        "iSCSIIpAddressType": "IPv4",
        "UEFIDevicePath": null
      }

    }
  }, 
  {
    "Not Added": {}
  }, 
  {
    "Not Added": {}
  }, 
  {
    "Not Added": {}
  }
]
```

> Then we opened up the output.txt file in a word processor, changed the property we wanted to, and re-uploaded the configuration to the server using the modify flag. Since second-level BIOS authentication was required, the biospassword flag was included as well. The original and modified output.txt files are given above, with the iSCSITargetInfoViaDHCP value changed from true to false. The original and modified output.txt files are given above, with the iSCSITargetInfoViaDHCP value changed from true to false.

> Here when the server was logged into, there was already a boot attempt configured. To delete a boot attempt, use the delete flag to remove the boot attempt. We then verified that the boot attempt was deleted with another list flag. Note that here, "iscsiconfig --delete 1" deletes the 1st iSCSI attempt. This is different from the number specified with "iscsiconfig --add [1]", which implies add an iSCSI attempt with **NicBoot1**.

```
ilorest > iscsiconfig --list -u username -p password --url=xx.xx.xx.xx
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext
Current iSCSI Attempts:
[
  {
    "Embedded LOM 1 Port 1 : Port 1 - Broadcom NetXtreme Gigabit Ethernet (BCM57
19)": {
      "Attempt 1": {
        "iSCSIConnectTimeoutMS": 0,
        "iSCSIChapUsername": null,
        "iSCSIChapSecret": null,
        "iSCSIInitiatorGateway": "0.0.0.0",
        "iSCSINicSource": "NicBoot1",
        "iSCSITargetInfoViaDHCP": false,
        "iSCSIBootAttemptName": "1",
        "iSCSIChapType": "OneWay",
        "iSCSITargetIpAddress": "0.0.0.0",
        "iSCSIIpAddressType": "IPv4",
        "UEFIDevicePath": null
      }
    }
  },
  {
    "Not Added": {}
  },
  {
    "Not Added": {}
  },
  {
    "Not Added": {}
  }
]
ilorest > iscsiconfig --delete 1 --biospassword=BIOSPASSWORD
One or more properties were changed and will not take effect until system is reset.
ilorest > iscsiconfig --list
Current iSCSI Attempts:
[
  {
    "Not Added": {}
  },
  {
    "Not Added": {}
  },
  {
    "Not Added": {}
  },
  {
    "Not Added": {}
  }
]
```

#### Syntax

iscsiconfig *[iSCSI Configuration] [Optional Parameters]*

#### Description

Use this command to view the current iSCSI configuration, to save the current iSCSI configuration to a file, to load an iSCSI configuration from a file, or to view available NIC resources for iSCSI configuration.

#### Parameters

- **--add=ADD**

Use this iSCSI configuration option to add an iSCSI configuration option.

- **--delete=DELETE**

Use this iSCSI configuration option to delete an iSCSI configuration option.

- **--modifiy=MODIFY**

Use this iSCSI configuration option to modify an iSCSI configuration option.

- **--list**

Use this iSCSI configuration option to list the details of the different iSCSI configurations.

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-f FILENAME, --filename=FILENAME**

Optionally include this flag to use the provided filename instead of the default `ilorest.json` file.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--biospassword=BIOSPASSWORD**

Select this flag to input a BIOS password. Include this flag if second-level BIOS authentication is needed for the command to execute.

- **--reboot=REBOOT**

Use this flag to perform a reboot command function after completion of operations. For help with parameters and descriptions regarding the reboot flag, run `help reboot`.

#### Inputs

None

#### Outputs

None

### Results command

> Results example commands:

> Using the results command without any parameters here shows any BIOS changes after a reboot. Here, Bios, Iscsi, and Boot all show as having been completed successfully.

```
ilorest > results

Results of the previous BIOS change:

Bios:

The operation completed successfully.

Iscsi:

The operation completed successfully.

Boot:

The operation completed successfully.
```


#### Syntax

results *[optional parameters]*

#### Description

Show the results of a BIOS change after a server reboot.

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

### Setpassword command

> Setpassword example commands:



#### Syntax

setpassword *[NEW_PASSWORD] [OLD_PASSWORD] [OPTIONS]*

#### Description



#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **-p PASSWORD, --password=PASSWORD**

Use the provided iLO password to log in.

- **--reboot=REBOOT**

Use this flag to perform a reboot command function after completion of operations. 'REBOOT' is replaceable parameter that can have multiple values. For help with parameters and descriptions regarding the reboot flag, run help reboot.




#### Inputs



#### Outputs


