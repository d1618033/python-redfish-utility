## Global commands

This section includes commands as well as their usage and examples for general commands in the RESTful Interface Tool. They include commands used to do things such as listing help for using commands, viewing, retrieving, modifying, and committing changes to server properties, and authenticating and logging in and out of the server.

### Help Command

> Help example commands:

> Entering the help to list the global iLOrest options and help options for all available commands.

> ![Help Example 1](images/examples/help_ex1.png "Help example 1")

> Providing a specific command will list help regarding that specific command.

> ![Help Example 2](images/examples/help_ex2.png "Help example 2")

> The alternate syntax to list details regarding a command.

> ![Help Example 3](images/examples/help_ex3.png "Help example 3")


#### Syntax

help *[command] [optional parameters]*

#### Description

Displays command line syntax and help menus for individual commands. Use this command if you want to know more about a command or need help using a command. Alternatively, you can use the `help` command without specifying a particular command if you wish to see all available commands and options.

#### Parameters

- Command 

Supplying a command to help will cause this command to display the help message corresponding to the given command, as well as the options relating to that particular command.

<aside class="notice">If no command is provided, the help command will provide help on all available commands and options.</aside>

- **-h, --help**

Running the help command with the **–h** or **–help** command will display information on how to use the help command.

- **-c FILE, --config=FILE**

Use the provided configuration file instead of the default one.

- **--cache-dir=PATH**

Use the provided directory as the location to cache data (default location: `C:\Users\USERNAME\AppData\Roaming\.ilorest`).

#### Global Options

**-v, --verbose**

Display verbose information.

**-d, --debug**

Display debug information.

**-nocache**

During execution the application will temporarily store data only in memory.

**-nologo**

Include to block copyright and logo.

**-redfish**

Use this flag if you wish to to enable Redfish only compliance. It is enabled by default in systems with iLO5 and above.

**_Important: The **-redfish** global option is required for iLO 4 firmware version 2.40 and is not required for iLO 5._** 

**--latestschema**

Optionally use the latest schema instead of the one requested by the file. 

<aside class="notice">
Might cause errors in some data retrieval due to difference in schema versions.
</aside>

#### Inputs

None

#### Outputs

None

### Login command

> Login example commands:

> To login remotely, supply the URL, username, and password for the server. Here the selector tag has been included so that the **HpBios** type is selected once the user is logged in. You can prove that the **HpBios** type has indeed been selected when we enter the select command.

> ![Login Example 1](images/examples/login_ex1.png "Login example 1")

