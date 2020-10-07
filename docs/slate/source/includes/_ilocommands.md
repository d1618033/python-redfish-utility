## iLO Commands

This section includes advanced functions for manipulating iLO using the RESTful Interface Tool. These commands include operations such as turning the server hardware on and off, resetting iLO, and updating firmware.

iLO commands that are supported for a specific HPE server generation:
<ul>
<li>certificate: Gen10 with limited functionality for Gen9
<li>fwintegritycheck: Gen10
<li>iloclone: Gen10
<li>sigrecompute: Gen9
</ul>

### Backuprestore command

> To create a backup (.bak) file run the command with the `backup` argument.

<pre>
iLOrest > <font color="#01a982">backuprestore backup</font>
Downloading backup file HPE_Kappa_20190203_0012.bak...Download complete.
</pre>

> To restore a server using the .bak file run the command with the `restore` argument. By default the command will search for a (.bak) file in the current working directory. Specify a (.bak) file using the `(-f, --filename)` option.

<pre>
iLOrest > <font color="#01a982">backuprestore restore</font>
Restore in progress. iLO while be unresponsive while the restore completes.
Your session will be terminated.
Logging session out.
</pre>

#### Syntax

backuprestore [OPTIONS]

#### Description

Backup and restore iLO to a server using a **.bak** file.

<aside class="notice">Use this command to only restore the machine from which the backup file was created. To apply one configuration in multiple systems, refer to the <a href="#serverclone-command">serverclone command</a>.</aside>

<aside class="notice">This command is available only in remote mode.</aside>

</aside>

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

- **-f FILENAME, --filename=FILENAME**

Use this command to specify the which backup file to restore. By default, the command will try to find a .bak file in the current working directory.

- **--filepass=FPASS**

Use the provided password when creating the backup file. The same password must be used for restoring.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

#### Inputs
None

#### Outputs
None

### Certificate command

<aside class="notice">
<ul>
<li>Please make sure the order of arguments is correct. The parameters are extracted based on their position in the arguments list.</li>
<li>Some certificate types are not available on Gen9.</li>
<li>Use the singlesignon command to import single sign on certificates.</li>
<li>Use quotes to include parameters, which contain whitespace when generating a CSR. For example: certificate csr "Hewlett Packard Enterprise" "iLORest Group" "CName" "United States" "Texas" "Houston"</li>
</ul>
</aside>

> Certificate example commands:

> To Generate an https certificate signing request use the `csr` argument along with the following information `Organization Name`, `Organization Unit`, `Common Name`, `Country`, `State`, `City`. Use quotes to include parameters which contain whitespace.

<pre>
iLOrest > login
Discovering data...Done
iLOrest > <font color="#01a982">certificate csr "Hewlett Packard Enterprise" "iLORest Group" CName "United States" Texas Houston </font>
iLO is creating a new certificate signing request This process can take up to 10 minutes.
X509 Certificate is being generated and the process might take up to 10 minutes.
</pre>

> To retrieve the certificate signing request use the `getcsr` argument. The default filename is `certificate.txt`, saved to the current working directory. Including the *(-f, --filename)* option will change the default name.

<pre>
iLOrest > <font color="#01a982">certificate getcsr</font>
Discovering data...Done
Certificate saved to: certificate.txt
</pre>

> To import a CA certificate use the `ca` argument followed by a file containing the certificate.

<pre>
iLOrest > <font color="#01a982">certificate ca certfile.txt</font>
The operation completed successfully.
</pre>

> To import a CRL certificate use the `crl` argument followed by a URI to the certificate file.

<pre>
iLOrest > <font color="#01a982">certificate crl http://hostname/location/to/cert.txt</font>
The operation completed successfully.
</pre>

> To import a TLS certificate use the `tls` argument followed by a file containing the certificate.

<pre>
iLOrest > <font color="#01a982">certificate tls certfile.txt</font>
The operation completed successfully.
</pre>

#### Syntax

certificate *[Optional Parameters]*

#### Description
Command for importing both iLO and login authorization certificates as well as generating iLO certificate signing requests.

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

- **-f FILENAME, --filename=FILENAME**

Use this flag if you wish to use a different filename for the certificate signing request. The default filename is certificate.txt.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

#### Inputs
None

#### Outputs
None


### Clearrestapistate command

> Clearrestapistate example commands:

> To Clear the persistent RESTful API state run the command without arguments.

<pre>
iLOrest > <font color="#01a982">clearrestapistate</font>
The operation completed successfully.
</pre>



#### Syntax

clearrestapistate *[Optional Parameters]*

#### Description
Clears the persistent RESTful API state. Generally not needed and shouldn't be done unless there are issues viewing info, setting, or committing data.

<aside class="warning">Some types such as Bios, Icsci, and SmartStorageConfig will not be available until a system reboot occurs after running this command.</aside>


#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.


#### Inputs
None


#### Outputs
None

### Directory command

<aside class="notice">
To change settings, you must first enable the directory. You can use the `--enable` option to enable a directory in the same command as settings are set.
</aside>

When creating custom local roles use the following numbers to specify privileges.

LOCAL PRIVILEGES:
1. Login
2. Remote Console
3. User Config
4. iLO (Manager) Config
5. Virtual Media
6. Virtual Power and Reset
7. Host NIC Config
8. Host Bios Config
9. Host Storage Config
10. System Recovery Config
11. Self Password Change
12. Configure Components

LOCAL ROLES:
- ReadOnly
- Operator
- Administrator

> To view current LDAP or kerberos settings run the command with the `ldap` or `kerberos` arguments.

<pre>
iLOrest > <font color="#01a982">directory ldap</font>
Discovering data...Done
LDAP settings:
--------------------------------
Enabled: False
Service Address: Not Set
Local Account Authorization: Enabled
Port: 55
Authentication Mode: Disabled
Search Settings:
        Search 1: blah
Remote Role Mapping(s):
        Local Role: dirgroupb3d8954f6ebbe735764e9f7c
        Remote Group: Administrators
        Local Role: dirgroup9d4546a03a03bb977c03086a
        Remote Group: Authenticated Users:S-1-5-11
iLOrest > <font color="#01a982">directory kerberos</font>
Kerberos settings:
--------------------------------
Enabled: False
Service Address: Not Set
Local Account Authorization: Enabled
Port: 1337
Realm: Not Set
Remote Role Mapping(s):
        Local Role: dirgroupb3d8954f6ebbe735764e9f7c
        Remote Group: Administrators
        Local Role: dirgroup9d4546a03a03bb977c03086a
        Remote Group: Authenticated Users:S-1-5-11
</pre>

> To add credentials to a service specify the service with the `ldap` or `kerberos` argument followed by the `USERNAME` and `PASSWORD` of the directory. The `--enable` flag was passed because previously the directory was disabled.

<pre>
iLOrest > <font color="#01a982">directory ldap USERNAME PASSWORD --enable</font>
Changing settings...
The operation completed successfully.
</pre>

> To specify the service address (`--serviceaddress`), port (`--port`), authentication schema (`--authentication`), and/or search strings (`--addsearch/--removesearch`) specify their respective options. Authentication schema and search strings can only be used with the LDAP directory.

<pre>
iLOrest > <font color="#01a982">directory ldap --serviceaddress x.x.y.z --addsearch string3,string4 --authentication=ExtendedSchema --port 199</font>
Changing settings...
The operation completed successfully.
iLOrest > directory ldap
LDAP settings:
--------------------------------
Enabled: True
Service Address: x.x.y.z
Local Account Authorization: Enabled
Port: 199
Authentication Mode: ExtendedSchema
Search Settings:
        Search 1: blah
        Search 2: string3
        Search 3: string4
Remote Role Mapping(s):
        Local Role: dirgroupb3d8954f6ebbe735764e9f7c
        Remote Group: Administrators
        Local Role: dirgroup9d4546a03a03bb977c03086a
        Remote Group: Authenticated Users:S-1-5-11
</pre>

> To specify the realm (`--realm`) and/or key tab (`--keytab`) specify their respective options. Realm and key tab can only be used with the Kerberos directory.

<pre>
iLOrest > <font color="#01a982">directory kerberos --realm Forgotten --keytab http://location/to/keytab.txt</font>
Changing settings...
The operation completed successfully.
Adding keytab...
The operation completed successfully.
</pre>

> To add directory role maps include the `ldap` argument with the `--addrolemap` option with the form `LocalRole:RemoteRoleGroup:OptionalSID`. Available roles can be found in the help text.

<pre>
iLOrest > directory ldap <font color="#01a982">--addrolemap "Administrator:Owners,ReadOnly:Reading Users:S-1-7-23"</font>
Changing settings...
The operation completed successfully.
iLOrest > directory ldap
LDAP settings:
--------------------------------
Enabled: True
Service Address: x.x.y.z:199
Local Account Authorization: Enabled
Port: 199
Authentication Mode: ExtendedSchema
Search Settings:
        Search 1: blah
        Search 2: string3
        Search 3: string4
Remote Role Mapping(s):
        Local Role: dirgroupb3d8954f6ebbe735764e9f7c
        Remote Group: Administrators
        Local Role: dirgroup9d4546a03a03bb977c03086a
        Remote Group: Authenticated Users:S-1-5-11
        Local Role: dirgroupb3b74668da9b6b0bc6864223
        Remote Group: Owners
        Local Role: dirgroup8e167f4006abce0ae22977d4
        Remote Group: Reading Users:S-1-7-23
</pre>

> To add custom local role maps include the `ldap` argument with the `--addrolemap` option with the form `PrivNum1;PrivNum2;...:RemoteRoleGroup:OptionalSID`. Numbers of privileges can be found in the help text.

<pre>
iLOrest > directory ldap --addrolemap "<font color="#01a982">1;2;3</font>:remoterole,<font color="#01a982">10;2;3</font>:Another remote role:S-1-7-23"
Changing settings...
The operation completed successfully.
Updating privileges of created role maps...
The operation completed successfully.
Updated privileges for ANOTHERETSTT
The operation completed successfully.
Updated privileges for A TESTTT:S-1-7-23
</pre>

> To remove directory role maps include the `ldap` argument with the `--removerolemap` option specifying the `LocalRole` of the role map to remove. Multiple role maps can be removed by separating them with commas.

