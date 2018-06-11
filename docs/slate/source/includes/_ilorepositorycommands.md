## iLO Repository Commands

<aside class="notice">
The iLO repository commands are designed for use with HPE Gen10 servers.
</aside>



### Deletecomp command

> Deletecomp example commands:

> Delete a single component by URI.

> ![Deletecomp Example 1](images/examples/deletecomp_ex1.png "Deletecomp example 1")


> Delete multiple components by ID.

> ![Deletecomp Example 2](images/examples/deletecomp_ex2.png "Deletecomp example 2")


> Delete all components. 

> ![Deletecomp Example 3](images/examples/deletecomp_ex3.png "Deletecomp example 3")


#### Syntax

deletecomp *[Optional Parameters]*

#### Description

Deletes components/binaries from the iLO repository.


#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-a, --all**

Delete all components.


#### Inputs
None


#### Outputs
None


### Downloadcomp command

> Downloadcomp example commands:

> Run to download the file from path.

> ![Downloadcomp Example 1](images/examples/downloadcomp_ex3.png "Downloadcomp example 1")

<aside class="warning">The output directory and files in that directory must be set to writable.</aside>
<aside class="warning">Any file in the output directory with the same name as the downloading component will be overwritten.</aside>


#### Syntax

downloadcomp *[Component Path] [Optional Parameters]*

#### Description

Downloads components/binaries from the iLO repository.


#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--sessionid=SESSIONID**
                        
Optionally include this flag if you would prefer to connect using a session id instead of a normal login.

- **--includelogs**         

Optionally include logs in the data retrieval process.
- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. Using this flag when not logged in will have no effect.

- **outdir=OUTDIR**

output directory for saving the file.


#### Inputs
None


#### Outputs
None 


### Flashfwpkg command

> flashfwpkg example commands:

> Upload component and add a task to flash.

> ![Flashfwpkg Example 1](images/examples/fwpkg_ex1.png "Flashfwpkg example 1")

> Skip extra checks before adding taskqueue.

> ![Flashfwpkg Example 2](images/examples/fwpkg_ex2.png "Flashfwpkg example 2")

#### Syntax

flashfwpkg *[FWPKG PATH] [Optional Parameters]*

#### Description

Run to upload and flash fwpkg components using the iLO repository.


#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **--url=URL**

If you are not logged in yet , use this flag along with the provided iLO URL to login to the server.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use the provided iLO password corresponding to the username you gave to login.

- **--forceupload**

Include this flag to force upload firmware with the same name already on the repository.

- **--ignorechecks**

Include this flag to ignore all checks to the taskqueue before attempting to process the .fwpkg file. 


#### Inputs
None

#### Outputs
None


### Installset command

> Installset example commands:

> Add install set.

> ![Installset Example 1](images/examples/installset_ex1.png "Installset example 1")


>List install sets.

> ![Installset Example 2](images/examples/installset_ex2.png "Installset example 2")


> Delete install set.

> ![Installset Example 3](images/examples/installset_ex1.png "Installset example 3")

> Install sets can be added by either the complete JSON structure.

```
{
	"Name": "installset name",
	"Description": "installset description",
	"Sequence": [{
			"Name": "Wait",
			"UpdatableBy": ["RuntimeAgent"],
			"Command": "Wait",
			"WaitTimeSeconds": 60
		},
		{
			"Name": "uniqueName",
			"UpdatableBy": ["RuntimeAgent"],
			"Command": "ApplyUpdate",
			"Filename": "filename.exe"
		},
		{
			"Name": "uniqueName2",
			"UpdatableBy": ["Bmc"],
			"Command": "ApplyUpdate",
			"WaitTimeSeconds": 0,
			"Filename": "filename2.hex"
		},
		{
			"Name": "uniqueName3",
			"UpdatableBy": ["Uefi", "RuntimeAgent"],
			"Command": "ApplyUpdate",
			"WaitTimeSeconds": 0,
			"Filename": "filename3.x86_64.rpm"
		},
		{
			"Name": "Reboot",
			"UpdatableBy": ["RuntimeAgent"],
			"Command": "ResetServer"
		}
	],
	"IsRecovery": false
}
```

> Or a list of sequences. 

```
[
		{
			"Name": "Wait",
			"UpdatableBy": ["RuntimeAgent"],
			"Command": "Wait",
			"WaitTimeSeconds": 60
		},
		{
			"Name": "uniqueName",
			"UpdatableBy": ["RuntimeAgent"],
			"Command": "ApplyUpdate",
			"Filename": "filename.exe"
		},
		{
			"Name": "Reboot",
			"UpdatableBy": ["RuntimeAgent"],
			"Command": "ResetServer"
		}
]
```



#### Syntax

installset *[Optional Parameters]*

#### Description

Run to perform operations on install sets.


#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-n NAME, --name=NAME**

Install set name to create, remove, or invoke.

- **-r, --removeall**

Remove all install sets.

- **-j, --json**

Optional: Include this flag to change the displayed output to JSON format. Preserving the JSON data structure makes the information easier to parse.

- **--expire=EXAFTER**

Optional: Include this flag to set the expiry time for installset. ISO 8601 Redfish-style time string to be written after which iLO will automatically change state to Expired.

-**--startafter=SAFTER**

