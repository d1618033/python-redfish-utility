## Global Options

This section lists all global options available.

**-h, --help**

Including the help flag will display general help for the tool.

**-c, --config=CONFIGFILE**

Use the provided configuration file instead of the default.

**--cache-dir=CACHEPATH**

Use the provided directory as the location to cache data instead of the default.

**-v, --verbose**

Display verbose information.

**-d, --debug**

Display debug information.

**--logdir=LOGPATH**

Use the provided directory as the location for the log file instead of the default.

**--nocache**

During execution the application will temporarily store data only in memory.

**--nologo**

Include to block copyright and logo.

**--notoolbar**

Include to block bottom status bar.

**--proxy=PROXYURL**

Use the provided proxy for communication.

**--redfish**

Use this flag if you wish to enable Redfish only compliance. It is enabled by default in systems with iLO 5 and above.

<aside class="notice">The --redfish global option is not required for iLO 5.</aside>

**--latestschema**

Optionally use the latest schema instead of the one requested by the file. 

<aside class="notice">
Might cause errors in some data retrieval due to difference in schema versions.
</aside>

## Global commands

This section includes commands as well as their usage and examples of general commands in the RESTful Interface Tool. They include commands used to do things such as listing help for using commands, viewing, retrieving, modifying, and committing changes to server properties, and authenticating and logging in and out of the server.

### Help Command

> Help example commands:

> Entering help will list the global options and all available commands for iLOREST.

<pre>
iLOrest > <font color="#01a982">help</font>
Usage: iLOrest [GLOBAL OPTIONS] [COMMAND] [ARGUMENTS] [COMMAND OPTIONS]

Options:
  -h, --help            Show this help message and exit.
  -c FILE, --config=FILE
                        Use the provided configuration file instead of the
                        default one.
  --cache-dir=PATH      Use the provided directory as the location to cache
                        data (default location:
                        C:\Users\kocurema\AppData\Roaming\.iLOrest)

  GLOBAL OPTIONS:
    -v, --verbose       Display verbose information.
    -d, --debug         Display debug information.
    --logdir=PATH       Use the provided directory as the location for log
                        file.
    --nocache           During execution the application will temporarily
                        store data only in memory.
    --nologo            Include to block copyright and logo.
	--notoolbar         Include to block bottom status bar.
    --redfish           Use this flag if you wish to to enable Redfish only
                        compliance. It is enabled by default in systems with
                        iLO5 and above.
    --latestschema      Optionally use the latest schema instead of the one
                        requested by the file. Note: May cause errors in some
                        data retreval due to difference in schema versions.
    --proxy=URL         Use the provided proxy for communication.

BIOS COMMANDS
  biosdefaults                 - Set the currently logged in server to default
                                  BIOS settings.
  bootorder                    - Displays and sets the current boot order.
  iscsiconfig                  - Displays and configures the current iscsi
                                  settings.
  pending                      - Show the pending changes that will be applied
                                  on reboot.
  results                      - Show the results of changes which require a
                                  server reboot.
  setpassword                  - Sets the admin password and poweron password

COMMANDS
  commit                       - Applies all the changes made during the
                                  current session.
  get                          - Displays the current value(s) of a
                                  property(ies) within a selected type.
  info                         - Displays detailed information about a
                                  property within a selected type.
  list                         - Displays the current value(s) of a
                                  property(ies) within a selected type
                                  including reserved properties.
  load                         - Loads the server configuration settings from
                                  a file.
  login                        - Connects to a server, establishes a secure
                                  session, and discovers data from iLO.
  logout                       - Ends the current session and disconnects from
                                  the server.
  save                         - Saves the selected type's settings to a file.
  select                       - Selects the object type to be used.
  set                          - Changes the value of a property within the
                                  currently selected type.
  status                       - Displays all pending changes within a
                                  selected type that need to be committed.
  types                        - Displays all selectable types within the
                                  currently logged in server.
  exit                         - Exits from the interactive shell.
  help                         - Displays command line syntax and help menus
                                  for individual commands. Example: help login

RAW COMMANDS
  rawdelete                    - Raw form of the DELETE command.
  rawget                       - Raw form of the GET command.
  rawhead                      - Raw form of the HEAD command.
  rawpatch                     - Raw form of the PATCH command.
  rawpost                      - Raw form of the POST command.
  rawput                       - Raw form of the PUT command.

SMART ARRAY COMMANDS
  clearcontrollerconfig        - Clears smart array controller configuration.
  createlogicaldrive           - Creates a new logical drive on the selected
                                  controller.
  deletelogicaldrive           - Deletes logical drives from the selected
                                  controller.
  drivesanitize                - Erase/Sanitizes physical drives
  factoryresetcontroller       - Factory resets a controller by index or
                                  location.
  smartarray                   - Discovers all storage controllers installed
                                  in the server and managed by the
                                  SmartStorage.

iLO COMMANDS
  certificate                  - Command for importing both iLO and login
                                  authorization certificates as well as
                                  generating iLO certificate signing requests
  clearrestapistate            - Clears the persistent state of the REST API.
                                  Some portions of the API may not be available
                                  until after the server reboots.
  directory                    - Update directory settings, add/delete
                                  directory roles, and test directory settings.
  disableilofunctionality      - disables iLO's accessibility via the network
                                  and resets iLO. WARNING: This should be used
                                  with caution as it will render iLO unable to
                                  respond to further network operations
                                  (including REST operations) until iLO is
                                  re-enabled using the RBSU menu.
  eskm                         - Command for all ESKM available actions.
  factorydefaults              - Resets iLO to factory defaults. WARNING: user
                                  data will be removed use with caution.
  fwintegritycheck             - Perform a firmware integrity check on the
                                  currently logged in server.
  firmwareupdate               - Perform a firmware update on the currently
                                  logged in server.
  iloaccounts                  - Adds / deletes an iLO account on the
                                  currently logged in server.
  backuprestore                - Backup and restore iLO to a server using a
                                  .bak file.
  iloclone                     - Clone the iLO config of the currently logged
                                  in server and copy it to the server in the
                                  arguments.
  ilofederation                - Adds / deletes an iLO federation group on the
                                  currently logged in server.
  ilolicense                   - Adds an iLO license key to the currently
                                  logged in server.
  iloreset                     - Reset iLO on the current logged in server.
  ipprofiles                   - This is used to manage hpeipprofile data
                                  store.
  onebuttonerase               - Performs One Button Erase on a system .
  reboot                       - Reboot operations for the current logged in
                                  server.
  sendtest                     - Command for sending various tests to iLO.
  serverclone                  - Creates a JSON formated clone file of a
                                  system's iLO, BIOS, and SSA configuration
                                  which can be duplicated onto other systems.
                                  User editable JSON file can be manipulated to
                                  modify settings before being loaded onto
                                  another machine.
  serverinfo                   - Shows aggregate health status and details of
                                  the currently logged in server.
  serverlogs                   - Download and perform log operations.
  serverstate                  - Returns the current state of the server.
  sigrecompute                 - Command to recalculate the signature of the
                                  computer's configuration.
  singlesignon                 - Command for all single sign on available
                                  actions.
  virtualmedia                 - Command for inserting and removing virtual
                                  media.

