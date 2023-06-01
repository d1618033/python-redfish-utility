## Smart NIC Commands

The Smart NIC commands are designed for use with HPE Gen10 and later servers.

<aside class="notice">
<ul>
<li>A Smart NIC Capable controller capable of communicating with iLO is required.</li>
</ul>
</aside>

### Smartnic Command

> To list all available smart NICs run the command without arguments.

<pre>
ilorest > <span style="color: #01a982; ">smartnic</span>
------------------------------------------------
SmartNic Information
------------------------------------------------
System 2:
        Model: Pensando DSC25v2 10/25G 2p 32GB
        Manufacturer: HPE
        Name: Data Processing Unit
        Firmware Version:
        PowerState: On
        SerialNumber: 5UP135004C
        SystemType: DPU
        Health: Critical
        State: Disabled
        Operating System: Unknown  OS
        OS Version: Unknown
        Available SystemCapabilities:
        Enable SystemCapabilities:
        Integration Config: OsReadyTimeout: 300
        UUID: 1DD80000-0000-4000-8000-00AECDF624A0
</pre>

> To list all smartnics in json format and without any logo.

<pre>
ilorest > <span style="color: #01a982; ">smartnic -j --nologo</span>
{
  "SmartNic Information": {
    "System 2": {
      "Available SystemCapabilities": [],
      "Enable SystemCapabilities": [],
      "Firmware Version": "",
      "Health": "Critical",
      "Integration Config": {
        "OsReadyTimeout": 300
      },
      "Manufacturer": "HPE",
      "Name": "Data Processing Unit",
      "OS Version": "Unknown",
      "Operating System": "Unknown  OS",
      "PowerState": "On",
      "SerialNumber": "5UP135004C",
      "State": "Disabled",
      "SystemType": "DPU",
      "UUID": "1DD80000-0000-4000-8000-00AECDF624A0",
      "model": "Pensando DSC25v2 10/25G 2p 32GB"
    }
  }
}
</pre>

> To view the logs of particular smartnic.

<pre>
ilorest > <span style="color: #01a982; ">smartnic --id=2 --logs -j --nologo</span>
{
  "Logs View": {
    "Created": "2021-06-10T08:08:42Z",
    "DPU Log cleared by": " Administrator",
    "EntryType": "Oem",
    "Id": "1",
    "Name": "DPU Log",
    "Severity": "OK"
  }
}
</pre>

> To update FW of a particular smartnic.

<pre>
ilorest > <span style="color: #01a982; ">smartnic --id=2 --update_fw https://1.1.1.1/pensando.tar</span>
Uploading firmware: pensando.tar
Firmware update in progress
Firmware update in completed
</pre>

> To view the bootprogress of smartnic.

<pre>
ilorest > <span style="color: #01a982; ">smartnic --id=2 --bootprogress -j --nologo</span>
{
  "Boot Progress": {
    "Id": "2",
    "LastState": "OEM",
    "OemLastState": "Unknown"
  }
}
</pre>

> To reset the smartnic.

<pre>
iLOrest > <span style="color: #01a982; ">smartnic --id=2 --reset=GracefulRestart</span>
Graceful server restart. Note, the current session will be terminated.
Please wait for the server to boot completely before logging in again.
Rebooting the server in 3 seconds...
</pre>


<p class="fake_header">Syntax</p>

Smartnic *[Optional Parameters]*

<p class="fake_header">Description</p>

Discovers all smartnics installed in the server and managed by the SmartStorage.  

<p class="fake_header">Parameters</p>

- **-h, --help**

Including the help flag will display help for the command.

- **--id=ID**

Use this flag to select the corresponding smartnic.

- **-j**

Use this flag to print the smartnic info in json format.

- **--logs**

Use this flag to get the logs of specified smartnic.

- **--clearlog**

Use this flag to clear log of smartnic.

- **--bootprogress**

Use this flag to check the bootprogress.

- **--update_fw=FWPKG**

Use this flag to update the FW of smartnic.

- **--reset=GracefulShutdown/ForceRestart/Nmi/GracefulRestart**

Use this flag to reset the smart as specified above.

<p class="fake_header">Login Parameters</p>

The following parameters can be included to login to a server in the same line as the command is run.

- **--url=URL**

If you are not logged in yet, use the provided iLO URL along with the user and password flags to login to the server in the same command.

- **-u User, --user=USER**

If you are not logged in yet, including this flag along with the password and URL flags can be used to login to a server in the same command.

- **-p Password, --password=PASSWORD**

If you are not logged in yet, use this flag along with the user and URL flags to login. Use the provided iLO password corresponding to the username you gave to login.

- **--logout**

Optionally include the logout flag to log out of the server after this command is completed. Using this flag when not logged in will have no effect.

<p class="fake_header">Input</p>
None

<p class="fake_header">Output</p>
None
