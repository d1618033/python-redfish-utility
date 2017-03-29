## Raw commands

These are the raw HTTP RESTful operations that can be used through the RESTful Interface Tool. The commands and their examples that can be found in this section include the equivalents of HTTP RESTful **PATCH, GET, POST, PUT, DELETE**, and **HEAD**.

### RawPatch command

> RawPatch example commands:

> Here, the **AdminName** of type **HpBios** was "" before. The rawpatch command sent the patch.json to change that property to become **Jean Kranz**. Commit is left out deliberately here since, raw commands (such as rawpost, rawput, etc.) do not require the commit command to be run since changes are made directly. Note that this particular change required second-level BIOS authentication, which is why the biospassword flag was included.

```
ilorest > get AdminName –u username –p password --url=xx.xx.xx.xx –-selector=HpBios.
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext
AdminName=""
ilorest > rawpatch patch.json --biospassword=BIOSPASSWORD
One or more properties were changed and will not take effect until system is reset.
ilorest > logout
Logging session out.
ilorest > get AdminName --selector=HpBios. -u username -p password --url=xx.xx.xx.xx
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext
AdminName=Jean Kranz
```

> The following **patch.json** file was used in the above example:

```json
{
    "path": "/rest/v1/systems/1/bios/Settings",
    "body": {
        "AdminName": "Jean Kranz"
    }
}
```



#### Syntax

rawpatch *[Filename] [Optional Parameters]*

#### Description

Use this command to perform an HTTP RESTful Patch command. Run to send a patch from the data in the input file.

#### Parameters

> Filename parameter example:

```json
{
	"path": "/rest/v1/systems/1/bios/Settings",
	"body": {
		"AdminName": "Jean Kranz"
	}
}
```

- **Filename**

Include the filename to use the data in the input file to send the patch. See the example JSON file that can be used to rawpatch on the side.

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

- **--providerid=PROVIDERID**

Use to pass in the provider ID header.

- **--service**

Use this flag to enable service mode and increase the function speed.

#### Inputs

File

Input the file containing the JSON information you wish to use for the HTTP RESTful PATCH command.

#### Outputs

None

### RawGet command

> RawGet example commands:

> **Above:** The rawget command here executed the GET command on the path **/rest/v1/systems/1/bios/Settings**. This displays the information in the given path. Note that the full list of information has been truncated here for space.

```
ilorest > rawget "/rest/v1/systems/1/bios/Settings" –u username –p password --url=xx.xx.xx.xx
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext

The operation completed successfully.
{
  "MemFastTraining": "Enabled",
  "NvDimmSanitize": "Disabled",
   …
  "TpmState": "NotPresent",
  "CollabPowerControl": "Enabled"
} 
```



```
ilorest > rawget "/rest/v1/systems/1/bios/Settings" –u username –p password --url=xx.xx.xx.xx --filename=output.json
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext
The operation completed successfully.
Results written out to 'output.json'.
```

#### Syntax

rawget *[Path] [Optional Parameters]*

#### Description

Use this command to perform an HTTP RESTful GET command. Run to retrieve data from the passed in path.

#### Parameters

- **Path**

Pass the path to the `rawget` command to point it at a location.

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

- **--providerid=PROVIDERID**

Use to pass in the provider ID header.

- **--service**

Use this flag to enable service mode and increase the function speed.

#### Inputs

None

#### Outputs

File

If you include the `filename` flag, this command will return an output file of the information retrieved when the `rawget` command was executed.

### RawPost command

> RawPost example commands:

> The rawpost command performs an HTTP REST POST operation using the information provided in the provided file. Here the ForceRestart ResetType was set, so after the rawpost posted the changes iLO executed a ForceRestart. Note that if a full path is not given, the tool will search for the file in the location the RESTful Interface Tool is started in.

```
ilorest > rawpost forcerestart.json -u username -p password --url=xx.xx.xx.xx
The operation completed successfully.
```

> The following **forcerestart.json** file is used in conjuncture:

```json
{
     "path": "/rest/v1/Systems/1",
     "body": {
         "Action": "Reset",
         "ResetType": "ForceRestart"
     }
 }
```



#### Syntax

rawpost *[Filename] [Optional Parameters]*

#### Description

Use this command to perform an HTTP RESTful POST command. Run to post the data from the passed in path.

