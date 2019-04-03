## BIOS commands

This section details usage and examples of RESTful Interface Tool commands related to configuring BIOS settings. These commands do things such as view and change the boot order, reset the BIOS configuration to the default settings, and configure iSCSI settings.

### Bootorder command

> Bootorder example commands:

> Run without arguments to view the current persistent boot order, continuous and one time boot options, and continuous and one time boot UEFI options.

<pre>
iLOrest > <font color="#01a982">bootorder</font>
Discovering data...Done

Current Persistent Boot Order:
1. HD.EmbRAID.1.6 (sles-secureboot)
2. HD.EmbRAID.1.7 (Windows Boot Manager)
3. HD.EmbRAID.1.8 (Red Hat Enterprise Linux)
4. NIC.LOM.1.1.IPv4 (Embedded LOM 1 Port 1 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC (PXE IPv4))
5. NIC.LOM.1.1.Httpv4 (Embedded LOM 1 Port 1 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC (HTTP(S) IPv4))
6. HD.SD.1.2 (Internal SD Card 1 : Generic USB3.0-CRW)
7. HD.EmbRAID.1.2 (Embedded RAID 1 : HPE Smart Array P408i-a SR Gen10 - Size:279.3 GiB Port:1I Bay:1 Box:1)
8. HD.EmbRAID.1.3 (Embedded RAID 1 : HPE Smart Array P408i-a SR Gen10 - Size:279.3 GiB Port:1I Bay:2 Box:1)
9. HD.EmbRAID.1.4 (Embedded RAID 1 : HPE Smart Array P408i-a SR Gen10 - Size:279.3 GiB Port:1I Bay:3 Box:1)
10. HD.EmbRAID.1.5 (Embedded RAID 1 : HPE Smart Array P408i-a SR Gen10 - Size:279.3 GiB Port:1I Bay:4 Box:1)
11. Generic.USB.1.1 (Generic USB Boot)
12. NIC.LOM.1.1.Httpv6 (Embedded LOM 1 Port 1 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC (HTTP(S) IPv6))
13. NIC.LOM.1.1.IPv6 (Embedded LOM 1 Port 1 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC (PXE IPv6))

Continuous and one time boot options:
1. None
2. Cd
3. Hdd
4. Usb
5. SDCard
6. Utilities
7. Diags
8. BiosSetup
9. Pxe
10. UefiShell
11. UefiHttp
12. UefiTarget

Continuous and one time boot uefi options:
1. HD.EmbRAID.1.7 (Windows Boot Manager)
2. HD.EmbRAID.1.6 (sles-secureboot)
3. HD.EmbRAID.1.8 (Red Hat Enterprise Linux)
4. NIC.LOM.1.1.IPv4 (Embedded LOM 1 Port 1 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC (PXE IPv4))
5. NIC.LOM.1.1.Httpv4 (Embedded LOM 1 Port 1 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC (HTTP(S) IPv4))
6. HD.SD.1.2 (Internal SD Card 1 : Generic USB3.0-CRW)
7. HD.EmbRAID.1.2 (Embedded RAID 1 : HPE Smart Array P408i-a SR Gen10 - Size:279.3 GiB Port:1I Bay:1 Box:1)
8. HD.EmbRAID.1.3 (Embedded RAID 1 : HPE Smart Array P408i-a SR Gen10 - Size:279.3 GiB Port:1I Bay:2 Box:1)
9. HD.EmbRAID.1.4 (Embedded RAID 1 : HPE Smart Array P408i-a SR Gen10 - Size:279.3 GiB Port:1I Bay:3 Box:1)
10. HD.EmbRAID.1.5 (Embedded RAID 1 : HPE Smart Array P408i-a SR Gen10 - Size:279.3 GiB Port:1I Bay:4 Box:1)
11. Generic.USB.1.1 (Generic USB Boot)
12. NIC.LOM.1.1.Httpv6 (Embedded LOM 1 Port 1 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC (HTTP(S) IPv6))
13. NIC.LOM.1.1.IPv6 (Embedded LOM 1 Port 1 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC (PXE IPv6))
</pre>