<pre>
iLOrest > directory ldap <font color="#01a982">--removerole dirgroupb3b74668da9b6b0bc6864223,dirgroup8e167f4006abce0ae22977d4</font>
Changing settings...
The operation completed successfully.
iLOrest > directory ldap
LDAP settings:
--------------------------------
Enabled: True
Service Address: x.x.y.z:199
Local Account Authorization: Enabled
Port: 199
Authentication Mode: ExtendedSchema
Search Settings:
        Search 1: blah
        Search 2: string3
        Search 3: string4
Remote Role Mapping(s):
        Local Role: dirgroupb3d8954f6ebbe735764e9f7c
        Remote Group: Administrators
        Local Role: dirgroup9d4546a03a03bb977c03086a
        Remote Group: Authenticated Users:S-1-5-11
</pre>

> To perform directory tests use the `test` argument followed by `start` to start the directory test, `stop` to stop the directory test, or `viewresults` to view the results of the last directory test.

<pre>
iLOrest > <font color="#01a982">directory test start</font>
Starting the directory test. Monitor results with command: directory viewresults
[200] The operation completed successfully.
iLOrest > <font color="#01a982">directory test stop</font>
Stopping the directory test.
[200] The operation completed successfully.
iLOrest > <font color="#01a982">directory test viewresults</font>
Test: Directory Server DNS Name
------------------------
Status: Failed
Notes: Unable to resolve host name x.x.y.z:199

Test: Ping Directory Server
------------------------
Status: Failed
Notes:

Test: Connect to Directory Server
------------------------
Status: Failed
Notes: Unable to connect to the directory server LDAP port within timeout. Verify directory server address. Use this to ensure iLO can correctly connect and use the directory server.

Test: Connect using SSL
------------------------
Status: Failed
Notes: Unable to connect to directory server within timeout.

Test: Bind to Directory Server
------------------------
Status: NotRun
Notes:

Test: Directory Administrator login
------------------------
Status: NotRun
Notes:

Test: User Authentication
------------------------
Status: NotRun
Notes:

Test: User Authorization
------------------------
Status: Failed
Notes:

Test: Directory User Contexts
------------------------
Status: NotRun
Notes:

Test: LOM Object exists
------------------------
Status: NotRun
Notes:

</pre>

#### Syntax

directory [kerberos/ldap/test] [OPTIONS]

#### Description


This command will view/update Kerberos or LDAP directory settings, add/delete directory roles, and test directory settings.

#### Parameters

- **ldap**

Use this parameter to update or view LDAP settings.

- **kerberos**

Use this parameter to update or view Kerberos (Active Directory) settings.

- **test**

Use this parameter to perform directory tests.

- **-h, --help**

Including the help flag will display help for the command.

- **--enable, --disable**

Use this command to enable or disable the LDAP or Kerberos services.

- **--serviceaddress=SERVICEADDRESS**

Use this command to set the service address of the LDAP or Kerberos Services.

- **--port=PORT**

Use this command to set the port of the LDAP or Kerberos services.

- **--realm=REALM**

Use this command to set the Kerberos realm.

- **--keytab=KEYTAB**

Use this command to import a Kerberos Keytab by its URI location.

- **--enablelocalauth, --disablelocalauth**

Use this command to enable or disable the authentication for local accounts.

- **--authentication=AUTHMODE**

Use this command to choose a LDAP authentication mode. The available modes are DefaultSchema (Directory Default Schema or Schema-   free) and ExtendedSchema (HPE Extended Schema).

- **--addsearch=SEARCH, --removesearch=SEARCH**

Use this command to add or remove search strings for generic LDAP services.

- **--addrolemap=ROLES, --removerolemap=ROLES**

Use this command to add or remove Role Mapping(s) for the LDAP and Kerberos services.

<aside class="notice">
When adding role map, SID is optional.
</aside>

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

-
**--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

- **-j, --json**

Use this command to change the displayed output to JSON format. Preserving the JSON data structure makes the information easier to parse.

#### Inputs
None

#### Outputs
None


### Disableilofunctionality command

> Disableilofunctionality example commands:

> To Disable iLO functionality run the command without arguments.

<pre>
iLOrest > <font color="#01a982">disableilofunctionality</font>
The operation completed successfully.
Disabling iLO functionality. iLO will be unavailable on the logged in server until it is re-enabled manually.
[200] The operation completed successfully.
</pre>



#### Syntax

disableilofunctionality *[Optional Parameters]*

#### Description
Disable iLO functionality on the current logged in server.

<aside class="notice">Add the --force flag to ignore critical task checking before disabling iLO.</aside>

<aside class="warning">This will render iLO unable to respond to network operations and Redfish will be unavailable until iLO functionality is restored.</aside>

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

- **--force**

Ignore any critical task checking and force disable iLO.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

#### Inputs
None

#### Outputs
None

### Eskm command

> Eskm example commands:

> To clear the ESKM logs use the `clearlog` argument.

<pre>
iLOrest > <font color="#01a982">eskm clearlog</font>
The operation completed successfully.
</pre>

> To test the ESKM connections use the `testconnections` argument. The response will indicate if the system can connect properly or if there is an issue.

<pre>
iLOrest > <font color="#01a982">eskm testconnections</font>
Enterprise Secure Key Manager Servers are not configured.
</pre>

#### Syntax

eskm *[Command]* *[Optional Parameters]*

#### Description
Command for testing connections to the Enterprise Secure Key Manager system and clearing the Enterprise Secure Key Manager logs.

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

#### Inputs
None

#### Outputs
None

### Factorydefaults command

<aside class="warning">This command will erase all iLO user setting data and reset iLO. Default credentials are required to access iLO after a factory reset.</aside>

> Factorydefaults example commands:

> To reset iLO to factory defaults in the current logged in server run the command without arguments.

<pre>
iLOrest > <font color="#01a982">factorydefaults</font>
Resetting iLO to factory default settings
Current session will be terminated.
The operation completed successfully.
</pre>


#### Syntax

factorydefaults *[Optional Parameters]*

#### Description
Reset iLO to factory defaults in the current logged in server.


#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.


#### Inputs
None



#### Outputs
None

### Firmwareupdate command

> Firmware update example commands:

> To update firmware specify the URI location of the firmware. iLO will then gather the file and flash it. The user will be logged out after firmware update completes successfully.

<aside class="notice">
iLO does not always reset after a firmware update.
</aside>

<pre>
iLOrest > <font color="#01a982">firmwareupdate http://firmwarehost/path/to/firmware/file.bin</font>

Starting upgrading process...

iLO is uploading the necessary files. Please wait...

Updating: \

Firmware update has completed and iLO may reset.
If iLO resets the session will be terminated.
Please wait for iLO to initialize completely before logging in again.
A reboot may be required for firmware changes to take effect.
Logging session out.
</pre>


#### Syntax

Firmwareupdate *[URI] [Optional Parameters]*

#### Description

Use this command to update the firmware via URI. iLO must be able to access the URI for update to complete successfully. This command only supports firmware with a `.bin` extension.

<aside class="notice">The firmware update command is only supported in <b>iLO 4 2.20</b> or higher.</aside>

#### Parameters

- **URI**

Point the **firmwareupdate** command towards the .bin file that holds the file for the firmware update.

- **-h, --help**

Including the help flag will display help for the command.

- **--tpmenabled**

Use this flag if the server you are currently logged into has a TPM chip installed.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

#### Inputs

File

Input a URI pointing to a `.bin` file to perform the `firmwareupdate` command. The .bin file should hold the file needed to perform the firmware update.

#### Outputs

None

### Fwintegritycheck command

> Fwintegritycheck example commands:

> To perform a firmware integrity check run the command without arguments.

<pre>
iLOrest > <font color="#01a982">fwintegritycheck</font>
The operation completed successfully.
</pre>

> To perform a firmware integrity check and return results of the check include the `--results` option.

<pre>
iLOrest > fwintegritycheck <font color="#01a982">--results</font>
The operation completed successfully.
Awaiting results of firmware integrity check....
Scan Result: OK
</pre>



#### Syntax

fwintegritycheck *[Optional Parameters]*

#### Description
Perform a firmware integrity check on the current logged in server.

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

- **--results**

Optionally include this flag to show results of firmware integrity check.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

#### Inputs
None


#### Outputs
None

### Iloaccounts command

When applying privileges directly use the following numbers to specify privileges.

PRIVILEGES:

1. Login
2. Remote Console
3. User Config
4. iLO Config
5. Virtual Media
6. Virtual Power and Reset

iLO 5 added privileges:

7. Host NIC Config
8. Host Bios Config
9. Host Storage Config
10. System Recovery Config

<aside class="notice">
This command has been recently changed. Please review the new method to specify privileges and querying accounts.
</aside>

> Iloaccounts example commands:

> To list the current iLO accounts on the system and their information, run the command without arguments.

<pre>
iLOrest > <font color="#01a982">iloaccounts</font>
Discovering data...Done
iLO Account info:
[Id] UserName (LoginName):
Privileges
-----------------
[1] Administrator (Administrator):
ServiceAccount=False
HostNICConfigPriv=True
HostStorageConfigPriv=True
RemoteConsolePriv=True
iLOConfigPriv=True
VirtualMediaPriv=True
UserConfigPriv=True
HostBIOSConfigPriv=True
VirtualPowerAndResetPriv=True
LoginPriv=True
SystemRecoveryConfigPriv=True

</pre>

> To add an iLO account include the `add` argument with the new account `USERNAME`, `LOGINNAME`, and `PASSWORD`. To optionally specify privileges at creation, use the `--addprivs` option with numbers from the privilege list.

<pre>
iLOrest > <font color="#01a982">iloaccounts add USERNAME ACCOUNTNAME PASSWORD --addprivs 1,4,7</font>
[201] The operation completed successfully.
iLOrest > iloaccounts
iLO Account info:
[Id] UserName (LoginName):
Privileges
-----------------
[1] Administrator (Administrator):
ServiceAccount=False
HostNICConfigPriv=True
HostStorageConfigPriv=True
RemoteConsolePriv=True
iLOConfigPriv=True
VirtualMediaPriv=True
UserConfigPriv=True
HostBIOSConfigPriv=True
VirtualPowerAndResetPriv=True
LoginPriv=True
SystemRecoveryConfigPriv=True

[3] USERNAME (ACCOUNTNAME):
ServiceAccount=False
HostNICConfigPriv=True
HostStorageConfigPriv=False
RemoteConsolePriv=False
iLOConfigPriv=True
VirtualMediaPriv=False
UserConfigPriv=False
HostBIOSConfigPriv=False
VirtualPowerAndResetPriv=False
LoginPriv=True
SystemRecoveryConfigPriv=False

