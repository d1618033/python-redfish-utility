## iLO Repository Commands

The iLO repository commands are designed for use with HPE Gen10 servers. 



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

- **sessionid=SESSIONID**
                        
Optionally include this flag if you would prefer to connect using a session id instead of a normal login.

- **includelogs**         

Optionally include logs in the data retrieval process.
- **logout**

Optionally include the logout flag to log out of the server after this command is completed. Using this flag when not logged in will have no effect.

- **outdir=OUTDIR**

output directory for saving the file.


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

> Complete JSON strucuture.

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

> The list of Sequences. 

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


#### Inputs
None


#### Outputs
None 



### Listcomp command

> Listcomp example commands:

> Run to list the components ofthe currently logged in system.

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

- **sessionid=SESSIONID**

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