> List numbers associated with the `Current Persistent Boot Order` list to set a new boot order. Any numbers left off of the new list will be added to the end. Using the previous examples Current Persistent Boot Order, this command will place `Generic.USB.1.1`, `HD.SD.1.2`, and `HD.EmbRAID.1.8` at the top in that order. The commit flag will commit the changes, otherwise changes are not saved.

<pre>
iLOrest > <font color="#01a982">bootorder [11,6,3] --commit</font>
Committing changes...
One or more properties were changed and will not take effect until system is reset.
iLOrest > bootorder

Current Persistent Boot Order:
1. Generic.USB.1.1 (Generic USB Boot)
2. HD.SD.1.2 (Internal SD Card 1 : Generic USB3.0-CRW)
3. HD.EmbRAID.1.8 (Red Hat Enterprise Linux)
4. HD.EmbRAID.1.6 (sles-secureboot)
5. HD.EmbRAID.1.7 (Windows Boot Manager)
6. NIC.LOM.1.1.IPv4 (Embedded LOM 1 Port 1 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC (PXE IPv4))
7. NIC.LOM.1.1.Httpv4 (Embedded LOM 1 Port 1 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC (HTTP(S) IPv4))
8. HD.EmbRAID.1.2 (Embedded RAID 1 : HPE Smart Array P408i-a SR Gen10 - Size:279.3 GiB Port:1I Bay:1 Box:1)
9. HD.EmbRAID.1.3 (Embedded RAID 1 : HPE Smart Array P408i-a SR Gen10 - Size:279.3 GiB Port:1I Bay:2 Box:1)
10. HD.EmbRAID.1.4 (Embedded RAID 1 : HPE Smart Array P408i-a SR Gen10 - Size:279.3 GiB Port:1I Bay:3 Box:1)
11. HD.EmbRAID.1.5 (Embedded RAID 1 : HPE Smart Array P408i-a SR Gen10 - Size:279.3 GiB Port:1I Bay:4 Box:1)
12. NIC.LOM.1.1.Httpv6 (Embedded LOM 1 Port 1 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC (HTTP(S) IPv6))
13. NIC.LOM.1.1.IPv6 (Embedded LOM 1 Port 1 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC (PXE IPv6))
...
</pre>

> Use partial string matching to set a boot order independent of the current boot order. All boot options not listed will be added to the end of the boot order. This command will set All v4 NICs first, followed by all hard drives, followed by Generic.USB.1.1, then committing the results.

<pre>
iLOrest > <font color="#01a982">bootorder NIC.*v4 HD* Generic.USB.1.1</font>
iLOrest > bootorder

Current Persistent Boot Order:
1. NIC.LOM.1.1.IPv4 (Embedded LOM 1 Port 1 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC (PXE IPv4))
2. NIC.LOM.1.1.Httpv4 (Embedded LOM 1 Port 1 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC (HTTP(S) IPv4))
3. HD.SD.1.2 (Internal SD Card 1 : Generic USB3.0-CRW)
4. HD.EmbRAID.1.8 (Red Hat Enterprise Linux)
5. HD.EmbRAID.1.6 (sles-secureboot)
6. HD.EmbRAID.1.7 (Windows Boot Manager)
7. HD.EmbRAID.1.2 (Embedded RAID 1 : HPE Smart Array P408i-a SR Gen10 - Size:279.3 GiB Port:1I Bay:1 Box:1)
8. HD.EmbRAID.1.3 (Embedded RAID 1 : HPE Smart Array P408i-a SR Gen10 - Size:279.3 GiB Port:1I Bay:2 Box:1)
9. HD.EmbRAID.1.4 (Embedded RAID 1 : HPE Smart Array P408i-a SR Gen10 - Size:279.3 GiB Port:1I Bay:3 Box:1)
10. HD.EmbRAID.1.5 (Embedded RAID 1 : HPE Smart Array P408i-a SR Gen10 - Size:279.3 GiB Port:1I Bay:4 Box:1)
11. Generic.USB.1.1 (Generic USB Boot)
12. NIC.LOM.1.1.Httpv6 (Embedded LOM 1 Port 1 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC (HTTP(S) IPv6))
13. NIC.LOM.1.1.IPv6 (Embedded LOM 1 Port 1 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC (PXE IPv6))
...
</pre>