</pre>

> To modify an iLO account's privileges include the `modify` argument, the `Id` or the `Username` of the account to modify, and include the `--addprivs` and/or `--removeprivs` options with numbers from the privilege list.

<pre>
iLOrest > iloaccounts
...
[3] USERNAME (ACCOUNTNAME):
ServiceAccount=False
HostNICConfigPriv=True
HostStorageConfigPriv=False
RemoteConsolePriv=False
iLOConfigPriv=True
VirtualMediaPriv=False
UserConfigPriv=False
HostBIOSConfigPriv=False
VirtualPowerAndResetPriv=False
LoginPriv=True
SystemRecoveryConfigPriv=False

iLOrest > <font color="#01a982">iloaccounts modify USERNAME --addprivs 2,3 --removeprivs 7</font>
The account was modified successfully.
iLOrest > iloaccounts
...
[3] USERNAME (ACCOUNTNAME):
ServiceAccount=False
HostNICConfigPriv=False
HostStorageConfigPriv=False
RemoteConsolePriv=True
iLOConfigPriv=True
VirtualMediaPriv=False
UserConfigPriv=True
HostBIOSConfigPriv=False
VirtualPowerAndResetPriv=False
LoginPriv=True
SystemRecoveryConfigPriv=False
</pre>

> To change the password of an account run the command with the `changepass` argument, specifying the `Id` or the `Username` of the account to modify and the new password.

<pre>
iLOrest > <font color="#01a982">iloaccounts changepass 3 newpassword</font>
The account was modified successfully.
</pre>

> To delete an iLO account run the command with the `delete` argument, specifying the `Id` or the `Username` of the account for deletion.

<pre>
iLOrest > <font color="#01a982">iloaccounts delete USERNAME</font>
The account was removed successfully.
</pre>

> To add a certificate to an account run the command with the `addcert` argument, specifying the `Id` or `Username` of the account followed by the path to an x.509 certificate.

<pre>
iLOrest > <font color="#01a982">iloaccounts addcert 3 C:\Temp\cert.txt</font>
The account was modified successfully.
</pre>

> To delete a certificate from an account run the command with the `deletecert` argument, specifying either the `Id` or `Username` of the account.

<pre>
iLOrest > <font color="#01a982">iloaccounts deletecert 3</font>
The account was modified successfully.
</pre>

> To verify the certificate run a `rawget`

<pre>
iLOrest > <font color="#01a982">rawget "/redfish/v1/AccountService/UserCertificateMapping/?$expand=."</font>
[200] The operation completed successfully.
{
	... Truncated...
	"Members": [
	{
	      "@odata.context": "/redfish/v1/$metadata#HpeiLOAccountCertificateMap.HpeiLOAccountCertificateMap",
	      "@odata.id": "/redfish/v1/AccountService/UserCertificateMapping/1/",
	      "@odata.type": "#HpeiLOAccountCertificateMap.v1_0_1.HpeiLOAccountCertificateMap",
	      "Fingerprint": "00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00",
	      "FingerprintDigestAlgorithm": "SHA256",
	      "Id": "1",
	      "UserName": "Administrator"
	},
	{
	      "@odata.context": "/redfish/v1/$metadata#HpeiLOAccountCertificateMap.HpeiLOAccountCertificateMap",
	      "@odata.id": "/redfish/v1/AccountService/UserCertificateMapping/9/",
	      "@odata.type": "#HpeiLOAccountCertificateMap.v1_0_1.HpeiLOAccountCertificateMap",
	      "Fingerprint": "00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00",
	      "FingerprintDigestAlgorithm": "SHA256",
	      "Id": "3",
	      "UserName": "USERNAME"
	}
	]
}
</pre>


#### Syntax

iloaccounts *[COMMAND] [OPTIONS]*

#### Description

Adds/deletes an iLO account on the currently logged in server and modifies iLO account privileges.

- **LOGINNAME:**  The account name, not used to login.
- **USERNAME:** The account username name, used to login.
- **PASSWORD:**  The account password, used to login.
- **Id:** The number associated with an iLO user account.
- **PRIVILEGES:**
  * 1: Login
  * 2: Remote Console
  * 3: User Config
  * 4: iLO Config
  * 5: Virtual Media
  * 6: Virtual Power and Reset

- **iLO 5 added privileges:**
  * 7: Host NIC Config
  * 8: Host Bios Config
  * 9: Host Storage Config
  * 10: System Recovery Config

- **Roles:**
  * Administrator
  * ReadOnly
  * Operator

<aside class="notice">By default, only login privilege is added to the newly created account with role "ReadOnly" in iLO 5 and no privileges in iLO 4. To modify these privileges, you can remove properties that would be set by using --removeprivs or you can directly set which privileges are given using --addprivs.</aside>

<aside class="notice">
Please make sure the order of arguments is correct. The
parameters are extracted based on their position in the arguments list.
Only privileges available to the logged in account can be set to the new account.
</aside>

<aside class="notice">
Account credentials are case-sensitive.
</aside>


#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

- **--addprivs=OPTPRIVS**

Optionally include this flag if you wish to specify which privileges you want added to the iLO account. Pick privileges from the privilege list in the above help text. Example: --addprivs=1,2,4

- **--removeprivs=OPTPRIVS**

Optionally include this flag if you wish to specify which privileges you want removed from the iLO account. Pick privileges from the privilege list in the above help text. Example: --removeprivs=1,2,4

- **--role=ROLE**

Optionally include this flag if you would like to specify Privileges by role. Valid choices are: Administrator, ReadOnly, and Operator.

- **-j, --json**

Optionally include this flag if you wish to change the displayed output to JSON format. Preserving the JSON data structure makes the information easier to parse.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

#### Inputs
None


#### Outputs
None


### Iloclone command <font color="#b62424">(Deprecated)</font>

<aside class="warning">
The iloclone command is being deprecated and will be removed in a future version. Use the <a href="#serverclone-command">serverclone command</a> instead.
</aside>

> Iloclone  example commands:

> To create a clone file from the current logged in server run the command with the `save` argument. You can specify a save file using the (`-f, --filename`) option.

<pre>
iLOrest > <font color="#01a982">iloclone save</font>
WARNING: iloclone command is being deprecated and will be removed in a future version. Use the serverclone command instead.
Gathering data required for clone. This may take a while...
You may be prompted to enter some information to complete the clone file.
Please input the password for user, Administrator:
Password:
Please input the key for federation, DEFAULT:
Password:
Configuration saved to: clone.json
</pre>


> To load the saved clone file to currently logged in server run the command with the `load` argument. You can specify a load file using the (`-f, --filename`) option.

<pre>
iLOrest > <font color="#01a982">iloclone load</font>
WARNING: iloclone command is being deprecated and will be removed in a future version. Use the serverclone command instead.
Are you sure you would like to continue? All user settings will be erased. (y/n)y

Patching: /redfish/v1/AccountService/Accounts/1/
iLO response with code [400]: The user or login user name already exists.

Posting: /redfish/v1/AccountService/Accounts/
[201] The operation completed successfully.

Posting: /redfish/v1/AccountService/Accounts/
[201] The operation completed successfully.

Posting: /redfish/v1/AccountService/Accounts/
[201] The operation completed successfully.

Patching: /redfish/v1/AccountService/
[201] The operation completed successfully.

Patching: /redfish/v1/Managers/1/EthernetInterfaces/1/
One or more properties were changed, but these changes will not take effect until the management processor is reset.

Patching: /redfish/v1/Managers/1/EthernetInterfaces/2/
One or more properties were changed, but these changes will not take effect until the management processor is reset.

Patching: /redfish/v1/Managers/1/
The operation completed successfully.

Patching: /redfish/v1/Managers/1/DateTime/
One or more properties were changed, but these changes will not take effect until the management processor is reset.

Patching: /redfish/v1/Managers/1/SnmpService/
The operation completed successfully.

Patching: /redfish/v1/Managers/1/FederationGroups/DEFAULT/
The operation completed successfully.

Patching: /redfish/v1/Managers/1/SecurityService/SSO/
The operation completed successfully.

Patching: /redfish/v1/Systems/1/
The operation completed successfully.

Patching: /redfish/v1/Chassis/1/Power/
The operation completed successfully.

Patching: /redfish/v1/systems/1/bios/settings/
One or more properties were changed and will not take effect until system is reset.

Patching: /redfish/v1/systems/1/bios/boot/settings/
One or more properties were changed and will not take effect until system is reset.

Patching: /redfish/v1/Systems/1/SecureBoot/
One or more properties were changed and will not take effect until system is reset.

Patching: /redfish/v1/Managers/1/NetworkProtocol/
One or more properties were changed, but these changes will not take effect until the management processor is reset.
Waiting for iLO to reset...
3 minutes remaining...
2 minutes remaining...
1 minute remaining...
</pre>


#### Syntax

iloclone *[Optional Parameters]*

#### Description

Command to clone the iLO and BIOS config of the currently logged in server and copy it to other server(s).

<aside class="notice">
This command is only available in local mode. During clone load, login using an iLO account with full privileges (such as the Administrator account) to ensure all items are cloned successfully.
</aside>

<aside class="notice">
The JSON file created by the save command is tailored for the iLO clone command. Manipulating the file may cause errors when running the load command.
</aside>

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

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

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

#### Inputs
None


#### Outputs
None


### Ilofederation command

When applying privileges directly use the following numbers to specify privileges.

PRIVILEGES:

1. Login
2. Remote Console
3. User Config
4. iLO Config
5. Virtual Media
6. Virtual Power and Reset

iLO 5 added privileges:

7. Host NIC Config
8. Host Bios Config
9. Host Storage Config
10. System Recovery Config

<aside class="notice">
Please make sure the order of arguments is correct. The parameters are extracted based on their position in the arguments list.
</aside>

<aside class="notice">
The federation key must be 8 characters or greater.
</aside>

> Ilofederation example commands:


> To add an iLO federation group to the current logged in server include the `add` argument with the new federation name and federation key. To optionally specify privileges at creation, use the `--addprivs` option with numbers from the privilege list.

<pre>
iLOrest > ilofederation
iLO Federation Id list with Privileges:

Name=DEFAULT:
HostNICConfigPriv=False
HostStorageConfigPriv=False
RemoteConsolePriv=False
iLOConfigPriv=False
VirtualMediaPriv=False
UserConfigPriv=False
HostBIOSConfigPriv=False
VirtualPowerAndResetPriv=False
LoginPriv=True
SystemRecoveryConfigPriv=False
iLOrest > <font color="#01a982">ilofederation add newfedname 8charfedkey --addprivs 1,3,5</font>
The resource has been created successfully.
iLOrest > ilofederation
iLO Federation Id list with Privileges:

Name=DEFAULT:
HostNICConfigPriv=False
HostStorageConfigPriv=False
RemoteConsolePriv=False
iLOConfigPriv=False
VirtualMediaPriv=False
UserConfigPriv=False
HostBIOSConfigPriv=False
VirtualPowerAndResetPriv=False
LoginPriv=True
SystemRecoveryConfigPriv=False

Name=newfedname:
HostNICConfigPriv=False
HostStorageConfigPriv=False
RemoteConsolePriv=False
iLOConfigPriv=False
VirtualMediaPriv=True
UserConfigPriv=True
HostBIOSConfigPriv=False
VirtualPowerAndResetPriv=False
LoginPriv=True
SystemRecoveryConfigPriv=False
</pre>


> To list the current iLO federations and their information run the command with no arguments.

<pre>

iLOrest > <font color="#01a982">ilofederation</font>
iLO Federation Id list with Privileges:

Name=DEFAULT:
HostNICConfigPriv=False
HostStorageConfigPriv=False
RemoteConsolePriv=False
iLOConfigPriv=False
VirtualMediaPriv=False
UserConfigPriv=False
HostBIOSConfigPriv=False
VirtualPowerAndResetPriv=False
LoginPriv=True
SystemRecoveryConfigPriv=False
</pre>


> To change the key of an iLO federation group include the `changekey` argument with the federation name and the new key.

<pre>
iLOrest > <font color="#01a982">ilofederation changekey newfedname newfedkey</font>
The operation completed successfully.
</pre>

> To delete an iLO federation group include the `delete` argument with the federation name to delete.

<pre>
iLOrest > ilofederation
iLO Federation Id list with Privileges:

Name=DEFAULT:
HostNICConfigPriv=False
HostStorageConfigPriv=False
RemoteConsolePriv=False
iLOConfigPriv=False
VirtualMediaPriv=False
UserConfigPriv=False
HostBIOSConfigPriv=False
VirtualPowerAndResetPriv=False
LoginPriv=True
SystemRecoveryConfigPriv=False

Name=newfedname:
HostNICConfigPriv=True
HostStorageConfigPriv=True
RemoteConsolePriv=True
iLOConfigPriv=True
VirtualMediaPriv=True
UserConfigPriv=True
HostBIOSConfigPriv=True
VirtualPowerAndResetPriv=True
LoginPriv=True
SystemRecoveryConfigPriv=True
iLOrest > <font color="#01a982">ilofederation delete newfedname</font>
The operation completed successfully.
iLOrest > ilofederation
iLO Federation Id list with Privileges:

Name=DEFAULT:
HostNICConfigPriv=False
HostStorageConfigPriv=False
RemoteConsolePriv=False
iLOConfigPriv=False
VirtualMediaPriv=False
UserConfigPriv=False
HostBIOSConfigPriv=False
VirtualPowerAndResetPriv=False
LoginPriv=True
SystemRecoveryConfigPriv=False
</pre>

> To modify an iLO federation group include the `modify` argument with the federation name you'd like to update.

<pre>
iLOrest > <font color="#01a982">ilofederation modify newfederation 8charfedkey --addprivs 1,2,3,4</font>
The resource has been created successfully.
iLOrest > ilofederation
iLO Federation Id list with Privileges:

Name=DEFAULT:
HostNICConfigPriv=False
HostStorageConfigPriv=False
RemoteConsolePriv=False
iLOConfigPriv=False
VirtualMediaPriv=False
UserConfigPriv=False
HostBIOSConfigPriv=False
VirtualPowerAndResetPriv=False
LoginPriv=True
SystemRecoveryConfigPriv=False

Name=newfederation
HostNICConfigPriv=False
HostStorageConfigPriv=False
RemoteConsolePriv=True
iLOConfigPriv=True
VirtualMediaPriv=False
UserConfigPriv=True
HostBIOSConfigPriv=False
VirtualPowerAndResetPriv=False
LoginPriv=True
SystemRecoveryConfigPriv=False
iLOrest > <font color="#01a982">ilofederation modify newfederation --removeprivs 1,2,3</font>
The operation completed successfully
iLOrest > ilofederation
Name=DEFAULT:
HostNICConfigPriv=False
HostStorageConfigPriv=False
RemoteConsolePriv=False
iLOConfigPriv=False
VirtualMediaPriv=False
UserConfigPriv=False
HostBIOSConfigPriv=False
VirtualPowerAndResetPriv=False
LoginPriv=True
SystemRecoveryConfigPriv=False

Name=newfederation
HostNICConfigPriv=False
HostStorageConfigPriv=False
RemoteConsolePriv=False
iLOConfigPriv=True
VirtualMediaPriv=False
UserConfigPriv=False
HostBIOSConfigPriv=False
VirtualPowerAndResetPriv=False
LoginPriv=False
SystemRecoveryConfigPriv=False
</pre>


#### Syntax

ilofederation *[COMMAND] [ARGUMENTS] [OPTIONS]*

#### Description

Adds, deletes, or modifies an iLO federation group on the currently logged in server.

- **FEDERATIONNAME**: The name (Id) of the federation group.
- **KEY**:  The key required to join the federation.
- **Id**: The number associated with an iLO federation.

- **PRIVILEGES:**
  * 1: Login
  * 2: Remote Console
  * 3: User Config
  * 4: iLO Config
  * 5: Virtual Media
  * 6: Virtual Power and Reset

- **iLO 5 added privileges:**
  * 7: Host NIC Config
  * 8: Host Bios Config
  * 9: Host Storage Config
  * 10: System Recovery Config

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

- **--addprivs=PRIVS**

Optionally include this flag if you wish to specify which privileges you want added to the iLO federation. This overrides the default of duplicating privileges of the currently logged in federation on the new federation. Pick privileges from the privilege list in the above help text.

Example: --addprivs=1,2,4

- **--removeprivs=PRIVS**

Optionally include this flag if you wish to specify which privileges you want removed from the iLO federation. This overrides the default of duplicating privileges of the currently logged in federation on the new federation. Pick privileges from the privilege list in the above help text.

Example: --removeprivs=1,2,4

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

#### Inputs
None


#### Outputs
None

### Ilolicense command

> Ilolicense example commands:

> To Apply an iLO license on the current logged in server run the command with the license key as an argument.

<pre>
iLOrest > <font color="#01a982">ilolicense XXXXX-XXXXX-XXXXX-XXXXX-XXXXX</font>
The resource has been created successfully.
</pre>

#### Syntax

ilolicense *[LICENSE_KEY] [OPTIONS]*

#### Description
Applies an iLO license on the currently logged in server.

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

#### Inputs
None


#### Outputs
None

### iLOReset command

<aside class="warning">Resetting iLO will render it unresponseive as it resets. The user will be logged out.</aside>

> iLOReset example commands:

> To reset iLO run the command without arguments.

<pre>
iLOrest > <font color="#01a982">iloreset</font>

After iLO resets the session will be terminated.
Please wait for iLO to initialize completely before logging in again.
This process may take up to 3 minutes.

A management processor reset is in progress.
</pre>



#### Syntax

iloreset *[Optional Parameters]*

#### Description

Run this command to reset iLO on the currently logged in server.

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

#### Inputs

None

#### Outputs

None

### Ipprofiles command

> Ipprofiles example commands:

> To list the current profiles on the server, run the command without arguments..

<pre>
iLOrest > <font color="#01a982">ipprofiles</font>
{
  "@odata.type": "#HpeIpProfiles.v1_0_0.HpeIpProfiles",
  "1540504034216": "{profile: data}"
}
</pre>

> To upload an ipprofile, input a valid JSON file path as an argument.

<pre>
iLOrest > <font color="#01a982">ipprofiles profile.json</font>
The operation completed successfully.
</pre>

> To remove a profile, use the unique key contained in the profile with the `(-d, --delete)` option.

<pre>
iLOrest > ipprofiles <font color="#01a982">-d 1540504034216</font>
The operation completed successfully.
iLOrest > ipprofiles
{
  "@odata.type": "#HpeIpProfiles.v1_0_0.HpeIpProfiles",
  "1549567973200": "{\"profile\": {}}"
}
iLOrest > ipprofiles -d 1549567973200
The operation completed successfully.
iLOrest > ipprofiles
{
  "@odata.type": "#HpeIpProfiles.v1_0_0.HpeIpProfiles"
}
</pre>


#### Syntax

ipprofiles *[Optional Parameters]*

#### Description

Run this command to manage the hpeipprofile data store.

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

- **-f FILENAME, --filename=FILENAME**

Write results to the specified file.

- **-d DEL_KEY, --delete=DEL_KEY**

Look for the key or keys in the ipprofile manager and delete.

- **-s START_IP, --start=START_IP**

Copies the specified IP profile into the job queue and starts it.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

#### Inputs

None

#### Outputs

None

### One Button Erase Command

> To initiate One Button Erase and erase all iLO settings, BIOS settings, User Data, and iLO Repository data run the command without arguments.

<pre>
iLOrest > <font color="#01a982">onebuttonerase</font>
Please type "erase" to begin erase process. Any other input will cancel the operation. If you wish to skip this prompt add the --confirm flag: erase
One or more properties were changed and will not take effect until system is reset.
The operation completed successfully.
        One Button Erase Status
==========================================================
Elapsed time in Minutes: 0
Elapsed Remaining Time in Minutes: 0
Bios Settings Erase: Idle
iLO Settings Erase: Idle
User Data Erase: Initiated /
</pre>

> To optionally skip the confirmation before initiating One Button Erase include the `--confirm` option.

<pre>
iLOrest > <font color="#01a982">onebuttonerase --confirm</font>
One or more properties were changed and will not take effect until system is reset.
The operation completed successfully.
        One Button Erase Status
==========================================================
Elapsed time in Minutes: 0
Elapsed Remaining Time in Minutes: 0
Bios Settings Erase: Idle
iLO Settings Erase: Idle
User Data Erase: Initiated \
</pre>


#### Syntax

onebuttonerase [OPTIONS]

#### Description

Performs One Button Erase on a system. Erases all iLO settings, Bios settings, User Data, and iLO Repository data.