#### Parameters

> Example Filename parameter JSON file below:

```json
{
     "path": "/rest/v1/Systems/1",
     "body": {
         "Action": "Reset",
         "ResetType": "ForceRestart"
     }
 }
```

- **Filename**

Include the filename to send a post from the data included in this input file. An example JSON file is shown on the side:

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

- **--providerid=PROVIDERID**

Use to pass in the provider ID header.

- **--service**

Use this flag to enable service mode and increase the function speed.

#### Inputs

File

Input the file containing the JSON information you wish to use for the HTTP RESTful PUT command.

#### Outputs

None

### RawPut command

> RawPut example commands:

> **Above:** Here the rawput command was used to put the above put.json file to the server. Use the biospassword flag if the resource you are trying to modify requires second-level BIOS authentication to modify.

```
ilorest > rawput put.json –u username –p password –-url=xx.xx.xx.xx –biospassword=BIOSPASSWORD
One or more properties were changed and will not take effect until system is reset.
```

> This example uses the following **put.json** file:

```
{
    "path": "/rest/v1/Systems/1/bios/Settings",
    "body":{
        "BaseConfig": "default"
    }
}
```

#### Syntax

rawput *[Filename] [Optional Parameters]*

#### Description

Use this command to perform an HTTP RESTful PUT command. Run to retrieve data from the passed in path.

#### Parameters

> Example input file below:

```json
{	
    "path": "/rest/v1/Systems/1/bios/Settings",
    "body":{	
        "BaseConfig": "default"
    }
}
```

- **Filename**

Include the filename to send a PUT from the data included in this input file. Example Input file shown on the side:

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

- **--providerid=PROVIDERID**

Use to pass in the provider ID header.

- **--service**

Use this flag to enable service mode and increase the function speed.

#### Inputs

File

Input the file containing the JSON information you wish to use for the HTTP RESTful PUT command.

#### Outputs

None

### RawDelete command

> RawDelete example commands:

> Here the rawdelete command was used to delete a session. After the server was logged into, the provided session was deleted.

```
ilorest > login xx.xx.xx.xx –u username –p password
Discovering data from iLO...Done
WARNING: Cache is activated session keys are stored in plaintext
ilorest > rawdelete "/rest/v1/Sessions/admin556dba8328b43959"
The operation completed successfully.
```


#### Syntax

rawdelete *[Path] [Optional Parameters]*

#### Description

Use this command to perform an HTTP RESTful DELETE command. Run to delete data from the passed in path.

#### Parameters

- **Path**

Pass in the path to point the HTTP RESTful DELETE command.

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--providerid=PROVIDERID**

Use to pass in the provider ID header.

- **--sessionid=SESSIONID**

Optionally include this flag if you would prefer to connect using a session id instead of a normal login.

- **--service**

Use this flag to enable service mode and increase the function speed.

#### Inputs

None

#### Outputs

None

### RawHead command

> RawHead example commands:

> The rawhead command is the HTTP RESTful HEAD operation. It is used to retrieve the data from the passed in path.

```
ilorest > rawhead /rest/v1/systems/1/bios/Settings -u username -p password --url=xx.xx.xx.xx
[200] No message returned by iLO.
{
  "Content-length": "3835",
  "Server": "HP-iLO-Server/1.30",
  "Connection": "keep-alive",
  "ETag": "BB642DA122E434087C3E7E7A646A8DAB",
  "Allow": "GET, HEAD, PUT, PATCH",
  "Cache-Control": "no-cache",
  "Date": "Mon, 01 Jun 2015 14:51:07 GMT",
  "X_HP-CHRP-Service-Version": "1.0.3",
  "Content-type": "application/json"
}
```


#### Syntax

rawhead [Path] [Optional Parameters]

#### Description

Use this command to perform an HTTP RESTful HEAD command. Run to retrieve header data from the passed in path.

#### Syntax

- **Path**

Pass in the path to point the HTTP RESTful HEAD command.

- **-h, --help**

Including the help flag on this command will display help on the usage of this command.

- **-f, --filename=Filename**

Include the filename to perform the current operation.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to log into a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **--service**

Use this flag to enable service mode and increase the function speed.

#### Inputs

None

#### Outputs

File

If you specify the `filename` flag, the `rawhead` command will output a file containing the information retrieved when performing the `rawhead` command.