> Change the one time boot order using the `--onetimeboot` option. Specify a option to boot to from the `Continuous and one time boot options` list.

<pre>
iLOrest > bootorder <font color="#01a982">--onetimeboot=Hdd</font> --commit
Committing changes...
The operation completed successfully.
</pre>


> Change the continuous boot order using the `--continuousboot` option. Specify a option to boot to from the `Continuous and one time boot options` list.

<pre>
iLOrest > bootorder <font color="#01a982">--continuousboot=Cd</font> --commit
Committing changes...
The operation completed successfully.
</pre>


> To turn off any continuous or one-time boot options that have been configured, use the `--disablebootflag` option. 

<pre>
iLOrest > bootorder <font color="#01a982">--disablebootflag</font> --commit
Committing changes...
The operation completed successfully.
</pre>



#### Syntax

bootorder *[Boot Order] [Optional Parameters]*

#### Description

Modifies the current boot order and sets continuous and one-time boot settings. Run this command without arguments to display current boot order. Run it with arguments to change the boot order. To perform a one-time boot, continuous boot, or disable continuous boot or one-time boot, use the respective options.

#### Parameters

- **Boot Order**

The boot order can be specified as a list of numbers or as a list of partial strings for matching. If omitted, displays the current boot order. See examples for usage and syntax.

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--commit**

Use this flag when you are ready to commit all the changes for the current selection. Some changes made in this way will be updated instantly, while others will be reflected the next time the server is started.

- **--biospassword=BIOSPASSWORD**

Select this flag to input a BIOS password. Include this flag if second-level BIOS authentication is needed for the command to execute.

<aside class="notice">This flag is used only on iLO 4 systems and not required on iLO 5 systems.</aside>

- **--reboot=REBOOT**

Use this flag to perform a reboot command function after completion of operations. For help with parameters and descriptions regarding the reboot flag, run `help reboot`.

- **--onetimeboot=ONETIMEBOOT**

Use this flag to configure a one-time boot option. Using this flag will prioritize the provided boot source only on the very next time the server is booted.

- **--continuousboot=CONTINUOUSBOOT**

Use this flag to enable a continuous boot option. Using this flag will cause the system to boot to the selected device every time the system boots.

- **--disablebootflag**

Use this to disable either continuous or one-time boot modes.

- **--securebootkeys=SECUREBOOT**

Use this flag to perform actions on secure boot keys. Possible values include defaultkeys: resets all keys to default, deletekeys: deletes all keys, deletepk: deletes all product keys.

#### Inputs

None

#### Outputs

None

### BiosDefaults command

> BiosDefaults example commands:

> To set the bios back to factory defaults, run the command without arguments

<aside class="notice">
Some changes are not applied until the system is reset.
</aside>

<pre>
iLOrest > <font color="#01a982">biosdefaults</font>
Resetting the currently logged in server's BIOS settings to defaults.
One or more properties were changed and will not take effect until system is reset.
</pre>

> To set the bios back to user defaults, include the `--userdefaults` flag.

<pre>
iLOrest > biosdefaults <font color="#01a982">--userdefaults</font>
Resetting the currently logged in server's BIOS settings to defaults.
One or more properties were changed and will not take effect until system is reset.
</pre>

> This command simultaneously logs in to the server at the provided URL (--url) with the provided username (-u) and password (-p), sets the bios back to default settings, then reboots *(--reboot)* the server to apply the changes. Using the reboot option automatically logs-out of the server.

<pre>
iLOrest > <font color="#01a982">biosdefaults --url xx.xx.xx.xx -u username -p password --reboot=ForceRestart</font>
Discovering data...Done
Resetting the currently logged in server's BIOS settings to defaults.
One or more properties were changed and will not take effect until system is reset.

After the server is rebooted the session will be terminated.
Please wait for the server to boot completely to login again.
Rebooting server in 3 seconds...
The operation completed successfully.
Logging session out.
</pre>



#### Syntax

biosdefaults *[Optional Parameters]*

#### Description

Sets the BIOS settings of the currently logged in server back to the default settings.

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

<aside class="notice">This flag is used only on iLO 4 systems and not required on iLO 5 systems.</aside>

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

> Using the iscsiconfig command without any options will display the current ISCSI configuration, including ISCSI initiator name and currently configured boot entries.

