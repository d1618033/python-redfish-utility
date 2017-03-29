# Using the RESTful Interface Tool

## RESTful Interface Tool Modes of operation

The RESTful Interface Tool has three modes of operation. By default, the interactive mode is utilized when you start the RESTful Interface Tool. With Scriptable Mode, you can use a script that gives commands to the RESTful Interface Tool. File-Based mode allows you to use a script that gives commands to the RESTful Interface Tool and use a file to load and save settings.

### Interactive mode

Interactive mode is started when you run the RESTful Interface Tool without any command line parameters. The `ilorest>` prompt is displayed and you can enter commands one at a time. You can exit the interactive mode by entering the `exit` command at the prompt. On Windows systems, double-click `ilorest.exe` to start an interactive session. You must be an administrator to run `ilorest.exe`.

![Interactive Mode](images/InteractiveMode_1.png "Interactive Mode")

### Scriptable mode

> The following script can be called to retrieve information regarding the **HpBios** type:

```
:: This is a batch file that logs into a remote server,
:: selects the HpBios type, and gets the BootMode value

:: Usage :: 
:: selectget.bat [URI] [USERNAME] [PASSWORD] 
@echo off

set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% LSS 3 goto :failCondition
goto :main

:failCondition
@echo Usage:
@echo selectget.bat [URI] [USERNAME] [PASSWORD]
goto :EOF

:main
@echo *****************************************
@echo ************* Logging in... *************
@echo *****************************************
ilorest.exe login %1 -u %2 -p %3
@echo *****************************************
@echo ******* selecting HpBios type... ********
@echo *****************************************
ilorest.exe select HpBios.
@echo *****************************************
@echo ********** getting BootMode... **********
@echo *****************************************
ilorest.exe get BootMode
pause
```

Scriptable mode is used if you want to script all the commands with the use of an external input file. The script contains a list of the RESTful Interface Tool command lines that let users get and set properties of server objects.

In this example, first the `HpBios` type is selected, and then the **get** command is used to retrieve information about the `BootMode` property of `HpBios`

### File-based mode

> The following script allows you to save, edit, and load a file to the server.

```
:: This a file-based edit mode helper for RESTful Interface Tool
:: 1. Run to download selected type to a file called ilorest.json
:: 2. Edit the ilorest.json file to make changes.
:: 3. Press any key running batch program to continue with program,
::    uploading the newly edited program to the server.

:: Usage ::
:: saveload.bat [SELECTOR] [FILENAME]
:: Specify a type with the SELECTOR tag, and
:: save to a file called FILENAME
@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% LSS 2 goto :failCondition
goto :main

:failCondition
@echo Usage:
@echo saveload.bat [SELECTOR] [FILENAME]
@echo specify a type with the SELECTOR tag, and
@echo save to a file called FILENAME
goto :EOF

:main
ilorest.exe login
ilorest.exe save --selector=%1 --json -f %2
@echo Edit the file, then:
pause
ilorest.exe load -f %2

```

File-based mode allows you to save and load settings from a file. This is similar to the `conrep.dat` files used by CONREP. File-based mode supports the JSON format.

When the example script is run, the following result is produced:

![File Mode example](images/FileBasedMode_1.png "File Based Mode example")

Here, the `HpBios` type is saved to a file called `ilorest1.json`. Then, after you modify any properties, the **load** command is used to make these changes on the server. 

The properties of `HpBios` can be edited here, and then loaded on the server. When the file is loaded on the server, changes to read-only values are not reflected. The full list in this example is truncated to save space.

> After saving this configuration, the **ilorest1.json** file looks like this:

```
{
	{
		"Comments":{
			"Manufacturer": "HP",
			"Model": "ProLiant DL360 Gen9",
			"BIOSFamily": "P89",
			"BIOSDate": "05/03/2015"
		}
	},
	{
		"HpBios.1.2.0": {
			"/rest/v1/systems/1/bios/Settings": {
				"AcpiRootBridgePxm": "Enabled",
				"AcpiSlit": "Enabled",
				"AdminName": "Jean Kranz",
				...
				"WakeOnLan": "Enabled"
			}
		}
	}
}
```

## Configuration file (ilorest.conf)

> Windows default configuration file

```
[ilorest]
#iLOrest reads the following environment variables, and applies them at runtime.  
#Note that they can be overridden by command line switches.

#####          Log Settings          #####
##########################################
# directory where iLOrest writes its log file
# logdir = .\ilorest_logs

#####         Cache Settings         #####
##########################################
# option to disable caching of all data
# cache = False

#####       Credential Settings      #####
##########################################
# option to use the provided url to login
# url = https://127.0.0.1

# option to use the provided username to login
# username = admin

# option to use the provided password to login
# password = password

#####         Commit Settings        #####
##########################################
# flag to commit in all places where applicable
# commit = True

#####    Output Default Settings     #####
##########################################
# flag to change output format in all places where applicable
# format = json

#####    Schema Default Settings     #####
##########################################
# directory where iLOrest will look for ilo schemas
# iloschemadir = .\

# directory where iLOrest will look for bios schemas
# biosschemadir = .\

#####  Default Save/Load Settings    #####
##########################################
# option to set default save output file
# savefile = ilorest.json

# option to set default load input file
# loadfile = ilorest.json
```

> Linux default configuration file

```
[iLOrest]
#iLOrest reads the following environment variables, and applies them at runtime.  
#Note that they can be overridden by command line switches.

#####          Log Settings          #####
##########################################
# directory where iLOrest writes its log file
# logdir = /var/log/ilorest/

#####         Cache Settings         #####
##########################################
# option to disable caching of all data
# cache = False

#####       Credential Settings      #####
##########################################
# option to use the provided url to login
# url = https://127.0.0.1

# option to use the provided username to login
# username = admin

# option to use the provided password to login
# password = password

#####         Commit Settings        #####
##########################################
# flag to commit in all places where applicable
# commit = True

#####    Output Default Settings     #####
##########################################
# flag to change output format in all places where applicable
# format = json

#####    Schema Default Settings     #####
##########################################
# directory where iLOrest will look for ilo schemas
# iloschemadir = /usr/share/ilorest/

# directory where iLOrest will look for bios schemas
# biosschemadir = /usr/share/ilorest/

#####  Default Save/Load Settings    #####
##########################################
# option to set default save output file
# savefile = ilorest.json

# option to set default load input file
# loadfile = ilorest.json
```

The configuration file contains the default settings for the tool. You can use a text editor to change the behavior of the tool such as adding a server IP address, username, and password. The settings that you added or updated in the configuration file are automatically loaded each time you start the tool. 

Configuration file locations:

- Windows OS: The same location as the executable file that starts the tool.
- Linux OS: `/etc/ilorest/ilorest.conf`