<aside class="warning"> This command will erase user data. Use this command with extreme caution. Complete erase can take up to 24 hours to complete. </aside>

#### Parameter

- **-h, --help**

Including the help flag will display help for the command.

- **--nomonitor**

Use this command to skip monitoring of the one button erase process and simply trigger the operation.

- **--confirm**

Use this command to skip the confirmation prompt before starting One Button Erase and begin the operation.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

#### Inputs
None

#### Outputs
None

### Reboot command

<aside class="notice">The reboot command will log out, the user, from the server. Wait for the system to fully reboot before attempting to login, or data such as Bios may be unavailable.</aside>
<aside class="notice">Arguments are not case-sensitive.</aside>

> Reboot example commands:

> If no arguments are supplied the default operation is `ForceRestart`.

<pre>
iLOrest > <font color="#01a982">reboot</font>

After the server is rebooted the session will be terminated.
Please wait for the server to boot completely to login again.
Rebooting server in 3 seconds...
The operation completed successfully.
Logging session out.
</pre>

> To perform a power function supply one of the reboot type parameters as an argument.

<pre>
iLOrest > <font color="#01a982">reboot ForceOff</font>

Server is powering off the session will be terminated.
Please wait for the server to boot completely to login again.
Powering off the server in 3 seconds...
The operation completed successfully.
Logging session out.
</pre>

> If the current power state does not allow for an operation to complete an error will be returned.

<pre>
iLOrest > <font color="#01a982">reboot On</font>

Session will now be terminated.
Please wait for the server to boot completely to login again.
Turning on the server in 3 seconds...
iLO response with code [400]: The operation was not successful due to the current power state (for example, attempting to turn the power off when it is already off).
</pre>

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

Immediately removes power from the server, followed by a restart of the system.

- **-h, --help**

Including the help flag will display help for the command.

- **--confirm**

Optionally include to request user confirmation for reboot.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

- **--includelogs**

You can optionally choose to set the **includelogs** flag. Doing so will include logs in the data retrieval process.

<aside class="notice">This option can be used to limit long login times.</aside>

#### Inputs

None

#### Outputs

None

### Results command


#### Syntax

results

#### Description

Use this command to retrieve a Redfish response. The results command provides feedback after an iLO state change. The feedback is a list of attributes that have been modified and a short message log that contains details of that state change. The results are limited to Redfish response messages for these groups: BIOS, iSCSI, and Smart Array.

#### Global verbosity options

- **v**

The verbose option provides a brief response message from iLO.

- **vv**

The extended verbosity option provides the following additional information for iLO HTTP and the iLO Channel Interface Driver response messages:
* An error response message id (“MessageId”), iLO response error message code identification.
* An error response message description (“Description”), essentially a quick synopsis of the issue.
* An error response message (“Message”) describing the reason for the error in greater detail. The offending properties are embedded as per the relevant error response resource.
* An error response resolution (“Resolution”) describing steps to correct the error.

> The following example shows extended verbosity:

<pre>
HTTP Response Code: [400]
MessageId: iLO.2.8.PropertyNotWritableOrUnknown
Description: The request included a value for a  read-only or unknown property.
Message: The property "NTPServers" is a read-only property and cannot be assigned a value, or not valid for this resource.
Resolution: If the operation did not complete, remove the property from the request body and resubmit the request.
</pre>

-**d**

The debug option provides a timestamp of all transmit and response activity with iLO to a file called iLOrest.log. This files is saved in the same path where you launched the tool.

>The following example shows the contents of the iLOrest.log file:

<pre>
2020-06-05 14:20:39,266 INFO    : Not using CA certificate.
2020-06-05 14:20:39,267 INFO    : Initializing no proxy.
2020-06-05 14:20:39,267 DEBUG : HTTP REQUEST: GET
            PATH: /redfish/v1/
            HEADERS: {'OData-Version': '4.0', 'Accept-Encoding': 'gzip'}
            BODY: None
2020-06-05 14:20:39,269 DEBUG : Starting new HTTPS connection (1): 16.83.61.104
2020-06-05 14:20:39,884 DEBUG : https://16.83.61.104:443 "GET /redfish/v1/ HTTP/1.1" 200 None
2020-06-05 14:20:39,885 INFO    : Response Time to /redfish/v1/: 0.615999937057 seconds.
2020-06-05 14:20:39,887 DEBUG : HTTP RESPONSE for /redfish/v1/:
Code:200 OK
Headers:
            Transfer-Encoding: chunked
            ETag: W/"16CA421D"
            Link: </redfish/v1/SchemaStore/en/ServiceRoot.json/>; rel=describedby
            Allow: GET, HEAD
            Cache-Control: no-cache
            Date: Fri, 05 Jun 2020 19:21:15 GMT
            OData-Version: 4.0
            X-Frame-Options: sameorigin
            Content-type: application/json; charset=utf-8

Body Response of /redfish/v1/: {"@odata.context":"/redfish/v1/$metadata#ServiceRoot.ServiceRoot","@odata.etag":"W/\"16CA421D\"","@odata.id":"/redfish/v1/","@odata.type":"#ServiceRoot.v1_5_1.ServiceRoot","Id":"RootService","AccountService":{"@odata.id":"/redfish/v1/AccountService/"},"Chassis":{"@odata.id":"/redfish/v1/Chassis/"},"EventService":{"@odata.id":"/redfish/v1/EventService/"},"JsonSchemas":{"@odata.id":"/redfish/v1/JsonSchemas/"},"Links":{"Sessions":{"@odata.id":"/redfish/v1/SessionService/Sessions/"}},"Managers":{"@odata.id":"/redfish/v1/Managers/"},"Name":"HPE RESTful Root Service","Oem":{"Hpe":{"@odata.context":"/redfish/v1/$metadata#HpeiLOServiceExt.HpeiLOServiceExt","@odata.type":"#HpeiLOServiceExt.v2_3_0.HpeiLOServiceExt","Links":{"ResourceDirectory":{"@odata.id":"/redfish/v1/ResourceDirectory/"}},"Manager":[{"DefaultLanguage":"en","FQDN":"ILOMXQ849018N.americas.hpqcorp.net","HostName":"ILOMXQ849018N","Languages":[{"Language":"en","TranslationName":"English","Version":"2.10"}],"ManagerFirmwareVersion":"2.10","ManagerType":"iLO 5","Status":{"Health":"OK"}}],"Moniker":{"ADVLIC":"iLO Advanced","BMC":"iLO","BSYS":"BladeSystem","CLASS":"Baseboard Management Controller","FEDGRP":"DEFAULT","IPROV":"Intelligent Provisioning","PRODABR":"iLO","PRODFAM":"Integrated Lights-Out","PRODGEN":"iLO 5","PRODNAM":"Integrated Lights-Out 5","PRODTAG":"HPE iLO 5","STDLIC":"iLO Standard","SUMABR":"SUM","SUMGR":"Smart Update Manager","SYSFAM":"ProLiant","VENDABR":"HPE","VENDNAM":"Hewlett Packard Enterprise","WWW":"www.hpe.com","WWWAHSV":"www.hpe.com/servers/ahsv","WWWBMC":"www.hpe.com/info/ilo","WWWDOC":"www.hpe.com/support/ilo-docs","WWWERS":"www.hpe.com/services/getconnected","WWWGLIS":"reserved for liconf URI","WWWIOL":"www.hpe.com/info/insightonline","WWWLIC":"www.hpe.com/info/ilo","WWWLML":"www.hpe.com/support","WWWPASS":"www.hpe.com/support/hpesc","WWWPRV":"www.hpe.com/info/privacy","WWWQSPEC":"www.hpe.com/info/qs","WWWRESTDOC":"www.hpe.com/support/restfulinterface/docs","WWWSUP":"www.hpe.com/support/ilo5","WWWSWLIC":"www.hpe.com/software/SWLicensing"},"Sessions":{"CertCommonName":"ILOMXQ849018N.americas.hpqcorp.net","CertificateLoginEnabled":false,"KerberosEnabled":false,"LDAPAuthLicenced":true,"LDAPEnabled":false,"LocalLoginEnabled":true,"LoginFailureDelay":0,"LoginHint":{"Hint":"POST to /Sessions to login using the following JSON object:","HintPOSTData":{"Password":"password","UserName":"username"}},"SecurityOverride":false,"ServerName":""},"System":[{"Status":{"Health":"OK"}}],"Time":"2020-06-05T19:21:15Z"}},"Product":"ProLiant DL360 Gen10","ProtocolFeaturesSupported":{"ExpandQuery":{"ExpandAll":false,"Levels":true,"Links":false,"MaxLevels":1,"NoLinks":true},"FilterQuery":true,"OnlyMemberQuery":true,"SelectQuery":false},"RedfishVersion":"1.6.0","Registries":{"@odata.id":"/redfish/v1/Registries/"},"SessionService":{"@odata.id":"/redfish/v1/SessionService/"},"Systems":{"@odata.id":"/redfish/v1/Systems/"},"Tasks":{"@odata.id":"/redfish/v1/TaskService/"},"TelemetryService":{"@odata.id":"/redfish/v1/TelemetryService/"},"UUID":"d3372204-1b09-54ea-9aa0-88940c369d59","UpdateService":{"@odata.id":"/redfish/v1/UpdateService/"},"Vendor":"HPE"}
</pre>

### Sendtest command

> Sendtest example commands:

> Send syslog test to the current logged in server.

<pre>
iLOrest > <font color="#01a982">sendtest syslog</font>
The operation completed successfully.
</pre>

> Send alert mail test to the current logged in server.

<pre>
iLOrest > <font color="#01a982">sendtest alertmail</font>
The operation completed successfully.
</pre>

> Send SNMP test alert to the current logged in server.

<pre>
iLOrest > <font color="#01a982">sendtest snmpalert</font>
The operation completed successfully.
</pre>



#### Syntax

sendtest *[Test Type] [Optional Parameters]*

#### Description

Command for triggering various tests to iLO.

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.


#### Inputs
None


#### Outputs
None

### Serverclone command

<aside class="notice">
This is a BETA command and is subject to change. Errors may be encountered. All settings may not be able to be transferred on load. If you have any feedback or to report a bug, create an issue on the iLOrest open source GitHub site: https://github.com/HewlettPackard/python-redfish-utility
</aside>

> To save an iLO and Bios config run the command with the `save` argument. You can specify a filename using the (`-f, --filename`) option, if this option is not used the command will search for `ilorest_clone.json`.