Optional: Insclude this flag to set the earliest execution time for installset. ISO 8601 Redfish-style time string to be used.

-**--	tpmover**

Use this flag if the server you are currently logged into has a TPM chip installed.

-**--updaterecoveryset**

If set then the components in the flash operations are used to replace matching contents in the Recovery Set.

-**--cleartaskqueue**

This option clears previous items in the task queue before the Install Set is invoked.

#### Inputs
None


#### Outputs
None 



### Listcomp command

> Listcomp example commands:

> Run to list the components of the currently logged in system.

> ![Listcomp Example 1](images/examples/listcomp_ex1.png "Listcomp example 1")


#### Syntax

listcomp *[Optional Parameters]*

#### Description

Run to list the components ofthe currently logged in system.


#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.


#### Inputs
None 


#### Outputs
None 


### Maintenancewindow command

> maintenancewindow example commands:

> Print the current maintenancewindows on the system.

> ![Maintenancewindow Example 1](images/examples/maintenancewindow_ex1.png "Maintenancewindow example 1")


> Create a new maintenance window with startup time 1998-11-21T00:00:00 and user defined expire time, name, and description.

> ![Maintenancewindow Example 2](images/examples/maintenancewindow_ex2.png "Maintenancewindow example 2")


> Delete maintenance windows by ID or name. 

> ![Maintenancewindow Example 3](images/examples/maintenancewindow_ex3.png "Maintenancewindow example 3")


#### Syntax

maintenancewindow *[Optional Parameters]*

#### Description

Run to add, remove, or delete maintenance windows from the iLO repository.


#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet , use this flag along with the provided iLO URL to login.

- **-j, --json**

Optional: Include this flag to change the displayed output to JSON format. Preserving the JSON data structure makes the information easier to parse.

- **-description=DESCRIPTION**

Optional: Include this flag to add a description to the maintenance window created by you.

- **-n NAME, --name=NAME**

Optional: Include this flag to name the maintenance window created by you. If a name is not specified, system will add a unique name.

- **-e EXPIRE, --expire=EXPIRE**

Optional: Include this flag to add the time a maintenance window expires.

#### Inputs
None


#### Outputs
None


### Makeinstallset command

> Makeinstallset example commands:

> Run without logging in for basic guidance on making an install set.

> ![Makeinstallset Example 1](images/examples/minstallset_ex1.png "Makeinstallset example 1")

> Run while logged into a system for guidance based on the current components on that system.

> ![Makeinstallset Example 2](images/examples/minstallset_ex2.png "Makeinstallset example 2")

#### Syntax

makeinstallset *[Optional Parameters]*

#### Description

Run to make installsets for iLO. 
If not logged into the server, the command will provide basic guidance on making an installset.
If logged into the server, the command will provide guidance based on the current components on the system.
<aside class="notice">When using this command on a logged in sever, for best results, make sure to upload the components before running this command.</aside>

#### Parameters

- **-h, --help**

Including the help flag on this command will display help.

- **-f FILENAME, --filename=FILENAME**

Include this flag to use a different filename than the default one. The default filename is myinstallset.json

#### Inputs
None


#### Outputs
None


### Taskqueue command

> Taskqueue example commands:

> Create new wait task for 60 secs.

> ![Taskqueue Example 1](images/examples/taskqueue_ex1.png "Taskqueue example 1")


> Create new component task.

> ![Taskqueue Example 2](images/examples/taskqueue_ex2.png "Taskqueue example 2")


> Print update task queue.

> ![Taskqueue Example 3](images/examples/taskqueue_ex3.png "Taskqueue example 3")


> Delete all tasks from update task queue.

> ![Taskqueue Example 4](images/examples/taskqueue_ex4.png "Taskqueue example 4")


#### Syntax

taskqueue *[Optional Parameters]*

#### Description

Run to add or remove tasks from the task queue. Added tasks are appended to the end of the queue.


#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **-r, --resetqueue**

Remove all update tasks in the queue.

- **-c, --cleanqueue**

Clean up all finished or errored tasks - leave pending.

#### Inputs
None 


#### Outputs
None 


### Uploadcomp command

> Uploadcomp example commands:

> Upload component to the iLO repository.

> ![Uploadcomp Example 1](images/examples/uploadcomp_ex2.png "Uploadcomp example 1")


#### Syntax

uploadcomp *[Optional Parameters]*

#### Description

Run to upload the component on to iLO repository.


#### Parameters

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--sessionid=SESSIONID**

Optionally include this flag if you would prefer to connect using a session id instead of a normal login.

- **--includelogs**

Optionally include logs in the data retrieval process.

- **-j, --json**

Optionally include this flag if you wish to change the displayed output to JSON format. Preserving the JSON data structure makes the information easier to parse.

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. Using this flag when not logged in will have no effect.

- **--component=COMPONENT**
  
Component or binary file path to upload to the update service.

- **--compsig=COMPONENTSIG**

Component signature file path needed by iLO to authenticate the component file. If not provided will try to find the signature file from component file path.

- **--forceupload**

Add this flag to force upload components with the same name already on the repository.

- **--update_repository**

If true uploads the component/binary on to the Repository, Default[True].

- **--update_target**

If true the uploaded component/binary will be flashed, Default[False].


#### Inputs
None 

#### Outputs
None 