iLO REPOSITORY COMMANDS
  deletecomp                   - Deletes components/binaries from the iLO
                                  Repository.
  downloadcomp                 - Downloads components/binaries from the iLO
                                  Repository.
  flashfwpkg                   - Flashes fwpkg components using the iLO
                                  repository.
  installset                   - Manages install sets for iLO.
  listcomp                     - Lists components/binaries from the iLO
                                  Repository.
  maintenancewindow            - Manages the maintenance windows for iLO.
  makeinstallset               - Creates install sets for iLO.
  taskqueue                    - Manages the update task queue for iLO.
  uploadcomp                   - Upload components/binary to the iLO
                                  Repository.
</pre>

> Providing a specific command will list help regarding that specific command.

<pre>
iLOrest > <font color="#01a982">help login</font>
Usage: login [URL] [OPTIONS]

        To login remotely run using iLO url and iLO credentials
        example: login <iLO url/hostname> -u <iLO username> -p <iLO password>

        To login on a local server run without arguments
        example: login

Options:
  -h, --help            show this help message and exit
  -u USER, --user=USER  If you are not logged in yet, including this flag
                        along with the password and URL flags can be used to
                        log into a server in the same command.
  -p PASSWORD, --password=PASSWORD
                        Use the provided iLO password to log in.
  --includelogs         Optionally include logs in the data retrieval process.
  --selector=SELECTOR   Optionally include this flag to select a type to run
                        the current command on. Use this flag when you wish to
                        select a type without entering another command, or if
                        you wish to work with a type that is different from
                        the one you currently have selected.
  --path=PATH           Optionally set a starting point for data collection
                        during login. If you do not specify a starting point,
                        the default path will be /redfish/v1/. Note: The path
                        flag can only be specified at the time of login.
                        Warning: Only for advanced users, and generally not
                        needed for normal operations.
  --biospassword=BIOSPASSWORD
                        Select this flag to input a BIOS password. Include
                        this flag if second-level BIOS authentication is
                        needed for the command to execute. This option is only
                        used on Gen 9 systems.
</pre>

> The alternate syntax to list details regarding a command is **-h**.

<pre>
iLOrest > <font color="#01a982">login -h</font>
Usage: login [URL] [OPTIONS]

        To login remotely run using iLO url and iLO credentials
        example: login <iLO url/hostname> -u <iLO username> -p <iLO password>

        To login on a local server run without arguments
        example: login

Options:
  -h, --help            show this help message and exit
  -u USER, --user=USER  If you are not logged in yet, including this flag
                        along with the password and URL flags can be used to
                        log into a server in the same command.
  -p PASSWORD, --password=PASSWORD
                        Use the provided iLO password to log in.
  --includelogs         Optionally include logs in the data retrieval process.
  --selector=SELECTOR   Optionally include this flag to select a type to run
                        the current command on. Use this flag when you wish to
                        select a type without entering another command, or if
                        you wish to work with a type that is different from
                        the one you currently have selected.
  --path=PATH           Optionally set a starting point for data collection
                        during login. If you do not specify a starting point,
                        the default path will be /redfish/v1/. Note: The path
                        flag can only be specified at the time of login.
                        Warning: Only for advanced users, and generally not
                        needed for normal operations.
  --biospassword=BIOSPASSWORD
                        Select this flag to input a BIOS password. Include
                        this flag if second-level BIOS authentication is
                        needed for the command to execute. This option is only
                        used on Gen 9 systems.
</pre>


#### Syntax

help *[command] [optional parameters]*

#### Description

Displays command-line syntax and help menus for individual commands. Use this command if you want to know more about a command or need help using a command. Alternatively, you can use the `help` command without specifying a particular command if you wish to see all the available commands and options.

#### Parameters

- Command 

Supplying a command to help will display the help message corresponding to the given command, as well as the options relating to that particular command.

<aside class="notice">If no command is provided, the help command will list and provide a brief description of all available commands.</aside>

- **-h, --help**

Running the `help` command with the **–h** or **–help** command will display information on how to use the `help` command.

- **-c FILE, --config=FILE**

Use the provided configuration file instead of the default one.

- **--cache-dir=PATH**

Use the provided directory as the location to cache data (default location: `C:\Users\USERNAME\AppData\Roaming\.ilorest`).

#### Inputs

None

#### Outputs

None

### Login command

> Login example commands:

> To login remotely, supply the URL, username, and password for the server. 


<pre>
iLOrest > <font color="#01a982">login xx.xx.xx.xx -u username -p password</font>
Discovering data...Done
</pre>

> Here the selector option has been included so that the `Bios` type is selected once the user is logged in. You can prove that the `Bios` type has indeed been selected when we enter the select command.

<pre>
iLOrest > login xx.xx.xx.xx -u username -p password <font color="#01a982">--select Bios.</font>
Discovering data...Done
iLOrest > select
Current selection: Bios.v1_0_0
</pre>

> An IPv4, IPv6, or hostname can be specified. IPv6 should use the following format.

<pre>
iLOrest > <font color="#01a982">login [xxxx::xxxx:xxxx:xxxx:xxxx] -u username -p password</font>
Discovering data...Done
</pre>

> Here a SSL certificate was included so iLOrest validates the HTTPS connection

<pre>
iLOrest > login system.domain.net -u username -p password <font color="#01a982">--https \path\to\SSLcert.crt</font>
Discovering data...Done
</pre>

> Here the URL, username, and password information are not specified here or in the configuration file, and the server was logged in to locally.

<pre>
iLOrest > <font color="#01a982">login</font>
Discovering data...Done
</pre>

#### Syntax

login *[URL] [User] [Password] [Optional Parameters]*

#### Description

Connects to a server, establishes a secure session, and discovers data from iLO. If you are logging in to a local server, run the command without arguments. If you are not logging in to a local server, supply the URL argument along with the user and password options.

#### Usage in Other Commands