<pre>
iLOrest > <font color="#01a982">serverclone save</font>
Saving properties of type: AccountService, path: /redfish/v1/AccountService/
Saving properties of type: Bios, path: /redfish/v1/systems/1/bios/settings/
Saving properties of type: ComputerSystem, path: /redfish/v1/Systems/1/
Saving properties of type: EthernetInterface, path: /redfish/v1/Managers/1/EthernetInterfaces/1/
Saving properties of type: EthernetInterface, path: /redfish/v1/Managers/1/EthernetInterfaces/2/
Saving properties of type: HpeESKM, path: /redfish/v1/Managers/1/SecurityService/ESKM/
Saving properties of type: HpeServerBootSettings, path: /redfish/v1/systems/1/bios/boot/settings/
Saving properties of type: HpeiLODateTime, path: /redfish/v1/Managers/1/DateTime/
Please input the federation key for Federation user: DEFAULT
Password: password
Please re-enter the federation key for Federation user: DEFAULT
Password: password
Saving properties of type: HpeiLOFederationGroup, path: /redfish/v1/Managers/1/FederationGroups/DEFAULT/
License Key Found ending in XXXXX:
Remember to edit your License Key...
Saving properties of type: HpeiLOLicense, path: /redfish/v1/Managers/1/LicenseService/1/
Saving properties of type: HpeiLOSSO, path: /redfish/v1/Managers/1/SecurityService/SSO/
Saving properties of type: HpeiLOSnmpService, path: /redfish/v1/Managers/1/SnmpService/
Saving properties of type: Manager, path: /redfish/v1/Managers/1/
Password: Please input the desired password for user: Administrator
password
Please re-enter the desired password for user: Administrator
Password: password
Saving properties of type: ManagerAccount, path: /redfish/v1/AccountService/Accounts/7/
Please input the desired password for user: tiQiR2
Password:
Using a placeholder password of '<pass>' in ilorest_clone.json file.
Saving properties of type: ManagerAccount, path: /redfish/v1/AccountService/Accounts/8/
Saving properties of type: ManagerNetworkProtocol, path: /redfish/v1/Managers/1/NetworkProtocol/
Saving properties of type: SecureBoot, path: /redfish/v1/Systems/1/SecureBoot/
Saving properties of type: SmartStorageConfig, path: /redfish/v1/systems/1/smartstorageconfig/settings/
Saving of clonefile to 'ilorest_clone.json' is complete.
</pre>

> To save an iLO and Bios config while providing a placeholder value for all user inputs run the command with the `save` argument and include the (`--quiet`) option. This option can be used to problematically create a file without user input and then use a script to fill in the settings.

<pre>
iLOrest > serverclone save <font color="#01a982">--silent</font>
Saving properties of type: AccountService, path: /redfish/v1/AccountService/
Saving properties of type: Bios, path: /redfish/v1/systems/1/bios/settings/
Saving properties of type: ComputerSystem, path: /redfish/v1/Systems/1/
Saving properties of type: EthernetInterface, path: /redfish/v1/Managers/1/EthernetInterfaces/1/
Saving properties of type: EthernetInterface, path: /redfish/v1/Managers/1/EthernetInterfaces/2/
Saving properties of type: HpeESKM, path: /redfish/v1/Managers/1/SecurityService/ESKM/
Saving properties of type: HpeSNMPAlertDestination, path: /redfish/v1/Managers/1/SnmpService/SNMPAlertDestinations/1/
Saving properties of type: HpeServerBootSettings, path: /redfish/v1/systems/1/bios/boot/settings/
Saving properties of type: HpeiLODateTime, path: /redfish/v1/Managers/1/DateTime/
Remember to edit the Federation key for acct: 'DEFAULT'.
Saving properties of type: HpeiLOFederationGroup, path: /redfish/v1/Managers/1/FederationGroups/DEFAULT/
Remember to edit the Federation key for acct: 'fed1'.
Saving properties of type: HpeiLOFederationGroup, path: /redfish/v1/Managers/1/FederationGroups/f250jenkins/
Remember to edit the Federation key for acct: '9P0Rn2'.
Saving properties of type: HpeiLOFederationGroup, path: /redfish/v1/Managers/1/FederationGroups/9P0Rn2/
License Key Found ending in: XXXXX
Remember to verify your License Key...
Saving properties of type: HpeiLOLicense, path: /redfish/v1/Managers/1/LicenseService/1/
Saving properties of type: HpeiLOSSO, path: /redfish/v1/Managers/1/SecurityService/SSO/
Saving properties of type: HpeiLOSnmpService, path: /redfish/v1/Managers/1/SnmpService/
Saving properties of type: Manager, path: /redfish/v1/Managers/1/
Remember to edit password for user: 'Administrator', login name: 'Administrator'.
Saving properties of type: ManagerAccount, path: /redfish/v1/AccountService/Accounts/1/
Remember to edit password for user: 'username', login name: 'username'.
Saving properties of type: ManagerAccount, path: /redfish/v1/AccountService/Accounts/2/
Remember to edit password for user: 'admin', login name: 'admin'.
Saving properties of type: ManagerAccount, path: /redfish/v1/AccountService/Accounts/120/
Saving properties of type: ManagerNetworkProtocol, path: /redfish/v1/Managers/1/NetworkProtocol/
Saving properties of type: SecureBoot, path: /redfish/v1/Systems/1/SecureBoot/
Saving properties of type: SmartStorageConfig, path: /redfish/v1/systems/1/smartstorageconfig/settings/
Saving of clonefile to 'ilorest_clone.json' is complete.
</pre>

> To load a clone file run the command with the `load` argument. You can specify a filename using the (`-f, --filename`) option, if this option is not used the command will search for `ilorest_clone.json`.

<pre>
iLOrest > <font color="#01a982">serverclone load -f ilorest_clone.json</font>
A configuration file 'ilorest_clone.json' containing configuration changes will be applied to this iLO server resulting in system setting changes for BIOS, ethernet controllers, disk controllers, deletion and rearrangement of logical disks...etc. Please confirm you acknowledge and would like to perform this operation now? (y/n)

Proceeding with ServerClone Load Operation...
This system has BIOS Version U32.
BIOS Versions are different. Suggest to have 'U30' in place before upgrading.
This system has has iLO 5 with firmware revision 1.40.
iLO Versions are compatible.
iLO Firmware Revisions are compatible.
Would you like to continue with migration of iLO configuration from 'ProLiant DL380 Gen10' to 'ProLiant DL360 Gen10'? (y/n)

Attempting Clone from a 'ProLiant DL380 Gen10' to a 'ProLiant DL360 Gen10'.
The contents of type: '#HpeServerBootSettings.v2_0_0.HpeServerBootSettings' should be compatible with '#HpeServerBootSettings.v2_0_0.HpeServerBootSettings', on this system.
The contents of type: '#SecureBoot.v1_0_0.SecureBoot' should be compatible with '#SecureBoot.v1_0_0.SecureBoot', on this system.
The contents of type: '#Manager.v1_3_3.Manager' should be compatible with '#Manager.v1_3_3.Manager', on this system.
The contents of type: '#Bios.v1_0_0.Bios' should be compatible with '#Bios.v1_0_0.Bios', on this system.
The contents of type: '#HpeiLOSSO.v2_0_0.HpeiLOSSO' should be compatible with '#HpeiLOSSO.v2_0_0.HpeiLOSSO', on this system.
The contents of type: '#HpeiLOSnmpService.v2_2_0.HpeiLOSnmpService' should be compatible with '#HpeiLOSnmpService.v2_2_0.HpeiLOSnmpService', on this system.
The contents of type: '#HpeiLOFederationGroup.v2_0_0.HpeiLOFederationGroup' should be compatible with '#HpeiLOFederationGroup.v2_0_0.HpeiLOFederationGroup', on this system.
Adding 'DEFAULT' to iLO Federation.
This account already exists on this system: 'DEFAULT'
Changing Federation account: 'DEFAULT's' key. Privileges will not be altered.
The operation completed successfully.
The contents of type: '#HpeiLODateTime.v2_0_0.HpeiLODateTime' should be compatible with '#HpeiLODateTime.v2_0_0.HpeiLODateTime', on this system.
The contents of type: '#ManagerAccount.v1_1_3.ManagerAccount' should be compatible with '#ManagerAccount.v1_1_3.ManagerAccount', on this system.
Adding user 'Ldpksh' to iLO Accounts.
The account name 'Ldpksh' already exists on this system.
Checking for and implementing account modification.
Changing account password for 'Ldpksh'.
The account was modified successfully.
Changing privileges for 'Ldpksh'.
The account was modified successfully.
The contents of type: '#ManagerAccount.v1_1_3.ManagerAccount' should be compatible with '#ManagerAccount.v1_1_3.ManagerAccount', on this system.
Adding user 'Administrator' to iLO Accounts.
An error occurred: Privilege SystemRecoveryConfigPriv is not available on this iLO version.. Check the ServerClone Error logfile for further info: clone_error_logfile.log
Logging error to 'clone_error_logfile.log'.
The contents of type: '#AccountService.v1_3_0.AccountService' should be compatible with '#AccountService.v1_3_0.AccountService', on this system.
The contents of type: '#ManagerNetworkProtocol.v1_0_0.ManagerNetworkProtocol' should be compatible with '#ManagerNetworkProtocol.v1_0_0.ManagerNetworkProtocol', on this system.
The contents of type: '#EthernetInterface.v1_4_1.EthernetInterface' should be compatible with '#EthernetInterface.v1_4_1.EthernetInterface', on this system.
iLO response with code [400]: The value for the property is the correct type, but this value is incompatible with the current value of another property.
This machine may not have a reconfigurable MACAddress...Retrying without patching MACAddress.
The operation has been completed successfully.
The contents of type: '#EthernetInterface.v1_4_1.EthernetInterface' should be compatible with '#EthernetInterface.v1_4_1.EthernetInterface', on this system.
The operation completed successfully.
NIC Interface Disabled.
The contents of type: '#ComputerSystem.v1_4_0.ComputerSystem' should be compatible with '#ComputerSystem.v1_4_0.ComputerSystem', on this system.
The contents of type: '#SmartStorageConfig.v2_0_0.SmartStorageConfig' should be compatible with '#SmartStorageConfig.v2_0_0.SmartStorageConfig', on this system.
The contents of type: '#HpeiLOLicense.v2_1_1.HpeiLOLicense' should be compatible with '#HpeiLOLicense.v2_1_1.HpeiLOLicense', on this system.
Attempting to load a license key to the server.
The resource has been created successfully.
The type: '#HpeESKM.v2_0_0.HpeESKM' was not found on this system. Associated properties can not be applied...Skipping
Loading configuration...
Committing changes...
The property you are trying to change has been updated. Please check entry again before manipulating it.
The system is ready to be reset. Perform a reset now? (y/n)