> Here the path was set to **/rest/v1/systems/1/bios** instead of the default **/rest/v1/**. To check that the path has indeed been set to a different place, the types command was entered and returned the types in the specified path, instead of in the default **/rest/v1/**. You can log in again with the default **/rest/v1/** to show the change.

> ![Login Example 2-1](images/examples/login_ex2-1.png "Login example 2-1")

> ![Login Example 2-2](images/examples/login_ex2-2.png "Login example 2-2")

> Here the URL, username, and password information are not specified here or in the configuration file, and the server was logged in to locally.

> ![Login Example 3](images/examples/login_ex3.png "Login example 3")



#### Syntax

login *[URL] [User] [Password] [Optional Parameters]*

#### Description

Connects to a server, establishes a secure session, and discovers data from iLO. Use the `login` command to connect to a server. This command establishes a secure session and discovers data from iLO. If you are logging in to a local server, run the command without arguments. If you are not logging in to a local server, see the following:

#### Parameters

- **URL**

Connect to the server located at the provided URL.

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User**

Connect to the server as the provided user.

- **-p Password**

Connect to the server with the password corresponding to the given user.

- **--includelogs**

Optionally choose to set the **includelogs** flag. Doing so will include logs in the data retrieval process.

- **--selector=SELECTOR**

Optionally including the **selector** flag allows you to select a type to run the current command on. Use this flag when you wish to select a type without entering another command, or if you wish to work with a type that is different from the one you currently have selected.

- **--filter [FILTER_ATTRIBUTE=FILTER_VALUE]**

Optionally set a filter value for a filter attribute. This uses the provided filter for the currently selected type.

<aside class="notice">Use this flag to narrow down your results. For example, selecting a common type might return multiple objects that are all of that type. If you want to modify the properties of only one of those objects, use the <b>filter</b> flag to narrow down results based on properties.</aside>

- **--path=PATH**

Optionally set a starting point for data collection. If you do not specify a starting point, the default path will be /rest/v1.

<aside class="notice">The path flag can only be specified at the time of login, so if you are already logged in to the server, the path flag will not change the path. If you are entering a command that isn’t the login command, but include your login information, you can still specify the path flag there.</aside>

- **--biospassword=BIOSPASSWORD**

Select this flag to input a BIOS password. Include this flag if second-level BIOS authentication is needed for the command to execute.

<aside class="warning">Cache is activated session keys and it is normal to see these keys stored in plaintext. This warning regarding an activated cache is normal to see. The full list has been truncated for space.</aside>

### Types command

> Types example commands:

> This command will list all the available types that you can select. The full list has been truncated for space.

> ![Types Example 1](images/examples/types_ex1.png "Types example 1")


> This command simultaneously logs in to the server at the provided URL with the provided username and password, and list all the available types that you can select. The full list has been truncated here for space.

> ![Types Example 2](images/examples/types_ex2.png "Types example 2")


> Specifying a path for the type command will print the types found in the given path. Here only the types found in **/rest/v1/systems/1/bios/** were returned.

> ![Types Example 3](images/examples/types_ex3.png "Types example 3")


#### Syntax

types *[Optional Parameters]*

#### Description

The `types` command displays all selectable types available within the currently logged in server. Types include a name as well as version information. Types represent the schema used for the resource and indicate the version of the schema. Version information is `major.minor.errata` (for example `SystemRoot.0.9.5`). Major versions are not backwards compatible, but everything else is.

#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--includelogs**

Optionally choose to set the **includelogs** flag. Doing so will include logs in the data retrieval process.

- **--path=PATH**

Optionally set a starting point for data collection. If you do not specify a starting point, the default path will be` /rest/v1`.

<aside class="notice">The <b>path</b> flag can only be specified at the time of login, so if you are already logged into the server, the <b>path</b> flag will not change the path. If you are entering a command that isn’t the <b>login</b> command, but include your login information, you can still specify the path flag there.</aside>

- **-fulltypes**

Optionally include this flag if you would prefer to return the full type name instead of the simplified versions.

#### Inputs

None

#### Outputs

None

<aside class="notice">See the iLO RESTful API Data Model Reference (iLO 4) at <a href=" http://www.hpe.com/info/restfulinterface/docs">http://www.hpe.com/info/restfulinterface/docs</a> for a list and description of all the possible types.</aside>

### Select command

> Select example commands:

> Before the commands were entered here, the user was not logged in to the server. When you use the select tag with login credentials, you are logged in to the server and the inputted type is selected. The type was selected by entering the select command with no type specified is verified, which shows that the currently selected type is returned. 

<aside class="notice">
Adding a period after the type selected, **HpBios**, limits the selection, preventing accidentally also selecting **HpBiosMapping**. This also removes the need to include the version.
</aside>

> ![Select Example 1](images/examples/select_ex1.png "Select example 1")


> Here the **ComputerSystem** type was selected instead of the **HpBios** type like in the example above.

> ![Select Example 2](images/examples/select_ex2.png "Select example 2")



#### Syntax

select *[Type] [Optional Parameters]*

#### Description

Use `select` to choose a specific type to work with. Eligible types for selection are those listed by the types command. Because commands are entered individually in the RESTful Interface Tool, working with specific types requires that you highlight or select the particular type you are working with. Use the `select` command to highlight a type so that you can work with it.

#### Parameters

- **Type**

Specify the type you want to select. Omitting a type to select will cause select to display the currently selected type.

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--includelogs**

Optionally choose to set the **includelogs** flag. Doing so will include logs in the data retrieval process.

- **--filter [FILTER_ATTRIBUTE=FILTER_VALUE]**

Optionally set a filter value for a filter attribute. This uses the provided filter for the currently selected type.

<aside class="notice"> Use this flag to narrow down your results. For example, selecting a common type might return multiple objects that are all of that type. If you want to modify the properties of only one of those objects, use the filter flag to narrow down results based on properties.</aside>

- **--path=PATH**

Optionally set a starting point for data collection. If you do not specify a starting point, the default path will be` /rest/v1`.

<aside class="notice"> The <b>path</b> flag can only be specified at the time of login, so if you are already logged in to the server, the <b>path</b> flag will not change the path. If you are entering a command that isn’t the login command, but include your login information, you can still specify the <b>path</b> flag there.</aside>

- **--biospassword=BIOSPASSWORD**

Select this flag to input a BIOS password. Include this flag if second-level BIOS authentication is needed for the command to execute.

#### Inputs

None

#### Outputs

None

### List command

> List command examples:

> This command shows the current values of the properties of the selected type, including reserved properties. The full list has been truncated here for space.

> ![List Example 1](images/examples/list_ex1.png "List example 1")

> Including the **--json** tag preserves the JSON structure of the type’s information. The full list has been truncated here for space.

> ![List Example 2](images/examples/list_ex2.png "List example 2")

> After the server is logged in to and the EthernetNetworkInterface type is selected, the list command reveals that there are two objects with that type on the server. So, to only show the one at **href=/rest/v1/Managers/1/NICs/2**, the list command was run again with the **--filter** flag included. The full list has been truncated here for space.

> ![List Example 3-1](images/examples/list_ex3-1.png "List example 3-1")

> ![List Example 3-2](images/examples/list_ex3-2.png "List example 3-2")

> ![List Example 3-3](images/examples/list_ex3-3.png "List example 3-3")



#### Syntax

list *[Optional Parameters]*

#### Description

Displays the JSON model of the currently selected type, showing current value(s) of properties including reserved properties. After you have selected a type, you can use the list command to see the details of the currently selected type. This includes information such as current values of properties.

<aside class="notice">The list command does display reserved properties for types, while the get command does not.</aside>

#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--includelogs**

Optionally choose to set the **includelogs** flag. Doing so will include logs in the data retrieval process.

- **--filter [FILTER_ATTRIBUTE=FILTER_VALUE]**

Optionally set a filter value for a filter attribute. This uses the provided filter for the currently selected type.

<aside class="notice"> Use this flag to narrow down your results. For example, selecting a common type might return multiple objects that are all of that type. If you want to modify the properties of only one of those objects, use the filter flag to narrow down results based on properties.</aside>


- **---j, --json**

Optionally include this flag if you wish to change the displayed output to JSON format. Preserving the JSON data structure makes the information easier to read.

- **--path=PATH**

Optionally set a starting point for data collection. If you do not specify a starting point, the default path will be `/rest/v1`.

<aside class="notice"> The <b>path</b> flag can only be specified at the time of login, so if you are already logged in to the server, the <b>path</b> flag will not change the path. If you are entering a command that isn’t the login command, but include your login information, you can still specify the <b>path</b> flag there.</aside>

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. You need to be logged in to use this flag.

#### Inputs

None

#### Outputs

None

### Info Command

> Info command examples:

> Omitting a property when using the info command causes info to list all available options, given that you have already selected a type. The full list has been truncated for space.

> ![Info Example 1](images/examples/info_ex1.png "Info example 1")


> Multiple properties under the VirtualMedia type are specified. By passing multiple properties, it returns the information on all of the properties passed.

> ![Info Example 2](images/examples/info_ex2.png "Info example 2")

> ![Info Example 3](images/examples/info_ex3.png "Info example 3")



#### Syntax

info *[Property] [Optional Parameters]*

#### Description

Displays detailed information about a property within a selected type. This section includes commands as well as their usage and examples for general commands in the RESTful Interface Tool. They include commands used to do things such as listing help for using commands, viewing, retrieving, modifying, and committing changes to server properties, and authenticating and logging in and out of the server.

#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--includelogs**

Optionally choose to set the **includelogs** flag. Doing so will include logs in the data retrieval process.

- **--filter [FILTER_ATTRIBUTE=FILTER_VALUE]**

Optionally set a filter value for a filter attribute. This uses the provided filter for the currently selected type.

<aside class="notice"> Use this flag to narrow down your results. For example, selecting a common type might return multiple objects that are all of that type. If you want to modify the properties of only one of those objects, use the filter flag to narrow down results based on properties.</aside>

- **--latestschema**

Optionally use the latest schema instead of the one requested by the file.

<aside class="warning">This might cause errors in some data retrieval due to differences in the schema’s organizational structure between versions.</aside>

- **-j, --json**

Optionally include this flag if you wish to change the displayed output to JSON format. Preserving the JSON data structure makes the information easier to read.

- **--path=PATH**

Optionally set a starting point for data collection. If you do not specify a starting point, the default path will be `/rest/v1`.

<aside class="notice"> The <b>path</b> flag can only be specified at the time of login, so if you are already logged in to the server, the <b>path</b> flag will not change the path. If you are entering a command that isn’t the login command, but include your login information, you can still specify the <b>path</b> flag there.</aside>

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. You need to be logged in to use this flag.

#### Inputs

None

#### Outputs

None

### Get command

> Get example commands:

> Using get without any property specified shows the properties of the selected type. 

<aside class="notice">
No reserved properties are shown with the get command. Also, the full list is truncated for space.
</aside>

> ![Get Example 1](images/examples/get_ex1.png "Get example 1")

> Using get with a specific property lists the current value of that property, given that a type has already been selected.

> ![Get Example 2](images/examples/get_ex2.png "Get example 2")


> Here the server at xx.xx.xx.xx is logged into, the type HpBios. is selected, and the get command is used to retrieve the BootOrderPolicy property of HpBios.

> ![Get Example 3](images/examples/get_ex3.png "Get example 3")


> Because the logout flag was included here, the user is logged out of the server after the get command here is performed.

> ![Get Example 4](images/examples/get_ex4.png "Get example 4")

> Here, the get command utilizes its ability to take multiple properties as arguments. The first time the get command was used on the **ConnectedVia** and **MediaTypes property**, two objects of type **VirtualMedia** and **MediaTypes** were returned. However, to get the **ConnectedVia** and **MediaTypes** value for only one of the types, the filter tag was included. When the get command was run with the filter, the only value printed this time was the **ConnectedVia** value and the **MediaTypes** value for the **VirtualMedia** located at the specified address.

> ![Get Example 5](images/examples/get_ex5.png "Get example 5")

#### Syntax

get *[Property] [Optional Parameters]*

#### Description

Displays the current value of a property of the currently selected type. Use the `get` command to retrieve the current value of a property. Use this command only after a type has already been selected. If the value you are looking up has no value, it will return with no contents found for that property entry.

<aside class="notice">The difference between the <b>get</b> command and the <b>list</b> command is that the <b>list</b> command also lists details about reserved properties, while the <b>get</b> command does not.</aside>

#### Parameters

- **Property**

Supplying a property will cause get to display the current value for that particular property. Otherwise, if you wish to retrieve all the properties, run without arguments. This is still assuming you have a type already selected.

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--includelogs**

Optionally choose to set the **includelogs** flag. Doing so will include logs in the data retrieval process.

- **--filter [FILTER_ATTRIBUTE=FILTER_VALUE]**

Optionally set a filter value for a filter attribute. This uses the provided filter for the currently selected type.

<aside class="notice"> Use this flag to narrow down your results. For example, selecting a common type might return multiple objects that are all of that type. If you want to modify the properties of only one of those objects, use the <b>filter</b> flag to narrow down results based on properties.</aside>

- **-j, --json**

Optionally include this flag if you wish to change the displayed output to JSON format. Preserving the JSON data structure makes the information easier to read.

- **--path=PATH**

Optionally set a starting point for data collection. If you do not specify a starting point, the default path will be `/rest/v1`.

<aside class="notice"> The <b>path</b> flag can only be specified at the time of login, so if you are already logged in to the server, the <b>path</b> flag will not change the path. If you are entering a command that isn’t the login command, but include your login information, you can still specify the <b>path</b> flag there.</aside>

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. You need to be logged in to use this flag.

#### Inputs

None

#### Outputs

None

### Set command

> Set example commands:

> Here the **ServiceName** property of the type **HpBios** has been set to the value **ExampleService**. When the get command is performed next, the value of **ServiceName** has been set to **ExampleService**. 

<aside class="notice">
Even though the get command shows **ServiceName** is set to **ExampleService**, the commit command must be performed next for the changes to be reflected next time the server is logged into.
</aside>

> ![Set Example 1](images/examples/set_ex1.png "Set example 1")



> Set the attribute of a type using the set command. Here the server is logged into using the username, password, and URL flags, and then **HpBios** is selected with the selector flag. Then, the **ServiceName** property is set.

> ![Set Example 2](images/examples/set_ex2.png "Set example 2")


> Here the **AdminName** property of the type **HpBios** was set to the value **JohnDoe**. Including the commit flag committed the changes, so that after logging back into the server, the **AdminName** becomes **JohnDoe**. Otherwise it would have returned to its previous value. Include the **biospassword** flag to input a password if second level BIOS authentication is required.

> ![Set Example 3](images/examples/set_ex3.png "Set example 3")


> Here the **AdminName** property of the type **HpBios** was set to the value **JohnDoe**. However, since the reboot flag was included but the commit flag was not, after the server is logged into again the **AdminName** property has returned to its original value.

> ![Set Example 4](images/examples/set_ex4.png "Set example 4")

#### Syntax

set *[Property=Value] [Path] [Optional Parameters]*

<aside class="notice">The syntax formats used to set properties can be tricky if not done correctly. See the following examples to illustrate how the syntax works.</aside>

- `set AdminName=John`

This is **correct** syntax. This sets the `AdminName` to John.

- `set “AdminName=John Doe”`

This is **correct** syntax. If the property has a space in it, use quotes around the entire property/value pair. Here the `AdminName` has been set to John Doe.

- `set AdminName=””`

This is **correct** syntax. Use this syntax if you wish to remove the `AdminName` property value, using quotes that have nothing between them.

- `set AdminName=’’`

This is **correct** syntax. This is an alternate syntax that also removes the `AdminName` property and sets it to nothing. Use single quotes with nothing between them.

- `set AdminName=’””’`

This is **correct** syntax. This deletes the `AdminName` value.

- `set AdminName=”John Doe”`

This is **incorrect** syntax, and will not be correctly reflected on the server.

#### Description

Given that a type is currently selected, changes the value of a property in that type. Use the `set` command to assign a value to the property of a type, provided that a type has already been selected. Properties in a multilevel path can be set using this command, and multiple properties of a type can also be simultaneously set.

<aside class="warning">No changes you have set will be reflected on the server unless you commit your changes afterward.</aside>

#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--includelogs**

Optionally choose to set the **includelogs** flag. Doing so will include logs in the data retrieval process.

- **--selector=SELECTOR**

Optionally include the selector flag to select a type to run the current command on. Use this flag when you wish to select a type without entering another command, or if you wish to work with a type that is different from the one you currently have selected.

- **--filter [FILTER_ATTRIBUTE=FILTER_VALUE]**

Optionally set a filter value for a filter attribute. This uses the provided filter for the currently selected type.

<aside class="notice"> Use this flag to narrow down your results. For example, selecting a common type might return multiple objects that are all of that type. If you want to modify the properties of only one of those objects, use the filter flag to narrow down results based on properties.</aside>

- **--latestschema**

Optionally use the latest schema instead of the one requested by the file.

<aside class="warning">This might cause errors in some data retrieval due to differences in the schema’s organizational structure between versions.</aside>

- **--commit**

Use this flag when you are ready to commit all the changes for the current selection. Including the --commit flag will log you out of the server after the command is run. Some changes made in this way will be updated instantly, while others will be reflected the next time the server is started.

- **--path=PATH**

Optionally set a starting point for data collection. If you do not specify a starting point, the default path will be` /rest/v1`.

<aside class="notice"> The <b>path</b> flag can only be specified at the time of login, so if you are already logged in to the server, the <b>path</b> flag will not change the path. If you are entering a command that isn’t the login command, but include your login information, you can still specify the <b>path</b> flag there.</aside>

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. You need to be logged in to use this flag.

- **--biospassword=BIOSPASSWORD**

Select this flag to input a BIOS password. Include this flag if second-level BIOS authentication is needed for the command to execute.

- **--reboot=REBOOT**

Use this flag to perform a reboot command function after completion of operations. For help with parameters and descriptions regarding the reboot flag, run `help reboot`.

- **--uniqueitemoverride**

Override the measures stopping the tool from writing over items that are system unique.

#### Inputs

None

#### Outputs

None

### Save command

> Save example commands:

> Here, the server is logged into, HpBios is selected, and the corresponding JSON file is saved to a local directory as the file ilorest.json. The ilorest.json file holds all the information regarding the selected type. Here, the save function was performed on the HpBios type, so the ilorest.json file that was saved holds the information about HpBios. The file holding that information looks like the following. 

> ![Save Example 1](images/examples/save_ex1.png "Save example 1")



> Example json file

```json
[
  {
    "Comments": {
      "Manufacturer": "HP", 
      "Model": "ProLiant DL360 Gen9", 
      "BIOSFamily": "P89", 
      "BIOSDate": "05/03/2015"
    }
  }, 
  {
    "HpBios.1.2.0": {
      "/rest/v1/systems/1/bios/Settings": {
        "AdminPassword": null, 
        "BootMode": "Uefi", 
        "Dhcpv4": "Enabled", 
        "DynamicPowerCapping": "Auto", 
        "EmbeddedSerialPort": "Com1Irq4", 
        "EmbeddedUefiShell": "Enabled", 
        "IntelPerfMonitoring": "Disabled", 
		…
        "UrlBootFile": "", 
        "Usb3Mode": "Auto", 
        "VlanPriority": 0, 
        "WakeOnLan": "Enabled"
      }	
    }
  }
]
```

> Here, **HpBios** is selected, and the corresponding JSON file is saved to a file called **HpBiosInfo.json** in a local directory. The attached --logout flag logs the user out after this command is completed.

> ![Save Example 2](images/examples/save_ex2.png "Save example 2")


#### Syntax

save *[Optional Parameters]*

#### Description

Saves the JSON information of a selected type to a local file. Use this command along with the `load` command when you want to modify properties of a selected type through file editing. Using this command saves a local copy of your selected type’s JSON information.

#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-f FILENAME, --filename=FILENAME**

Use this flag if you wish to use a different filename than the default one. The default filename is `ilorest.json`.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--includelogs**

Optionally choose to set the **includelogs** flag. Doing so will include logs in the data retrieval process.

- **--selector=SELECTOR**

Include the selector flag to select a type to run the current command on. Use this flag when you wish to select a type without entering another command, or if you wish to work with a type that is different from the one you currently have selected.

- **--filter [ATTRIBUTE]=[VALUE]**

Optionally set a filter value for a filter attribute. This uses the provided filter for the currently selected type.

<aside class="notice"> Use this flag to narrow down your results. For example, selecting a common type might return multiple objects that are all of that type. If you want to modify the properties of only one of those objects, use the filter flag to narrow down results based on properties.</aside>

- **-j, --json**

Optionally include this flag if you wish to change the displayed output to JSON format. Preserving the JSON data structure makes the information easier to read.

- **--path=PATH**

Optionally set a starting point for data collection. If you do not specify a starting point, the default path will be` /rest/v1`.

<aside class="notice"> The <b>path</b> flag can only be specified at the time of login, so if you are already logged in to the server, the <b>path</b> flag will not change the path. If you are entering a command that isn’t the login command, but include your login information, you can still specify the <b>path</b> flag there.</aside>

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. You need to be logged in to use this flag.

- **-e ENCRYPTION, --encryption=ENCRYPTION**

Optionally include this flag to encrypt/decrypt a file using the key provided.

#### Inputs

None

#### Outputs

JSON file

Save a selected type to a file in JSON format. You can edit the values in the file, and then use the `load` command to upload the changes to the server. 

### Load command

> Load example commands:

> This is the multi-server configuration setup. You must pass in a multi-server file in the following format.

> ![Load Example 1](images/examples/load_ex1.png "Load example 1")



> All servers are configured concurrently. Because the filename tag is included, it searches for the file called **output.json** and loads that information to the servers by setting any property values that have changed. If no values have changed, the load process is complete. If any property values have changed, the changes are committed and the user is logged out of the server. Logs of the entire process are then stored in the same location as the ilorest logs.

> ![Load Example 2](images/examples/load_mpfile.png "Load example 2")


> The load command entered here first logs into the server using the given information. Then, since no file was specified for it to load, it searches for the file called **ilorest.json** and loads that information to the server by setting any property values that have changed. If no values have changed, it is finished. Otherwise, it commits the changes and logs the user out of the server. Here there have been changes made, so the after changing property values the changes are committed and the server logged out of.

> ![Load Example 3](images/examples/load_ex2.png "Load example 3")


> The load command entered here first logs into the server using the given information. Since the filename tag has been included, it searches for the file called **biosconfig.json** and loads that information to the server by setting any property values that have changed. If no values have changed, it is finished. Otherwise, it commits the changes. Here all the properties specified in **biosconfig.json** are the same as the values on the server, so the command is finished executing. 

> ![Load Example 4](images/examples/load_ex3.png "Load example 4")



#### Syntax

load *[Optional Parameters]*

#### Description

Loads the server configuration from a file. Run this command without parameters to use the configuration found in the file called `ilorest.json`. Otherwise, you can point this command to use any file you specify. Use this function to change the properties of a type to new values. This command uploads the new values of the type’s properties to the server.

<aside class="notice"><b>Read-only</b> properties are skipped, and non-read only properties continue to be set.</aside>

#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-f FILENAME, --filename=FILENAME**

Use this flag if you wish to use a different filename than the default one. The default filename is `ilorest.json`.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--latestschema**

Optionally use the latest schema instead of the one requested by the file.

<aside class="warning">This might cause errors in some data retrieval due to differences in the schema’s organizational structure between versions.</aside>

- **--biospassword=BIOSPASSWORD**

Select this flag to input a BIOS password. Include this flag if second-level BIOS authentication is needed for the command to execute.

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. You need to be logged in to use this flag.

- **--uniqueitemoverride**

Override the measures stopping the tool from writing over items that are system unique.

- **-m MPFILENAME, --multiprocessing=MPFILENAME**

Use the provided filename to obtain data.

- **-o OUTDIRECTORY, --outputdirectory=OUTDIRECTORY**

Use the provided directory to output data for a multiple server configuration.

- **-o OFILENAME, --outputfilename=OFILENAME**

Use the provided filename to output data.

- **-e ENCRYPTION, --encryption=ENCRYPTION**

Optionally include this flag to encrypt/decrypt a file using the key provided.

#### Inputs

JSON Object

Input a JSON object to load from a custom configuration file, otherwise the configuration will default to looking for a file called `ilorest.json`.

#### Outputs

None

### Status command

> Status example commands:

> The status command shows changes to be committed. Here we see that the Description property of **ComputerSystem** has been set to **ComputerSystemView**, and that the **ServiceName** property of **HpBios** has been set to **SimpleService**. The status command shows all pending changes, including changes for different types.

> ![Status Example 1](images/examples/status_ex1.png "Status example 1")



#### Syntax

status *[Optional Parameters]*

#### Description

Displays all pending changes. All pending changes will be displayed, regardless of which type is currently selected. Unless you have already committed your changes using the `–commit` flag, changes you make to properties will be queued. Use the `status` command to see all the changes that have not been committed yet.

#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

#### Inputs

None

#### Outputs

None

### Commit command

> Commit example commands:

> Once you have made changes and are ready for them to take effect, use the commit command to commit your changes. Here the commit command saves the **AdminName** property of **HpBios.** to the new value of **DeniseHarkins**, and includes the **biospassword=BIOSPASSWORD** for second level BIOS authentication. The included reboot flag reboots the server. The commit command always logs out of the server.

> ![Commit Example 1](images/examples/commit_ex1.png "Commit example 1")


> Here the logout flag was used to demonstrate that the server can be logged out of after another command. Here, after the **EmbSata1Enabled** property of HpBios was set to a new value, then the server was logged out of because the logout flag was included. 

<aside class="notice">
The commit flag isn't used here; therefore, changes are not committed upon logout.
</aside>

> ![Commit Example 2](images/examples/commit_ex2.png "Commit example 2")



#### Syntax

commit *[Optional Parameters]*

#### Description

Applies all changes made during the current session and then executes the `logout` command. After you have changed one or more values for the property of a type, you need to commit those changes in order for those changes to be reflected on the server. Use the `commit` command to do this. Once you have run the `commit` command, you will automatically be logged out of the server.

#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **--biospassword=BIOSPASSWORD**

Select this flag to input a BIOS password. Include this flag if second-level BIOS authentication is needed for the command to execute.

- **--reboot=REBOOT**

Use this flag to perform a reboot command function after completion of operations. For help with parameters and descriptions regarding the reboot flag, run `help reboot`.

#### Inputs

None

#### Outputs

None

### Logout command

> Logout example commands:

> Use the logout command to end the session and disconnect from the server.

> ![Logout Example 1](images/examples/logout_ex1.png "Logout example 1")

> Here the logout flag was used to demonstrate that the server can be logged out of after another command. Here, after the **EmbSata1Enabled** property of **HpBios** was set to a new value, the server was logged out of because the logout flag was included.

> ![Logout Example 2](images/examples/logout_ex2.png "Logout example 2")


#### Syntax

logout *[Optional Parameters]*

#### Description

Use the `logout` command to exit your session and to disconnect from the server.

#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

#### Inputs

None

#### Outputs

None

### Exit command

> Exit example commands

> This command exits the interactive shell.

> ![Exit Example 1](images/examples/exit_ex1.png "Exit example 1")

#### Syntax

exit *[Optional Parameters]*

#### Description

Use the `exit` command if you wish to exit from the interactive shell. Using exit will also log you out and disconnect you from the server.

#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

#### Inputs

None

#### Outputs

None
