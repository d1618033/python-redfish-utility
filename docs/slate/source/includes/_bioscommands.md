## BIOS commands

This section details usage and examples of RESTful Interface Tool commands related to configuring BIOS settings. These commands do things such as view and change the boot order, reset the BIOS configuration to the default settings, and configure iSCSI settings.

### Bootorder command

> Bootorder example commands:

> In this example, the boot order was not specified first. The current persistent boot order is listed. Other options, such as continuous and one time boot options, as well as continuous and one time boot UEFI options are also displayed. Next, we call bootorder with a specified list. This sets the boot order to **Generic.USB.1.1, HD.EmbRAID.1.3., NIC.LOM.1.1.Httpv4, HD.SD.1.2, NIC.LOM.1.1.IPV4, NIC.LOM.1.1.Httpv6, NIC.LOM.1.1.IPv6, HD.EmbRAID.1.5, HD.EmbRAID1.6, HD.EmbRAID.1.4, HD.EmbRAID1.2**. The commit flag will commit the changes, otherwise changes are not saved.

> ![Bootorder Example 1](images/examples/bootorder_ex1.png "Bootorder example 1")


> Here the one time boot order was changed so that the next time the server boots it will boot from the hard drive.

> ![Bootorder Example 2](images/examples/bootorder_ex2.png "Bootorder example 2")


> Here the continuous boot option was changed so that it will keep attempting to boot from the cd drive.

> ![Bootorder Example 3](images/examples/bootorder_ex3.png "Bootorder example 3")


> To turn off any continuous or one-time boot options that have been configured, include the disablebootflag option. 

> ![Bootorder Example 4](images/examples/bootorder_ex4.png "Bootorder example 4")



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

Use this flag to perform actions on secure boot keys.Possible values include defaultkeys: resets all keys to default,deletekeys: deletes all keys, deletepk: deletes all product keys.

#### Inputs

None

#### Outputs

None

### BiosDefaults command

> BiosDefaults example commands:

> Here after the server was logged into, the biosdefaults command resets the BIOS settings to their default values. 

<aside class="notice">
Some changes are not applied until the system is reset.
</aside>

> ![BiosDefaults Example 1](images/examples/biosdefaults_ex1.png "BiosDefaults example 1")


> Here after the server was logged into, the biosdefaults command reset the BIOS settings to their default values. The reboot flag was included so that some changes requiring a reboot will be reflected.

> ![BiosDefaults Example 2](images/examples/biosdefaults_ex2.png "BiosDefaults example 2")


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

> Using the iscsiconfig command without any flags will display the current ISCSI configuration, including ISCSI initiator name and currently configured boot entries.

> ![iSCSIConfig Example 1](images/examples/iscsi_ex1.png "iSCSIConfig example 1")

> Use the list flag to retrieve the current configured iscsi boot attempts. If none are configured, as seen above, then you will see all sections with a message stating **Not Added**.

> ![iSCSIConfig Example 2](images/examples/iscsi_ex2.png "iSCSIConfig example 2")

> The add [2] flag was included here to add a boot attempt. The [2] entry here causes the server to add a boot attempt with the **iSCSINicSource NicBoot** value of 2. Thus, the [2] supplied here caused a new entry to be added with **iSCSINicSource** value **NicBoot2**. 

<aside class="notice">
The 2 inputted here is not the attempt number, as opposed to "iscsiconfig --delete 2" which does *delete the 2nd boot attempt.*
</aside>

> ![iSCSIConfig Example 3](images/examples/iscsi_ex3.png "iSCSIConfig example 3")


> Here we first added a boot attempt, then decided to modify some properties. We do this by first writing the **iscsiconfig** properties to a file called **output.txt** using the –f flag. 

<aside class="notice">
The results are only written to the file if the --list flag is included as well.
</aside>

> ![iSCSIConfig Example 4-1](images/examples/iscsi_ex4-1.png "iSCSIConfig example 4-1")

> ![iSCSIConfig Example 4-2](images/examples/iscsi_ex4-2.png "iSCSIConfig example 4-2")

> ![iSCSIConfig Example 5-1](images/examples/iscsi_ex5-1.png "iSCSIConfig example 5-1")


> Then we opened up the output.txt file in a word processor, changed the property we wanted to, and re-uploaded the configuration to the server using the modify flag. Since second-level BIOS authentication was required, the biospassword flag was included as well. The original and modified output.txt files are given above, with the iSCSITargetInfoViaDHCP value changed from true to false. The original and modified output.txt files are given above, with the iSCSITargetInfoViaDHCP value changed from true to false.

> Here when the server was logged into, there was already a boot attempt configured. To delete a boot attempt, use the delete flag to remove the boot attempt. We then verified that the boot attempt was deleted with another list flag. 

<aside class="notice">
The "iscsiconfig --delete 1" command deletes the 1st iSCSI attempt. This is different from the number specified with "iscsiconfig --add [1]", which implies add an iSCSI attempt with **NicBoot1**.
</aside>


> ![iSCSIConfig Example 5-2](images/examples/iscsi_ex5-2.png "iSCSIConfig example 5-2")

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

<aside class="notice">This flag is used only on iLO 4 systems and not required on iLO 5 systems.</aside>

- **--reboot=REBOOT**

Use this flag to perform a reboot command function after completion of operations. For help with parameters and descriptions regarding the reboot flag, run `help reboot`.

#### Inputs

None

#### Outputs

None

### Results command

> Results example commands:

> Using the results command without any parameters here shows any BIOS changes after a reboot. Here, Bios, Iscsi, and Boot all show as having been completed successfully.

> ![Results Example 1](images/examples/results_ex1.png "Results example 1")

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

### Pending command

> Pending example commands:

> Here when first running the pending command on a server with no changes we see there are no changes found.

> ![Pending Example 1](images/examples/pending_ex1.png "Pending example 1")

> Now we set and commit AdminName to the new value "newadminname". After we log back into the server we see pending command shows our change to AdminName that will take effect on reboot.

> ![Pending Example 2](images/examples/pending_ex2.png "Pending example 2")

#### Syntax

pending *[Optional Parameters]*

#### Description

Displays pending committed changes that will be applied after a reboot.

#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **--url=URL**

Use the provided iLO URL to login.

- **-u USER, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p PASSWORD, --password=PASSWORD**

Use the provided iLO password to log in.


#### Inputs

None

#### Outputs

None

### Setpassword command

<aside class="notice">
Please make sure the order of passwords is maintained. The passwords are extracted base on their position in the arguments list.
</aside>

> Setpassword example commands:

> Setting the admin password with no previous password set.

> ![Setpassword Example 1](images/examples/setpassword_ex1.png "Setpassword example 1")


> Setting the admin password back to nothing. 

> ![Setpassword Example 2](images/examples/setpassword_ex2.png "Setpassword example 2")


> Setting the power on password.

> ![Setpassword Example 3](images/examples/setpassword_ex3.png "Setpassword example 3")

	


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

None


#### Outputs

None

