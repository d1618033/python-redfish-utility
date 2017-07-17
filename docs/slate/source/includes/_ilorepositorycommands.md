## iLO Repository Commands



### Component command

> Component example commands:


#### Syntax

component *[Optional Parameters]*

#### Description



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



#### Outputs


### Downloadcomp command

> Downloadcomp example commands:


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

Optionally include the logout flag to log out of the server after this command is completed. Using this flag when not logged in will have no effect

- **outdir=OUTDIR**

output directory for saving the file.


#### Inputs



#### Outputs



### Installset command

> Installset example commands:


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



#### Outputs



### Listcomp command

> Listcomp example commands:


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



#### Outputs

### Taskqueue command

> Taskqueue example commands:


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



#### Outputs


### Uploadcomp command

> Uploadcomp example commands:


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



#### Outputs