<pre>
iLOrest > <font color="#01a982">iscsiconfig</font>

Iscsi Initiator Name: "iqn.2015-02.com.hpe:uefi-U32-Kappa"

Available iSCSI Boot Network Interfaces:
[1] Embedded LOM 1 Port 1 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC
[2] Embedded LOM 1 Port 2 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC
[3] Embedded LOM 1 Port 3 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC
[4] Embedded LOM 1 Port 4 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC
</pre>

> Use the list flag to retrieve the current configured iscsi boot attempts. If none are configured, then all sections will have a message stating **Not Added**.

<pre>
iLOrest > iscsiconfig <font color="#01a982">--list</font>
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
</pre>

> To add an iSCSI boot attempt use the `--add` option, specifying which iSCSI Network Interface to attempt a boot from. This command will add a boot attempt from option [2] in the `Available iSCSI Boot Network Interfaces` list.

<pre>
iLOrest > iscsiconfig <font color="#01a982">--add [2]</font>
One or more properties were changed and will not take effect until system is reset.
iLOrest > iscsiconfig --list
Current iSCSI Attempts:
[
  {
    "Embedded LOM 1 Port 2 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC": {
      "Attempt 1": {
        "iSCSILUN": "0",
        "iSCSIAttemptName": "1",
        "iSCSIConnectTimeoutMS": 20000,
        "iSCSIChapUsername": "",
        "iSCSIChapSecret": "",
        "iSCSIInitiatorGateway": "0.0.0.0",
        "iSCSINicSource": "NicBoot2",
        "iSCSIConnection": "Disabled",
        "iSCSIInitiatorNetmask": "0.0.0.0",
        "iSCSITargetName": "",
        "iSCSIReverseChapUsername": "",
        "iSCSIInitiatorInfoViaDHCP": true,
        "iSCSIAttemptInstance": 1,
        "iSCSITargetTcpPort": 3260,
        "iSCSIConnectRetry": 3,
        "StructuredBootString": null,
        "iSCSIReverseChapSecret": "",
        "iSCSIInitiatorIpAddress": "0.0.0.0",
        "iSCSIAuthenticationMethod": "None",
        "iSCSITargetInfoViaDHCP": true,
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
</pre>

> Modify properties for boot attempts by outputting them to a file, editing the file, then apply the changes with the `--modify` option. You must include the `--list` option with the `-f` option to write to a file.

<pre>
iLOrest > iscsiconfig <font color="#01a982">--list -f output.txt</font>
Results written out to 'output.txt'
iLOrest > iscsiconfig <font color="#01a982">--modify output.txt</font>
One or more properties were changed and will not take effect until system is reset.
</pre>

> To delete an iSCSI attempt use the `--delete` option, specifying which attempt to delete.

<pre>
iLOrest > iscsiconfig --list
Current iSCSI Attempts:
[
  {
    "Embedded LOM 1 Port 2 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC": {
      "Attempt 1": {
        "iSCSILUN": "0",
        "iSCSIAttemptName": "1",
        "iSCSIConnectTimeoutMS": 20000,
        "iSCSIChapUsername": "blah",
        "iSCSIChapSecret": "",
        "iSCSIInitiatorGateway": "0.0.0.0",
        "iSCSINicSource": "NicBoot2",
        "iSCSIConnection": "Disabled",
        "iSCSIInitiatorNetmask": "0.0.0.0",
        "iSCSITargetName": "",
        "iSCSIReverseChapUsername": "",
        "iSCSIInitiatorInfoViaDHCP": true,
        "iSCSIAttemptInstance": 1,
        "iSCSITargetTcpPort": 3260,
        "iSCSIConnectRetry": 3,
        "StructuredBootString": null,
        "iSCSIReverseChapSecret": "",
        "iSCSIInitiatorIpAddress": "0.0.0.0",
        "iSCSIAuthenticationMethod": "None",
        "iSCSITargetInfoViaDHCP": true,
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

iLOrest > iscsiconfig <font color="#01a982">--delete 1</font>
One or more properties were changed and will not take effect until system is reset.
iLOrest > iscsiconfig --list
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
</pre>



#### Syntax

iscsiconfig *[iSCSI Configuration] [Optional Parameters]*

#### Description

Use this command to view the current iSCSI configuration, save the current iSCSI configuration to a file, load an iSCSI configuration from a file, or view available NIC resources for iSCSI configuration.

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

<aside class="notice">This flag is used only on iLO 4 systems and not required on iLO 5 systems.</aside>

- **--reboot=REBOOT**

Use this flag to perform a reboot command function after completion of operations. For help with parameters and descriptions regarding the reboot flag, run `help reboot`.

#### Inputs

None

#### Outputs

None

### Results command

> Results example commands:

> Run the command without any parameters to gather the results of any changes which occurred on the last reboot.

<pre>
iLOrest > <font color="#01a982">results</font>
Results of the previous reboot changes:

Bios:
The operation completed successfully.
SmartArray:
Request successfully completed
Boot:
The operation completed successfully.
Iscsi:
The operation completed successfully.
</pre>

#### Syntax

results *[optional parameters]*

#### Description

Show the results of any changes, which require a system reboot to take effect.

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

### Pending command

> Pending example commands:

> Run `pending` with no arguments show current changes that *have* been committed to the server and are awaiting a reboot. In this example, no changes have been found.

<pre>
iLOrest > <font color="#01a982">pending</font>
Current Pending Changes:

SmartStorageConfig.v2_0_1:
No pending changes found.

HpeServerBootSettings.v2_0_0:
No pending changes found.

HpeScalablePmem.v1_0_0:
No pending changes found.

HpeiSCSISoftwareInitiator.v2_0_0:
No pending changes found.

HpeKmsConfig.v1_0_0:
No pending changes found.

HpeServerConfigLock.v1_0_0:
No pending changes found.

Bios.v1_0_0:
No pending changes found.

HpeTlsConfig.v1_0_0:
No pending changes found.
</pre>

> After committing a change to AdminName the pending command shows the change to AdminName that will take effect on reboot.

<pre>
iLOrest > select bios.
iLOrest > set AdminName=newname --commit
Committing changes...
One or more properties were changed and will not take effect until system is reset.
iLOrest > <font color="#01a982">pending</font>
Current Pending Changes:

SmartStorageConfig.v2_0_1:
No pending changes found.

HpeServerBootSettings.v2_0_0:
No pending changes found.

HpeScalablePmem.v1_0_0:
No pending changes found.

HpeiSCSISoftwareInitiator.v2_0_0:
No pending changes found.

HpeKmsConfig.v1_0_0:
No pending changes found.

HpeServerConfigLock.v1_0_0:
No pending changes found.

Bios.v1_0_0:
Attributes=
            AdminName=
                       Current=""
                       Pending=newname

HpeTlsConfig.v1_0_0:
No pending changes found.
</pre>

#### Syntax

pending *[Optional Parameters]*

#### Description

Displays pending committed changes that will be applied after a reboot.

#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **-p PASSWORD, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

#### Inputs

None

#### Outputs

None

### Setpassword command

<aside class="notice">
Please make sure the order of passwords is maintained. The passwords are extracted based on their position in the arguments list.
</aside>

> Setpassword example commands:

> To set a new password, include the new password and the current password. When setting a bios or power on password with no previous password set, `OLD_PASSWORD` must be set to `""` signifying no password.

<pre>
iLOrest > <font color="#01a982">setpassword newpassword ""</font>
The operation completed successfully.
</pre>


> When setting a bios or power on password back to nothing, `NEW_PASSWORD` must be set to `""`.

<pre>
iLOrest > <font color="#01a982">setpassword "" oldpassword</font>
The operation completed successfully.
</pre>


> To set the power on password, include the `--poweron` option.

<pre>
iLOrest > setpassword newpassword "" <font color="#01a982">--poweron</font>
The operation completed successfully.
</pre>

	


#### Syntax

setpassword *[NEW_PASSWORD] [OLD_PASSWORD] [OPTIONS]*

#### Description

Sets the bios admin password and poweron password.

#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--reboot=REBOOT**

Use this flag to perform a reboot command function after completion of operations. 'REBOOT' is replaceable parameter that can have multiple values. For help with parameters and descriptions regarding the reboot flag, run help reboot.

#### Inputs

None


#### Outputs

None