Login remotely as part of other commands by including the *--url*, *(-u, --user)*, and *(-p, --password)* flags. Optionally include the *--https* flag to validate the SSL certificate when logging in. Locally you will be logged in automatically unless running in higher security modes (see [Higher Security Modes](#higher-security-modes)).

#### Parameters

- **URL**

Connect to the server located at the provided URL.

- **-h, --help**

Including the help flag will display help for the command.

- **-u User**

Connect to the server as the provided user.

- **-p Password**

Connect to the server with the password corresponding to the given user.

- **--https**

Use the provided CA bundle or SSL certificate with your login to connect 
securely to the system in remote mode. This flag has no effect in local mode.

- **--includelogs**

Optionally choose to set the **includelogs** flag. Doing so will include logs in the data retrieval process.

<aside class="notice">Use this option to limit long login times.</aside>

- **--selector=SELECTOR**

Optionally including the **selector** flag allows you to select a type to run while running the current command. Use this flag when you wish to select a type without entering another command, or if you wish to work with a type that is different from the one you currently have selected.

- **--path=PATH**

Optionally set a starting point for data collection. If you do not specify a starting point, the default path will be /rest/v1.

<aside class="notice">The <b>path</b> flag can only be specified at the time of login, so if you are already logged into the server, the <b>path</b> flag will not change the path. If you are entering a command that isn’t the <b>login</b> command, but includes your login information, you can still specify the path flag there.</aside>

- **--biospassword=BIOSPASSWORD**

Select this flag to input a BIOS password. Include this flag if second-level BIOS authentication is needed for the command to execute.

<aside class="notice">This option is only used on Gen 9 systems.</aside>

### Types command

> Types example commands:

> This command will list all the available types that you can select. The full list has been truncated for space.

<pre>
iLOrest > login xx.xx.xx.xx -u username -p password
Discovering data...Done
iLOrest > <font color="#01a982">types</font>
Type options:
AccountService.v1_3_0
Bios.v1_0_0
CertificateCollection
Chassis.v1_6_0
ChassisCollection
ComputerSystem.v1_4_0
ComputerSystemCollection
EthernetInterface.v1_4_1
EthernetInterfaceCollection
EventDestinationCollection
EventService.v1_0_8
HostInterface.v1_1_1
HostInterfaceCollection
HpeBaseConfigs.v2_0_0
HpeBaseNetworkAdapter.v2_0_0
HpeBaseNetworkAdapterCollection
HpeBiosMapping.v2_0_0
HpeCertAuth.v1_1_0
HpeCertificate.v1_0_0
HpeCertificateCollection
HpeComponent.v1_0_1
HpeComponentCollection
HpeComponentInstallSet.v1_0_3
HpeComponentInstallSetCollection
HpeComponentUpdateTaskQueueCollection
HpeDirectoryTest.v1_0_0
HpeESKM.v2_0_0
...
</pre>

> This command simultaneously logs in to the server at the provided URL with the provided username and password, and list all the available types that you can select. The full list has been truncated here for space.

<pre>
iLOrest > <font color="#01a982">types --url xx.xx.xx.xx -u username -p password</font>
Discovering data...Done
Type options:
AccountService.v1_3_0
Bios.v1_0_0
CertificateCollection
Chassis.v1_6_0
ChassisCollection
ComputerSystem.v1_4_0
ComputerSystemCollection
EthernetInterface.v1_4_1
EthernetInterfaceCollection
EventDestinationCollection
EventService.v1_0_8
HostInterface.v1_1_1
HostInterfaceCollection
HpeBaseConfigs.v2_0_0
HpeBaseNetworkAdapter.v2_0_0
HpeBaseNetworkAdapterCollection
HpeBiosMapping.v2_0_0
HpeCertAuth.v1_1_0
HpeCertificate.v1_0_0
HpeCertificateCollection
HpeComponent.v1_0_1
HpeComponentCollection
HpeComponentInstallSet.v1_0_3
HpeComponentInstallSetCollection
HpeComponentUpdateTaskQueueCollection
HpeDirectoryTest.v1_0_0
HpeESKM.v2_0_0
...
</pre>

> Adding the `fulltypes` option will return the full type name instead of the default simplified versions. This is only available on Redfish systems.

<pre>
iLOrest > <font color="#01a982">types --fulltypes</font>
Type options:
#AccountService.v1_3_0.AccountService
#Bios.v1_0_0.Bios
#CertificateCollection.CertificateCollection
#Chassis.v1_6_0.Chassis
#ChassisCollection.ChassisCollection
#ComputerSystem.v1_4_0.ComputerSystem
#ComputerSystemCollection.ComputerSystemCollection
#EthernetInterface.v1_4_1.EthernetInterface
#EthernetInterfaceCollection.EthernetInterfaceCollection
#EventDestinationCollection.EventDestinationCollection
#EventService.v1_0_8.EventService
#HostInterface.v1_1_1.HostInterface
#HostInterfaceCollection.HostInterfaceCollection
#HpeBaseConfigs.v2_0_0.HpeBaseConfigs
#HpeBaseNetworkAdapter.v2_0_0.HpeBaseNetworkAdapter
#HpeBaseNetworkAdapterCollection.HpeBaseNetworkAdapterCollection
#HpeBiosMapping.v2_0_0.HpeBiosMapping
#HpeCertAuth.v1_1_0.HpeCertAuth
#HpeCertificate.v1_0_0.HpeCertificate
#HpeCertificateCollection.HpeCertificateCollection
#HpeComponent.v1_0_1.HpeComponent
#HpeComponentCollection.HpeComponentCollection
#HpeComponentInstallSet.v1_0_3.HpeComponentInstallSet
#HpeComponentInstallSetCollection.HpeComponentInstallSetCollection
#HpeComponentUpdateTaskQueueCollection.HpeComponentUpdateTaskQueueCollection
#HpeDirectoryTest.v1_0_0.HpeDirectoryTest
#HpeESKM.v2_0_0.HpeESKM
...
</pre>



#### Syntax

types *[Optional Parameters]*

#### Description

The `types` command displays all selectable types available within the currently logged in server. Types include a name as well as version information. Types represent the schema used for the resource and indicate the version of the schema. Version information is `major.minor.errata` (for example: `SystemRoot.0.9.5`). Major versions are not backwards compatible, but everything else is.

<aside class="notice">See the iLO RESTful API Data Model Reference at <a href=" https://hewlettpackard.github.io/ilo-rest-api-docs/ilo5/#resource-definitions">https://hewlettpackard.github.io/ilo-rest-api-docs/</a> for a list and description of all the possible types.</aside>

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

- **--fulltypes**

Optionally include this flag if you would prefer to return the full type name instead of the simplified versions.

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

Optionally choose to set the **includelogs** flag. Doing so will include logs in the data retrieval process.

<aside class="notice">Use this option to limit long login times.</aside>

- **--path=PATH**

Optionally set a starting point for data collection. If you do not specify a starting point, the default path will be` /redfish/v1/`. (see [Path Option](#path-option) for more information).

<aside class="notice">The <b>path</b> flag can only be specified at the time of login, so if you are already logged into the server, the <b>path</b> flag will not change the path. If you are entering a command that isn’t the <b>login</b> command, but includes your login information, you can still specify the path flag there.</aside>

#### Inputs

None

#### Outputs

None

### Select command

> Select example commands:

> This command simultaneously logs in to the server at the provided URL (--url) with the provided username (-u) and password (-p), and selects the `ComputerSystem.` type.

<aside class="notice">
Adding a period after the selected type will ensure the selection is limited to one type. For example, selecting **Bios** will select both **Bios.v1_0_0** and **HpeBiosMapping.v2_0_0**. Selecting **Bios.** will only select the **Bios.v1_0_0** type.
</aside>

<aside class="notice">
Supplying the type version is not required. The selection **Bios.** and **Bios.v1_0_0** are identical.
</aside>

<pre>
iLOrest > <font color="#01a982">select ComputerSystem. --url xx.xx.xx.xx -u username -p password</font>
Discovering data...Done
iLOrest > select
Current selection: ComputerSystem.v1_4_0
</pre>

> Running the select command with no argument will return the current selection.

<pre>
iLOrest > <font color="#01a982">select</font>
Error: No type currently selected. Please use the 'types' command to
get a list of types, or pass your type by using the '--selector' flag.
iLOrest > select Bios.
iLOrest > <font color="#01a982">select</font>
Current selection: Bios.v1_0_0
</pre>

> Adding a period after the type selected, `Bios`, limits the selection, preventing accidentally also selecting anything else starting with `Bios`. This also removes the need to include the version.

<pre>
iLOrest > select Bios
iLOrest > select
Current selection: HpeBiosMapping.v2_0_0, Bios.v1_0_0
iLOrest > <font color="#01a982">select Bios.</font>
iLOrest > select
Current selection: Bios.v1_0_0
</pre>

> iLOrest caches data once a type has been selected for the first time. To refresh a type with the most up to date information use the `--refresh` option.

<pre>
iLOrest > select ComputerSystem.
iLOrest > get Oem/Hpe/PowerOnMinutes
Oem=
     Hpe=
          PowerOnMinutes=814088
iLOrest > <font color="#01a982">select ComputerSystem. --refresh</font>
iLOrest > get Oem/Hpe/PowerOnMinutes
Oem=
     Hpe=
          PowerOnMinutes=814089
</pre>



#### Syntax

select *[Type] [Optional Parameters]*

#### Description

Use `select` to choose a specific type to work with. Eligible types for selection are those listed by the types command. Because commands are entered individually in the RESTful Interface Tool, working with specific types requires that you highlight or select the particular type you are working with. Use the `select` command to highlight a type so that you can work with it.

#### Usage in Other Commands

Select a type from another command by including the *(--select, --selector)* option flag followed by the type to select. Not all commands have the `select` flag, run help on the command to see available options.

#### Parameters

- **Type**

Specify the type you want to select. Omitting a type to select will cause select to display the currently selected type.

- **-h, --help**

Including the help flag will display help for the command.

- **--biospassword=BIOSPASSWORD**

Select this flag to input a BIOS password. Include this flag if second-level BIOS authentication is needed for the command to execute.

<aside class="notice">This option is only used on Gen 9 systems.</aside>

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

Optionally choose to set the **includelogs** flag. Doing so will include logs in the data retrieval process.

<aside class="notice">Use this option to limit long login times.</aside>

- **--path=PATH**

Optionally set a starting point for data collection. If you do not specify a starting point, the default path will be` /redfish/v1/`. (see [Path Option](#path-option) for more information).

<aside class="notice">The <b>path</b> flag can only be specified at the time of login, so if you are already logged into the server, the <b>path</b> flag will not change the path. If you are entering a command that isn’t the <b>login</b> command, but includes your login information, you can still specify the path flag there.</aside>

#### Inputs

None

#### Outputs

None

### List command

<aside class="notice">arguments are not case-sensitive.</aside>

> List command examples:

> With a Type selected, run the command without arguments to list all properties within the selected type, including reserved properties. The full list has been truncated here for space.

<pre>
iLOrest > select Bios.
iLOrest > <font color="#01a982">list</font>
@odata.context=/redfish/v1/$metadata#Bios.Bios
@odata.etag=W/"02E13BA89B606F6F6F02950EB3CA676D"
@odata.id=/redfish/v1/systems/1/bios/settings/
@odata.type=#Bios.v1_0_0.Bios
AcpiHpet=Enabled
AcpiRootBridgePxm=Enabled
AcpiSlit=Enabled
AdjSecPrefetch=Enabled
AdminEmail=""
AdminName=""
AdminOtherInfo=""
AdminPhone=""
AdvCrashDumpMode=Disabled
AdvancedMemProtection=AdvancedEcc
AsrStatus=Enabled
AsrTimeoutMinutes=Timeout10
AssetTagProtection=Unlocked
AttributeRegistry=BiosAttributeRegistryU32.v1_2_10
AutoPowerOn=RestoreLastState
BootMode=Uefi
...
</pre>

> Including the `-j`,`--json` option preserves the JSON structure of the type’s information. The full list has been truncated here for space.

<pre>
iLOrest > select ComputerSystem.
iLOrest > <font color="#01a982">list --json</font>
{
  "@odata.context": "/redfish/v1/$metadata#ComputerSystem.ComputerSystem",
  "@odata.etag": "W/\"9D48B4B7\"",
  "@odata.id": "/redfish/v1/Systems/1/",
  "@odata.type": "#ComputerSystem.v1_4_0.ComputerSystem",
  "Actions": {
    "#ComputerSystem.Reset": {
      "ResetType@Redfish.AllowableValues": [
        "On",
        "ForceOff",
        "ForceRestart",
        "Nmi",
        "PushPowerButton"
      ],
      "target": "/redfish/v1/Systems/1/Actions/ComputerSystem.Reset/"
    }
  },
  "AssetTag": "",
  "Bios": {
    "@odata.id": "/redfish/v1/systems/1/bios/"
  },
  "BiosVersion": "U32 v2.10 (12/14/2018)",
  "Boot": {
    "BootSourceOverrideTarget": "None",
    "BootSourceOverrideTarget@Redfish.AllowableValues": [
      "None",
      "Cd",
      "Hdd",
...
</pre>

> To return specific properties or sub-properties include them as arguments. If the property you want to return is a sub-property add them in the form `Property/Sub-property`.

<pre>
iLOrest > <font color="#01a982">list @odata.id Boot/BootSourceOverrideMode AssetTag</font>
@odata.id=/redfish/v1/Systems/1/
AssetTag=""
Boot=
      BootSourceOverrideMode=UEFI
</pre>



#### Syntax

list *[Property(s)] [Optional Parameters]*

#### Description

Displays the current values of the properties of a selected type including reserved properties in human-readable and optionally JSON formats. Optionally include arguments to only return the values of those properties.

<aside class="notice">The list command does display reserved properties for types, while the get command does not.</aside>

#### Parameters

- **Property(s)**

Supplying a property or multiple properties will cause list to display the current value for that particular property or properties. Otherwise, if you wish to retrieve all the properties, run without arguments. Use this command only after a type has already been selected. If the value you are looking up is not available, it will return with no contents found for that property entry.

- **-h, --help**

Including the help flag will display help for the command.

- **--filter [FILTER_ATTRIBUTE=FILTER_VALUE]**

Optionally set a filter value for a filter attribute. This uses the provided filter for the currently selected type. (see [Filter Option](#filter-option) for more information).

<aside class="notice"> Use this flag to narrow down your results. For example, selecting a common type might return multiple objects that are all of that type. If you want to modify the properties of only one of those objects, use the filter flag to narrow down results based on properties.</aside>

- **---j, --json**

Optionally include this flag if you wish to change the displayed output to JSON format. Preserving the JSON data structure can make the information easier to parse.

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. You need to be logged in to use this flag.

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

Optionally choose to set the **includelogs** flag. Doing so will include logs in the data retrieval process.

<aside class="notice">Use this option to limit long login times.</aside>

- **--path=PATH**

Optionally set a starting point for data collection. If you do not specify a starting point, the default path will be` /redfish/v1/`. (see [Path Option](#path-option) for more information).

<aside class="notice">The <b>path</b> flag can only be specified at the time of login, so if you are already logged into the server, the <b>path</b> flag will not change the path. If you are entering a command that isn’t the <b>login</b> command, but includes your login information, you can still specify the path flag there.</aside>

#### Inputs

None

#### Outputs

None

### Info Command

> Info command examples:

> Omitting a property when using the info command causes info to list all available options, given that you have already selected a type. The full list has been truncated for space.

<pre>
iLOrest > select Bios.
iLOrest > <font color="#01a982">info</font>
Info options:
AcpiHpet
AcpiRootBridgePxm
AcpiSlit
AdjSecPrefetch
AdminEmail
AdminName
AdminOtherInfo
AdminPhone
</pre>

> This command simultaneously logs in to the server at the provided URL (--url) with the provided username (-u) and password (-p), selects the `Power.` type, and displays the `PowerSupplies` information.

<pre>
iLOrest > <font color="#01a982">info PowerSupplies -u username -p password --url xx.xx.xx.xx --select Power.</font>
Discovering data...Done

NAME
    PowerSupplies


DESCRIPTION
    Details of the power supplies associated with this system or
    device


TYPE
    array


READ-ONLY
    True


SUB-PROPERTIES
    Redundancy, Name, SerialNumber, MemberId, @odata.id,
    PowerCapacityWatts, Model, PartNumber, Status,
    LastPowerOutputWatts, SparePartNumber, RelatedItem,
    LineInputVoltageType, Oem, PowerSupplyType, LineInputVoltage,
    FirmwareVersion, Manufacturer
</pre>

> Multiple properties under the VirtualMedia type are specified. By passing multiple properties, it returns the information on all of the properties passed.

<pre>
iLOrest > select VirtualMedia.
iLOrest > <font color="#01a982">info Image WriteProtected</font>

NAME
    Image


DESCRIPTION
    The valid URI indicating the image that is mounted on this server.
    A null value indicates that no image exists.


TYPE
    string
    null


READ-ONLY
    False


**************************************************

NAME
    WriteProtected


DESCRIPTION
    Indicates whether the virtual media is protected against write
    operations.


TYPE
    boolean
    null


READ-ONLY
    False


POSSIBLE VALUES
    True or False
</pre>

> Any Sub-Properties shown in an info response can be queried in the same form as set, list, and get: `Property/Sub-property`.

<pre>
iLOrest > select ComputerSystem.
iLOrest > info Boot

NAME
    Boot


DESCRIPTION
    The boot information for the current resource.


TYPE
    object


READ-ONLY
    False


SUB-PROPERTIES
    BootSourceOverrideTarget,
    BootSourceOverrideTarget@Redfish.AllowableValues,
    BootSourceOverrideEnabled, BootSourceOverrideMode,
    UefiTargetBootSourceOverride@Redfish.AllowableValues,
    UefiTargetBootSourceOverride
iLOrest > <font color="#01a982">info Boot/BootSourceOverrideTarget</font>

NAME
    BootSourceOverrideTarget


DESCRIPTION
    The current boot source to be used at next boot instead of the
    normal boot device, if BootSourceOverrideEnabled is true.


TYPE
    string
    null


READ-ONLY
    False
</pre>



#### Syntax

info *[Property(s)] [Optional Parameters]*

#### Description

Displays detailed information about a property within a selected type. Information displayed includes the data type of the value, if the property is read-only or not, a brief description, possible values, and any sub-properties associated with the property.

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

- **--latestschema**

Optionally use the latest schema instead of the one requested by the file.

<aside class="warning">This might cause errors in some data retrieval due to differences in the schema’s organizational structure between versions.</aside>

- **-j, --json**

Optionally include this flag if you wish to change the displayed output to JSON format. Preserving the JSON data structure makes the information easier to read.

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. You need to be logged in to use this flag.

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

Optionally choose to set the **includelogs** flag. Doing so will include logs in the data retrieval process.

<aside class="notice">Use this option to limit long login times.</aside>

- **--path=PATH**

Optionally set a starting point for data collection. If you do not specify a starting point, the default path will be` /redfish/v1/`. (see [Path Option](#path-option) for more information).

<aside class="notice">The <b>path</b> flag can only be specified at the time of login, so if you are already logged into the server, the <b>path</b> flag will not change the path. If you are entering a command that isn’t the <b>login</b> command, but includes your login information, you can still specify the path flag there.</aside>

#### Inputs

None

#### Outputs

None

### Get command

> Get example commands:

> Using get without any property specified shows the properties of the selected type. The full list is truncated for space.

<aside class="notice">
No reserved properties are shown with the get command.
</aside>
<aside class="notice">Arguments are not case-sensitive.</aside>

<pre>
iLOrest > select Bios.
iLOrest > <font color="#01a982">get</font>
AcpiHpet=Enabled
AcpiRootBridgePxm=Enabled
AcpiSlit=Enabled
AdjSecPrefetch=Enabled
AdminEmail=""
AdminName=Michael L
AdminOtherInfo=""
AdminPhone=""
...
</pre>

> Using get with a specific property lists the current value of that property, given that a type has already been selected.

<pre>
iLOrest > <font color="#01a982">get AdminName</font>
AdminName=Jason E
</pre>

> This command simultaneously logs in to the server at the provided URL (--url) with the provided username (-u) and password (-p), selects the `Bios.` type, and the `get` command is used to retrieve the `BootOrderPolicy` property of `Bios.`

<pre>
iLOrest > <font color="#01a982">get BootOrderPolicy --url xx.xx.xx.xx -u username -p password --select Bios.</font>
Discovering data...Done
BootOrderPolicy=RetryIndefinitely
</pre>

> Because the logout flag was included, the user is logged out of the server after the get command is performed.

<pre>
iLOrest > select ComputerSystem.
iLOrest > <font color="#01a982">get AssetTag --logout</font>
AssetTag=""
Logging session out.
</pre>

> Any Sub-Properties shown can be queried in the same form as set, list, and info: `Property/Sub-property`. You can also specify multiple properties to get simultaneously.

<pre>
iLOrest > select ComputerSystem.
iLOrest > get MemorySummary
MemorySummary=
               Status=
                       HealthRollup=OK
               TotalSystemPersistentMemoryGiB=0
               TotalSystemMemoryGiB=32
iLOrest > <font color="#01a982">get MemorySummary/Status MemorySummary/TotalSystemMemoryGiB AssetTag</font>
AssetTag=""
MemorySummary=
               Status=
                       HealthRollup=OK
               TotalSystemMemoryGiB=32
</pre>

> You can use the `noreadonly` flag to narrow down your results to only properties that can be changed.

<pre>
iLOrest > select ComputerSystem.
iLOrest > get
AssetTag=""
BiosVersion=U32 v2.10 (12/14/2018)
Boot=
      BootSourceOverrideTarget=None
      BootSourceOverrideTarget@Redfish.AllowableValues=None
                                                        Cd
                                                        Hdd
                                                        Usb
                                                        SDCard
                                                        Utilities
                                                        Diags
                                                        BiosSetup
                                                        Pxe
                                                        UefiShell
                                                        UefiHttp
                                                        UefiTarget
      BootSourceOverrideEnabled=Disabled
...
iLOrest > <font color="#01a982">get --noreadonly</font>
AssetTag=""
Boot=
      BootSourceOverrideTarget=None
      BootSourceOverrideEnabled=Disabled
      BootSourceOverrideMode=Legacy
      UefiTargetBootSourceOverride=None
HostName=ahostname
IndicatorLED=Unknown
Oem=
     Hpe=
          EndOfPostDelaySeconds=None
          PowerOnDelay=Minimum
          ServerFQDN=""
          PowerAutoOn=RemainOff
          PostMode=None
          ProcessorJitterControl=
                                  Mode=Auto
          PostDiscoveryMode=None
          PowerRegulatorMode=OSControl
</pre>


#### Syntax

get *[Property(s)] [Optional Parameters]*

#### Description

Displays the current value of a property of the currently selected type. Use this command only after a type has already been selected. If the value you are looking up is not available, it will return with no contents found for that property entry.

<aside class="notice">The difference between the <b>get</b> command and the <b>list</b> command is that the <b>list</b> command displays details about the reserved properties, while the <b>get</b> command does not.</aside>

#### Parameters

- **Property(s)**

Supplying a property or multiple properties will cause get to display the current value for that particular property or properties. Otherwise, if you wish to retrieve all the properties, run without arguments. This is still assuming you have a type already selected.

- **-h, --help**

Including the help flag will display help for the command.

-**--selector=SELECTOR**

Optionally including the **selector** flag allows you to select a type to run while running the current command. Use this command to select a type without entering another command, or to work with a type that is different from the one currently selected.

- **--filter [FILTER_ATTRIBUTE=FILTER_VALUE]**

Optionally set a filter value for a filter attribute. This uses the provided filter for the currently selected type. (see [Filter Option](#filter-option) for more information).

<aside class="notice"> Use this flag to narrow down your results. For example, selecting a common type might return multiple objects that are all of that type. If you want to modify the properties of only one of those objects, use the filter flag to narrow down results based on properties.</aside>

- **-j, --json**

Optionally include this flag to change the displayed output to JSON format. Preserving the JSON data structure makes the information easier to read.

- **--noreadonly**

Optionally include this flag to display properties that are not read-only. This is useful to see what is configurable with the selected type(s).

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. You need to be logged in to use this flag.

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

Optionally choose to set the **includelogs** flag. Doing so will include logs in the data retrieval process.

<aside class="notice">Use this option to limit long login times.</aside>

- **--path=PATH**

Optionally set a starting point for data collection. If you do not specify a starting point, the default path will be` /redfish/v1/`. (see [Path Option](#path-option) for more information).

<aside class="notice">The <b>path</b> flag can only be specified at the time of login, so if you are already logged into the server, the <b>path</b> flag will not change the path. If you are entering a command that isn’t the <b>login</b> command, but includes your login information, you can still specify the path flag there.</aside>

#### Inputs

None

#### Outputs

None

### Set command

<aside class="notice">Arguments are not case-sensitive.</aside>

> Set example commands:

> You can set multiple properties from the same type simultaneously. Add quotes around the property and value to add spaces in the value.

> <aside class="notice">Even though the get command shows **ServiceName** is set to **ExampleService** and **AdminName** set to **Jason E**, the commit command must be performed next for the changes to be updated on the server.</aside>

<pre>
iLOrest > select Bios.
iLOrest > get AdminName ServiceName
AdminName=""
ServiceName=""
iLOrest > <font color="#01a982">set "AdminName=Jason E" ServiceName=ExampleService</font>
iLOrest > get AdminName ServiceName
AdminName=Jason E
ServiceName=ExampleService
</pre>

> This command simultaneously logs in to the server at the provided URL (--url) with the provided username (-u) and password (-p), and then selects the `Bios.` type. The `set` command is used to set the `AdminName` property to `Jason E`, and the commit flag has been added to apply the changes to the server.

<pre>
iLOrest > <font color="#01a982">set "AdminName=Jason E" --url xx.xx.xx.xx -u username -p password --select Bios. --commit</font>
Discovering data...Done
Committing changes...
One or more properties were changed and will not take effect until system is reset.
</pre>


> To revert your changes on a type you can use the refresh flag.

<pre>
iLOrest > select Bios.
iLOrest > get AdminName
AdminName=Jason E
iLOrest > set AdminName=JohnDoe
iLOrest > get AdminName
AdminName=JohnDoe
iLOrest > <font color="#01a982">select Bios. --refresh</font>
iLOrest > get AdminName
AdminName=Jason E
</pre>



#### Description

Changes the value of a property in a currently selected type. Multiple properties can be set simultaneously.

<aside class="warning">The changes set will be reflected on the server only after committing them.</aside>

#### Syntax

set *[Property=Value] [Path] [Optional Parameters]*

<aside class="notice">The syntax formats used to set properties can be tricky if not done correctly. See the following examples to illustrate how the syntax works.</aside>

- `set AdminName=John`

**Correct** syntax. This sets the `AdminName` to John.

- `set “AdminName=John Doe”`

**Correct** syntax. If the property has a space in it, use quotes around the entire property/value pair. Here the `AdminName` has been set to John Doe.

- `set AdminName=””`

**Correct** syntax. Use this syntax, only quotes with no value, to remove the `AdminName` property value.

- `set AdminName=’’`

**Correct** syntax. This is an alternate syntax that also removes the `AdminName` property and sets it to nothing. Use single quotes with nothing between them.

- `set AdminName=’””’`

**Correct** syntax. This deletes the `AdminName` value.

- `set AdminName=”John Doe”`

This is **incorrect** syntax, and will not be correctly reflected on the server.

#### Parameters

- **Property(s)**

Supplying a property and a value will stage an update to that property with the supplied value.

- **-h, --help**

Including the help flag will display help for the command.

- **--selector=SELECTOR**

Optionally including the **selector** flag allows you to select a type to run while running the current command. Use this flag when you wish to select a type without entering another command, or if you wish to work with a type that is different from the one you currently have selected.

- **--filter [FILTER_ATTRIBUTE=FILTER_VALUE]**

Optionally set a filter value for a filter attribute. This uses the provided filter for the currently selected type. (see [Filter Option](#filter-option) for more information).

<aside class="notice"> Use this flag to narrow down your results. For example, selecting a common type might return multiple objects that are all of that type. If you want to modify the properties of only one of those objects, use the filter flag to narrow down results based on properties.</aside>

- **--latestschema**

Optionally use the latest schema instead of the one requested by the file.

<aside class="warning">This might cause errors in some data retrieval due to differences in the schema’s organizational structure between versions.</aside>

- **--commit**

Use this flag when you are ready to commit all pending changes. Some changes made in this way will be updated instantly, while others will be reflected the next time the server is started.

- **--biospassword=BIOSPASSWORD**

Select this flag to input a BIOS password. Include this flag if second-level BIOS authentication is needed for the command to execute.

<aside class="notice">This option is only used on Gen 9 systems.</aside>

- **--reboot=REBOOT**

Use this flag to perform a reboot command function after completion of operations. For help with parameters and descriptions regarding the reboot flag, run `help reboot`.

- **--uniqueitemoverride**

Override the measures stopping the tool from writing over items that are system unique.

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. You need to be logged in to use this flag.

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

Optionally choose to set the **includelogs** flag. Doing so will include logs in the data retrieval process.

<aside class="notice">Use this option to limit long login times.</aside>

- **--path=PATH**

Optionally set a starting point for data collection. If you do not specify a starting point, the default path will be` /redfish/v1/`. (see [Path Option](#path-option) for more information).

<aside class="notice">The <b>path</b> flag can only be specified at the time of login, so if you are already logged into the server, the <b>path</b> flag will not change the path. If you are entering a command that isn’t the <b>login</b> command, but includes your login information, you can still specify the path flag there.</aside>

#### Inputs

None

#### Outputs

None

### Save command

> Save example commands:

> Here, the server is logged into, Bios is selected, and the corresponding JSON file is saved to a local directory as the file ilorest.json. The ilorest.json file holds all the information regarding the selected type. Here, the save function was performed on the Bios type, so the `ilorest.json` file that was saved holds the information about `Bios.` The file holding that information looks like the following. 

<pre>
iLOrest > <font color="#01a982">save --select Bios. --url xx.xx.xx.xx -u username -p password</font>
Discovering data...Done
Saving configuration...
Configuration saved to: ilorest.json
</pre>


> Example json file:

```json
[
  {
    "Comments": {
      "Manufacturer": "HPE", 
      "Model": "ProLiant DL360 Gen10", 
      "BIOSFamily": "U32", 
      "BIOSDate": "12/14/2018", 
      "SerialNumber": "Kappa", 
      "iLOVersion": "iLO 5 v1.40"
    }
  }, 
  {
    "#Bios.v1_0_0.Bios": {
      "/redfish/v1/systems/1/bios/settings/": {
        "@odata.context": "/redfish/v1/$metadata#Bios.Bios", 
        "@odata.etag": "W/\"02E13BA89B606F6F6F02950EB3CA676D\"", 
        "@odata.id": "/redfish/v1/systems/1/bios/settings/", 
        "AttributeRegistry": "BiosAttributeRegistryU32.v1_2_10", 
        "Attributes": {
          "MemFastTraining": "Enabled", 
          "PowerRegulator": "DynamicPowerSavings", 
          "EmbeddedDiagnostics": "Enabled", 
          "Ipv6Address": "::", 
          "PersistentMemBackupPowerPolicy": "UseExternalBackupPower", 
          "ServiceEmail": "", 
          "FlexLom1Aspm": "Disabled", 
          "UrlBootFile": "", 
          "DcuStreamPrefetcher": "Enabled", 
          "IntelNicDmaChannels": "Enabled", 
          ...
        }, 
        "Id": "settings", 
        "Name": "BIOS Pending Settings"
      }
    }
  }
]
```

> Use the multisave option to specify multiple types to save in a single file. This file can be sent to load in order to load multiple types with a single command. All type strings are delimited by a ','.

<pre>
iLOrest > <font color="#01a982">save --multisave Bios.,ComputerSystem.</font>
Discovering data...Done
Saving configuration...
Configuration saved to: ilorest.json
</pre>

> This command simultaneously logs in to the server at the provided URL (--url) with the provided username (-u) and password (-p), selects the `Bios.` type, saves the JSON response to a file called `BiosInfo.json` in a local directory, and then logs out. 

<pre>
iLOrest > <font color="#01a982">save --select Bios. --url xx.xx.xx.xx -u username -p password -f BiosInfo.json --logout</font>
Discovering data...Done
Saving configuration...
Configuration saved to: BiosInfo.json
Logging session out.
</pre>

#### Syntax

save *[Optional Parameters]*
 
#### Description

Saves the JSON information of a selected type to a local file. Use this command along with the `load` command when you want to modify properties of a selected type through file editing. Using this command saves a local copy of your selected type’s JSON information.

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

- **-f FILENAME, --filename=FILENAME**

Use this flag if you wish to use a different filename than the default one. The default filename is `ilorest.json`.

- **--selector=SELECTOR**

Optionally including the **selector** flag allows you to select a type to run while running the current command. Use this flag when you wish to select a type without entering another command, or if you wish to work with a type that is different from the one you currently have selected.

- **--multisave=MULTISAVE**

Optionally include this flag to save multiple types of single file. Override the currently selected type.

- **--filter [FILTER_ATTRIBUTE=FILTER_VALUE]**

Optionally set a filter value for a filter attribute. This uses the provided filter for the currently selected type. (see [Filter Option](#filter-option) for more information).

<aside class="notice"> Use this flag to narrow down your results. For example, selecting a common type might return multiple objects that are all of that type. If you want to modify the properties of only one of those objects, use the filter flag to narrow down results based on properties.</aside>

- **-j, --json**

Optionally include this flag if you wish to change the displayed output to JSON format. Preserving the JSON data structure makes the information easier to read.

- **--encryption=ENCRYPTION**

Optionally include this flag to encrypt a file using the key provided.

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. You need to be logged in to use this flag.

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

Optionally choose to set the **includelogs** flag. Doing so will include logs in the data retrieval process.

<aside class="notice">Use this option to limit long login times.</aside>

- **--path=PATH**

Optionally set a starting point for data collection. If you do not specify a starting point, the default path will be` /redfish/v1/`. (see [Path Option](#path-option) for more information).

<aside class="notice">The <b>path</b> flag can only be specified at the time of login, so if you are already logged into the server, the <b>path</b> flag will not change the path. If you are entering a command that isn’t the <b>login</b> command, but includes your login information, you can still specify the path flag there.</aside>

#### Inputs

None

#### Outputs

JSON file

Save a selected type to a file in JSON format. You can edit the values in the file, and then use the `load` command to upload the changes to the server. 

### Load command

> Load example commands:

> If no filename is supplied with the (-f, --filename) option, save looks for a file named `ilorest.json` in the current working directory. Save will automatically select the required type to make changes.

<pre>
iLOrest > <font color="#01a982">load</font>
Loading configuration...
Committing changes...
One or more properties were changed and will not take effect until system is reset.
</pre>

> This command simultaneously logs in to the server at the provided URL (--url) with the provided username (-u) and password (-p) and load a file from the current working directory called `biosconfig.json`.

<pre>
iLOrest > <font color="#01a982">load --url xx.xx.xx.xx -u username -p password -f biosconfig.json</font>
Discovering data...Done
Loading configuration...
Committing changes...
One or more properties were changed and will not take effect until system is reset.
</pre>

> This is the multi-server configuration setup. You must pass in a multi-server file in the following format.

<pre>
iLOrest > <font color="#01a982">load -m mpfilename.txt -f biosconfig.json</font>
Discovering data...Done
Loading configuration for multiple servers...
Logging session out.
Checking given server information...
Create multiple processes to load configuration concurrently to all servers...
Loading Configuration for xx.xx.xx.xx : SUCCESS
Loading Configuration for xx.xx.xx.xy : SUCCESS
All servers have been successfully configured.
</pre>

> All servers are configured concurrently. Because the filename tag is included, it searches for the file called `biosconfig.json` and loads that information to the servers. If no values have changed, the load process is complete. If any property values have changed, the changes are committed and the user is logged out of the server. Logs of the entire process are then stored in the same location as the iLOrest logs.

<pre>
--url 10.0.0.100 -u username -p password
--url 10.0.0.101 -u username -p password
--url 10.0.0.102 -u username -p password
--url 10.0.0.103 -u username -p password
</pre>



#### Syntax

load *[Optional Parameters]*

#### Description

Loads the server configuration from a file. Run this command without parameters to use the configuration found in the file called `ilorest.json`. Otherwise, you can point this command to use any file you specify. Use this function to change the properties of a type to new values. This command uploads the new values of the type’s properties to the server.

<aside class="notice"><b>Read-only</b> properties are skipped, and non-read only properties continue to be set.</aside>

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

- **-f FILENAME, --filename=FILENAME**

Use this flag if you wish to use a different filename than the default one. The default filename is `ilorest.json`.

- **--latestschema**

Optionally use the latest schema instead of the one requested by the file.

<aside class="warning">This might cause errors in some data retrieval due to differences in the schema’s organizational structure between versions.</aside>

- **--biospassword=BIOSPASSWORD**

Select this flag to input a BIOS password. Include this flag if second-level BIOS authentication is needed for the command to execute.

<aside class="notice">This option is only used on Gen 9 systems.</aside>

- **--uniqueitemoverride**

Override the measures stopping the tool from writing over items that are system unique.

- **-m MPFILENAME, --multiprocessing=MPFILENAME**

Optionally supply a filename to a multi-processing file to load concurrently on multiple servers.

- **-o OUTDIRECTORY, --outputdirectory=OUTDIRECTORY**

Use the provided directory to output data for a multiple server configuration.

- **--encryption=ENCRYPTION**

Optionally include this flag to decrypt a file using the key provided.

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. You need to be logged in to use this flag.

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

JSON Object

Input a JSON object to load from a custom configuration file, otherwise the configuration will default to looking for a file called `ilorest.json`.

#### Outputs

None

### Status command

> Status example commands:

> The status command shows changes to be committed. The status command shows all pending changes, including changes for different types.

<pre>
iLOrest > <font color="#01a982">status</font>
Current changes found:
Bios.v1_0_0(/redfish/v1/systems/1/bios/settings/) (Currently selected)
        Attributes/ServiceName=simpleservice
ComputerSystem.v1_4_0(/redfish/v1/Systems/1/)
        AssetTag=newtag
</pre>

> Once changes are committed they no longer show in status.

<pre>
iLOrest > <font color="#01a982">status</font>
Current changes found:
Bios.v1_0_0(/redfish/v1/systems/1/bios/settings/) (Currently selected)
        Attributes/ServiceName=simpleservice
ComputerSystem.v1_4_0(/redfish/v1/Systems/1/)
        AssetTag=newtag
iLOrest > commit
Committing changes...
One or more properties were changed and will not take effect until system is reset.
The operation completed successfully.
iLOrest > status
No changes found
</pre>



#### Syntax

status *[Optional Parameters]*

#### Description

Displays all pending changes, regardless of which type is currently selected. All the changes that have not been committed yet will be shown.

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

#### Inputs

None

#### Outputs

None

### Commit command

> Commit example commands:

> Commit all pending changes made by set by running the `commit` command.

<pre>
iLOrest > select ComputerSystem.
iLOrest > set AssetTag=newtag
iLOrest > select Bios.
iLOrest > set servicename=simpleservice
iLOrest > <font color="#01a982">commit</font>
Committing changes...
One or more properties were changed and will not take effect until system is reset.
The operation completed successfully.
</pre>


> If you do not commit before logging out changes will be lost.

<aside class="notice">
You must commit changes before logging out or settings will not be updated on the server.
</aside>

<pre>
iLOrest > select Bios.
iLOrest > get AdminName
AdminName=Chelsea K
iLOrest > set AdminName=newname
iLOrest > get AdminName
AdminName=newname
iLOrest > logout
Logging session out.
iLOrest > get AdminName --select Bios.
Discovering data...Done
AdminName=Chelsea K
</pre>

> Commit after running other commands by using the `--commit` option. This command simultaneously logs in to the server at the provided URL (--url) with the provided username (-u, --user) and password (-p, --password), selects the `ComputerSystem.` type, sets `AssetTag` to `""`, commits the change, and logs-out.

<pre>
iLOrest > <font color="#01a982">set AssetTag="" --url xx.xx.xx.xx -u username -p password --selector ComputerSystem. --commit --logout</font>
Discovering data...Done
Committing changes...
The operation completed successfully.
Logging session out.
</pre>



#### Syntax

commit *[Optional Parameters]*

#### Description

Applies all changes made during the current session. After you have changed one or more values for the property of a type, you need to commit those changes in order for those changes to be reflected on the server.

#### Usage in Other Commands

To commit at the end of a command, include the *--commit* option. Not all commands have the `commit` flag, run help on the command to see available options.

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

- **--biospassword=BIOSPASSWORD**

Select this flag to input a BIOS password. Include this flag if second-level BIOS authentication is needed for the command to execute.

<aside class="notice">This option is only used on Gen 9 systems.</aside>

- **--reboot=REBOOT**

Use this flag to perform a reboot command function after completion of operations. For help with parameters and descriptions regarding the reboot flag, run `help reboot`.

#### Inputs

None

#### Outputs

None

### Logout command

> Logout example commands:

> Use the logout command to end the session and disconnect from the server.

<pre>
iLOrest > login xx.xx.xx.xx -u username -p password
Discovering data...Done
iLOrest > <font color="#01a982">logout</font>
Logging session out.
</pre>

> Logout from another command using the `--logout` option.

<pre>
iLOrest > get AssetTag --select ComputerSystem. <font color="#01a982">--logout</font>
AssetTag=""
Logging session out.
</pre>


#### Syntax

logout *[Optional Parameters]*

#### Description

Use the `logout` command to exit your session and to disconnect from the server.

#### Usage in Other Commands

To log out at the end of a command, include the *--logout* option. Not all commands have the `logout` flag, run help on the command to see available options.

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

#### Inputs

None

#### Outputs

None

### Exit command

> Exit example commands

> This command exits the interactive shell.

<pre>
iLOrest > <font color="#01a982">exit</font>
Logging session out.
Bye for now
</pre>

#### Syntax

exit *[Optional Parameters]*

#### Description

Use the `exit` command if you wish to exit from the interactive shell. Using exit will also log you out and disconnect you from the server.

#### Parameters

- **-h, --help**

Including the help flag will display help for the command.

#### Inputs

None

#### Outputs

None