Resetting iLO...

After iLO resets the session will be terminated.
Please wait for iLO to initialize completely before logging in again.
This process may take up to 3 minutes.

A management processor reset is in progress.
Sleeping 120 seconds for iLO reset...
Logging session out.
Discovering data...Done
Resetting System...
System already Powered Off: PowerOff
Loading of clonefile 'ilorest_clone.json' to server is complete. Review the changelog file 'changelog.log'.
</pre>

> To load a clone file with SSO and/or TLS certificates run the command with the `load` argument and include the `--tlscert` and/or `--ssocert` arguments followed by certificate files.

<pre>
iLOrest > login
Discovering data...Done
iLOrest > serverclone load <font color="#01a982"> --silent --tlscert sso_certificate.txt --ssocert certificate.txt</font>
This system has BIOS Version U32.
BIOS Versions are different. Suggest to have 'U30' in place before upgrading.
This system has has iLO 5 with firmware revision 1.40.
iLO Versions are compatible.
iLO Firmware Revisions are compatible.
Attempting Clone from a 'ProLiant DL380 Gen10' to a 'ProLiant DL360 Gen10'.
<font color="#01a982">Uploading SSO Certificate...
The operation completed successfully.
Uploading TLS Certificate...
The operation completed successfully.</font>
The contents of type: '#HpeServerBootSettings.v2_0_0.HpeServerBootSettings' should be compatible with '#HpeServerBootSettings.v2_0_0.HpeServerBootSettings', on this system.
The contents of type: '#SecureBoot.v1_0_0.SecureBoot' should be compatible with '#SecureBoot.v1_0_0.SecureBoot', on this system.
The contents of type: '#Manager.v1_3_3.Manager' should be compatible with '#Manager.v1_3_3.Manager', on this system.
The contents of type: '#Bios.v1_0_0.Bios' should be compatible with '#Bios.v1_0_0.Bios', on this system.
The contents of type: '#HpeiLOSSO.v2_0_0.HpeiLOSSO' should be compatible with '#HpeiLOSSO.v2_0_0.HpeiLOSSO', on this system.
The contents of type: '#HpeiLOSnmpService.v2_2_0.HpeiLOSnmpService' should be compatible with '#HpeiLOSnmpService.v2_2_0.HpeiLOSnmpService', on this system.
The contents of type: '#HpeiLOFederationGroup.v2_0_0.HpeiLOFederationGroup' should be compatible with '#HpeiLOFederationGroup.v2_0_0.HpeiLOFederationGroup', on this system.
...
</pre>

> An example of simultaneously deleting one account and adding another within a JSON file. For new accounts, the path is simply a placeholder, iLO will determine the URI to be used.

> Clone file snippet to be modified; the element to be removed is <font color="#01a982">highlighted</font>.

<pre>
{
  ...
  "#ManagerAccount.v1_1_3.ManagerAccount": {
    "/redfish/v1/AccountService/Accounts/1/": {
      "Privileges": {
        "HostNICConfigPriv": true,
        "HostStorageConfigPriv": true,
        "RemoteConsolePriv": true,
        "iLOConfigPriv": true,
        "VirtualMediaPriv": true,
        "UserConfigPriv": true,
        "HostBIOSConfigPriv": true,
        "VirtualPowerAndResetPriv": true,
        "LoginPriv": true,
        "SystemRecoveryConfigPriv": true
      },
      "Password": "password",
      "User_Name": "Administrator",
      "Login_Name": "Administrator",
      "AccountType": "User Account"
    },
	<font color="#01a982">
    "/redfish/v1/AccountService/Accounts/16/": {
      "Privileges": {
        "HostNICConfigPriv": true,
        "HostStorageConfigPriv": true,
        "RemoteConsolePriv": true,
        "iLOConfigPriv": true,
        "VirtualMediaPriv": true,
        "UserConfigPriv": true,
        "HostBIOSConfigPriv": true,
        "VirtualPowerAndResetPriv": true,
        "LoginPriv": true,
        "SystemRecoveryConfigPriv": false
      },
      "Password": "strongestavenger",
      "User_Name": "thor",
      "Login_Name": "Thor",
      "AccountType": "User Account"
    }
	</font>
  }
  ...
}
</pre>

> New version of clone file. The new element added is <font color="#01a982">highlighted</font>.

<pre>
{
  ...
  "#ManagerAccount.v1_1_3.ManagerAccount": {
    "/redfish/v1/AccountService/Accounts/1/": {
      "Privileges": {
        "HostNICConfigPriv": true,
        "HostStorageConfigPriv": true,
        "RemoteConsolePriv": true,
        "iLOConfigPriv": true,
        "VirtualMediaPriv": true,
        "UserConfigPriv": true,
        "HostBIOSConfigPriv": true,
        "VirtualPowerAndResetPriv": true,
        "LoginPriv": true,
        "SystemRecoveryConfigPriv": true
      },
      "Password": "password",
      "User_Name": "Administrator",
      "Login_Name": "Administrator",
      "AccountType": "User Account"
    }
	<font color="#01a982">
    "/redfish/v1/AccountService/Accounts/4/": {
      "Privileges": {
        "HostNICConfigPriv": true,
        "HostStorageConfigPriv": true,
        "RemoteConsolePriv": true,
        "iLOConfigPriv": true,
        "VirtualMediaPriv": true,
        "UserConfigPriv": true,
        "HostBIOSConfigPriv": true,
        "VirtualPowerAndResetPriv": true,
        "LoginPriv": true,
        "SystemRecoveryConfigPriv": false
      },
      "Password": "godofmischief",
      "User_Name": "loki",
      "Login_Name": "Loki",
      "AccountType": "User Account"
    }
	</font>
  }
  ...
}
</pre>


#### Syntax

serverclone [save/load] [OPTIONS]

#### Description

Creates a JSON formatted clone file (named ilorest_clone.json) of a system's iLO and bios configuration by default. You have the option to include Smart Storage Array configurations, as well as Single Sign-On and TLS certificates.
<aside class="notice">The JSON file might require some editing.</aside>

<aside class="notice">The default values are set for the iLO Management Account password and Federation Group key when the auto (automated mode) is used. </aside>

<aside class="notice">When loading a clone file, login using an iLO account with full administrative privileges (such as the Administrator account) to ensure all system parameters are cloned successfully.</aside>

<aside class="notice">When working with iLO Managment Accounts or iLO Federation Groups, remove entries from the JSON clone file (within the relevant dictionary) in order to perform deletion. In order to create new accounts on the server, simply add relevant nested dictionaries to the JSON file.</aside>

<aside class="notice">The Administrator account cannot be deleted using serverclone.</aside>

<aside class="notice">If settings for a particular type should not be changed, it is suggested to completely omit this dictionary from the JSON clone file.</aside>

#### Parameters

- **save**

Used to save a clone file.

- **load**

Used to load a clone file.

- **-h, --help**

Including the help flag will display help for the command.

- **--biospassword=BIOSPASSWORD**

Select this flag to input a BIOS password. Include this flag if second-level BIOS authentication is needed for the command to execute.

<aside class="notice">This option is only used on Gen 9 systems.</aside>

- **--encryption=ENCRYPTION**

Use this command optionally to encrypt/decrypt a file using the key provided.

- **--ssocert=SSOCERT**

Use this command during 'load' to include an SSO certificate. This should be properly formatted in a simple text file.

- **--tlscert=TLSCERT**

Use this command during 'load' to include a TLS certificate. This should be properly formatted in a simple text file.

- **-f CLONEFILENAME, --clonefile=CLONEFILENAME**

This is an optional command used to rename the default clone file 'ilorest_clone.json'.

- **--errarch=ARCHIVE, --archive=ARCHIVE**

Allow for save to automatically archive the clone file and error log file. Use with load will archive the clone file, temporary patch file, error log file and changelog file.

- **--uniqueitemoverride**

Use this command to override the measures stopping the tool from writing over items that are system unique.

- **--quiet**

This is an optional command used to keep the output text to the console to a minimum.

- **--ilossa**

This is an optional command used to include configuration of iLO Smart Array Devices during save or load processes.

- **--nobios**

This is an optional command used to remove Bios configuration  during save or load processes.

- **--logout=LOGOUT**

Use this command to logout.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

- **auto**

This optional command provides preset credentials, so that you are not prompted for credentials. The preset value of **<p/k>** is used as the password for the iLO account manager accounts and the iLO federation group keys. Warning and confirmation messages are suppressed.   

#### Inputs
None

#### Outputs
None

### Serverlogs command

> Serverlogs example commands:

> Select `AHS` to download AHS logs from a server to a file. The filename is pre-generated from the server serial number and date and time the AHS log was gathered.

<pre>
iLOrest > <font color="#01a982">serverlogs --selectlog=AHS</font>
</pre>

> To view logs select a log using the `--selectlog` option. You can output logs to a file with the `(-f, --filename)` option.

<pre>
iLOrest > serverlogs <font color="#01a982">--selectlog=IML</font>

@odata.type=#LogEntry.v1_0_0.LogEntry
Name=Integrated Management Log
Created=2019-02-02T22:02:40Z
@odata.id=/redfish/v1/Systems/1/LogServices/IML/Entries/1/
@odata.context=/redfish/v1/$metadata#LogEntry.LogEntry
Id=1
Oem=
     Hpe=
          @odata.type=#HpeLogEntry.v2_1_0.HpeLogEntry
          Count=1
          Updated=2019-02-02T22:02:40Z
          Code=1
          EventNumber=2054
          @odata.context=/redfish/v1/$metadata#HpeLogEntry.HpeLogEntry
          Class=33
          Categories=Maintenance
                      Administration
OemRecordFormat=Hpe-IML
Message=IML Cleared (iLO 5 user: admin)
EntryType=Oem
Severity=OK
</pre>

> To filter logs you can use the `--filter` option.

<pre>
iLOrest > serverlogs --selectlog=IML <font color="#01a982">--filter Id=1</font>

@odata.type=#LogEntry.v1_0_0.LogEntry
Name=Integrated Management Log
Created=2019-02-02T22:02:40Z
@odata.id=/redfish/v1/Systems/1/LogServices/IML/Entries/1/
@odata.context=/redfish/v1/$metadata#LogEntry.LogEntry
Id=1
Oem=
     Hpe=
          @odata.type=#HpeLogEntry.v2_1_0.HpeLogEntry
          Count=1
          Updated=2019-02-02T22:02:40Z
          Code=1
          EventNumber=2054
          @odata.context=/redfish/v1/$metadata#HpeLogEntry.HpeLogEntry
          Class=33
          Categories=Maintenance
                      Administration
OemRecordFormat=Hpe-IML
Message=IML Cleared (iLO 5 user: admin)
EntryType=Oem
Severity=OK
</pre>

> Use the `--customiseAHS` with a string to customize AHS results. This is only available for downloading remote AHS logs. This command will only download AHS logs from January 26th 2019 to February 1st 2019.

<pre>
serverlogs --selectlog=AHS <font color="#01a982">--customiseAHS "from=2019-01-26&&to=2019-02-01"</font>
</pre>

> Clear logs by selecting a log with `--selectlog` and including the `(-c, --clearlog)` option. This command will clear the AHS logs.

<pre>
iLOrest > serverlogs --selectlog=AHS <font color="#01a982">--clearlog</font>
One or more properties were changed and will not take effect until the device is reset and system is rebooted
</pre>

> To insert an IML log use the `(-m, --maintenancemessage)` flag. This is only available with IML logs.

<pre>
iLOrest > serverlogs --selectlog=IML <font color="#01a982">-m "Text message for maintenance"</font>
[201] The operation completed successfully.
</pre>

> To set an IML log as repaired use the `(-r, --repair)` option. Specify the Id of a log to mark as repaired. You can only repair entries with severities of `Critical` or `Warning`.

<pre>
iLOrest > serverlogs --selectlog=IML --filter Severity=Critical

@odata.type=#LogEntry.v1_0_0.LogEntry
Name=Integrated Management Log
Created=2019-02-02T22:08:32Z
@odata.id=/redfish/v1/Systems/1/LogServices/IML/Entries/3/
@odata.context=/redfish/v1/$metadata#LogEntry.LogEntry
Id=3
Oem=
     Hpe=
          @odata.type=#HpeLogEntry.v2_1_0.HpeLogEntry
          Count=2
          Updated=2019-02-02T22:10:05Z
          Code=1043
          EventNumber=2057
          @odata.context=/redfish/v1/$metadata#HpeLogEntry.HpeLogEntry
          RecommendedAction=Update the Innovation Engine Firmware.
          LearnMoreLink=http://www.hpe.com/support/class0x0032code0x0413-gen10
          Repaired=False
          Class=50
          Categories=Security
OemRecordFormat=Hpe-IML
Message=Innovation Engine Image Authentication Error. The Innovation Engine image could not be authenticated.
EntryType=Oem
Severity=Critical
iLOrest > serverlogs --selectlog=IML <font color="#01a982">-r 3</font>
The operation completed successfully.
iLOrest > serverlogs --selectlog=IML --filter Id=3

@odata.type=#LogEntry.v1_0_0.LogEntry
Name=Integrated Management Log
Created=2019-02-02T22:08:32Z
@odata.id=/redfish/v1/Systems/1/LogServices/IML/Entries/3/
@odata.context=/redfish/v1/$metadata#LogEntry.LogEntry
Id=3
Oem=
     Hpe=
          @odata.type=#HpeLogEntry.v2_1_0.HpeLogEntry
          Count=3
          Updated=2019-02-02T22:12:20Z
          Code=1043
          EventNumber=2057
          @odata.context=/redfish/v1/$metadata#HpeLogEntry.HpeLogEntry
          RecommendedAction=Update the Innovation Engine Firmware.
          LearnMoreLink=http://www.hpe.com/support/class0x0032code0x0413-gen10
          Repaired=True
          Class=50
          Categories=Security
OemRecordFormat=Hpe-IML
Message=Innovation Engine Image Authentication Error. The Innovation Engine image could not be authenticated.
EntryType=Oem
Severity=OK
</pre>

#### Syntax

serverlogs *--selectlog=[Log_Selection] [Optional Parameters]*

#### Description

Command for downloading and performing log operations.

<aside class="warning">You must use the default name when downloading AHS logs, the -f parameter is not supported.</aside>

#### Parameters

- **AHS**

Use this with the --selectlog option to perform operations on the AHS logs.

- **IEL**

Use this with the --selectlog option to perform operations on the IEL logs.

- **IML**

Use this with the --selectlog option to perform operations on the IML logs.

- **SA**

Use this with the --selectlog option to perfrom opertation on the Security logs.

- **-h, --help**

Including the help flag will display help for the command.

- **-f FILENAME, --filename=FILENAME**

Use this flag if you wish to use a different filename than the default one. The default filename is ilorest.json.

- **--filter=FILTER**

Optionally set a filter value and a filter attribute to filter logs.

- **-j, --json**

Optionally include this flag if you wish to change the displayed output to JSON format. Preserving the JSON data structure makes the information easier to parse.

- **--selectlog=SERVICE**

Read log from the given log service. Options: IML, IEL or AHS.


- **-c, --clearlog**

Clears the logs for the selected option.

- **--customiseAHS=CUSTOMISEAHS**

Allows customized AHS log data to be downloaded.

- **--downloadallahs**

Allows complete AHS log data to be downloaded.

- **--directorypath=DIRECTORYPATH**

Directory path for the ahs file.

- **-m MAINMES, --maintenancemessage=MAINMES**

Maintenance message to be inserted into the log. (IML LOGS ONLY FEATURE)

- **--mpfile=MPFILENAME**

Use the provided filename to obtain server information.

- **-o OUTDIRECTORY, --outputdirectory=OUTDIRECTORY**

Use the provided directory to output data for multiple server downloads.

- **--mplog=MPLOG**

Used to indicate the logs to be downloaded on multiple servers. Allowable values: IEL, IML, AHS, all or combination of any two.

- **-r REPIML, --repair=REPIML**

Repair the IML log with the given ID.

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. Using this flag when not logged in will have no effect.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

#### Inputs
None


#### Outputs
None

### Serverstate command

> Serverstate example commands:

> To return the serverstate run the command without arguments. Possible values include: None, Unknown, Reset, PowerOff, InPost, InPostDiscoveryComplete, FinishedPost.

<pre>
iLOrest > <font color="#01a982">serverstate</font>
The server is currently in state: FinishedPost
</pre>



#### Syntax

serverstate *[Optional Parameter]*

#### Description

Returns the current state of the server.

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

#### Inputs

None

#### Outputs

None


### Sigrecompute command

> Sigrecompute  example commands:

> To Recalculate the signature on the systems configuration run the command without arguments.

<pre>
iLOrest > <font color="#01a982">sigrecompute</font>
The operation completed successfully.
</pre>



#### Syntax

sigrecompute *[OPTIONS]*

#### Description
Recalculate the signature on the systems configuration.

<aside class="notice">
The sigrecompute command is not available on Redfish systems.
</aside>


#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

#### Inputs
None

#### Outputs
None

### Singlesignon command

> Singlesignon  example commands:

> To delete a specific SSO record by running the command with the `deleterecord` argument and specify it by number.

<pre>
iLOrest > <font color="#01a982">singlesignon deleterecord 1</font>
The operation completed successfully.
</pre>

> To delete a specific SSO record by running the command with the `deleterecord` argument followed by the `all` keyword.

<pre>
iLOrest > <font color="#01a982">singlesignon deleterecord all</font>
The operation completed successfully.
</pre>

> To import a SSO DNS name run the command with the `dnsname` argument followed by the DNS to import.

<pre>
iLOrest > <font color="#01a982">singlesignon importdns dnsname</font>
The operation completed successfully.
</pre>

> To import a SSO certificate from a file run the command with the `importcert` argument followed by the certificate file to import. You can also import the certificate by URI, by specifying a URI path to the certificate instead.

<pre>
iLOrest > <font color="#01a982">singlesignon importcert certfile.txt</font>
The operation completed successfully.
</pre>



#### Syntax

Singlesignon *[OPTIONS]*

#### Description

Command for all single sign on available actions.



#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

#### Inputs
None

#### Outputs
None

### Virtualmedia command

> Virtualmedia  example commands:

> To view current virtual media run the command without arguments.

<pre>
iLOrest > <font color="#01a982">virtualmedia</font>
Available Virtual Media Options:
[1] Media Types Available: Floppy USBStick  Image Inserted: None
[2] Media Types Available: CD DVD  Image Inserted: None
</pre>

> To insert virtual media specify the type of virtual media by Id number followed by the URI location to the image. You can specify the media to boot next reset by including the `--bootnextreset` option.

<pre>
iLOrest > <font color="#01a982">virtualmedia 2 http://xx.xx.xx.xx/path/to/vm.iso --bootnextreset</font>
The operation completed successfully.
iLOrest > virtualmedia
Available Virtual Media Options:
[1] Media Types Available: Floppy USBStick  Image Inserted: None
[2] Media Types Available: CD DVD  Image Inserted: http://xx.xx.xx.xx/path/to/vm.iso
</pre>  

> To remove an inserted media specify the type of virtual media by Id number and include the `--remove` option.

<pre>
iLOrest > <font color="#01a982">virtualmedia 2 --remove</font>
The operation completed successfully.
iLOrest > virtualmedia
Available Virtual Media Options:
[1] Media Types Available: Floppy USBStick  Image Inserted: None
[2] Media Types Available: CD DVD  Image Inserted: None
</pre>



#### Syntax

virtualmedia *[ID] [URI] [OPTIONS]*

#### Description

Command for inserting and removing virtual media.

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

- **--reboot=REBOOT**

Use this flag to perform a reboot command function after completion of operations.  For help with parameters and descriptions regarding the reboot flag, run help reboot.

- **--remove**

Use this flag to remove the media from the selection.

- **--bootnextreset**

Use this flag if you wish to boot from the image on next server reboot.

#### Login Parameters

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, use this flag along with the password and URL flags to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect
securely to the system in remote mode. This flag has no effect in local mode.

<aside class="notice">
The image will be ejected automatically on the second server reboot so that the server does not boot to the image twice.
</aside>

#### Inputs
None

#### Outputs
None
