# Installation

## Requirements

The following is a list of requirements for the server you want to manage with the tool:

- Local management: Gen9 server with a Windows OS or Linux OS (64–bit) installed (If you want to install the tool locally on the server).
- Remote management: Gen9 server with or without an OS installed.
- iLO 4 2.00 or later.
- The install packages are available for download from [http://www.hpe.com/info/resttool](http://www.hpe.com/info/resttool).

### Updating the JSON schemas used by the RESTful Interface Tool

> Windows Directory

```

C:\Program Files\Hewlett Packard Enterprise\HP RESTful Interface Tool\

```

> Linux Directory

```

/usr/share/ilorest

```

If you are using iLO 2.10 or later and the RESTful Interface Tool 1.30 or later, the JSON schemas are automatically updated. If you are using an earlier version of iLO or an earlier version of the RESTful Interface Tool, you must manually get the latest JSON schemas from the SPP located in the `\hp_restful_api directory`. Copy the schema files to the appropriate directory:

### Installing the RESTful Interface Tool

The following installation steps describe how to install the tool in a Windows OS or Linux OS.
#### Windows
1. Download the RESTful Interface Tool (Windows MSI package) from [http://www.hpe.com/info/resttool](http://www.hpe.com/info/resttool).
2. Install the package on the server you prefer to manage for local management. For remote management, install the package on a laptop or server that has access to the managed server network.

#### Linux
1. Download the RESTful Interface Tool (Linux RPM package) from [http://www.hpe.com/info/resttool](http://www.hpe.com/info/resttool).
2. Install the installation package on the server you prefer to manage for local management. For remote management, install the package on a laptop or server that has access to the managed server network.

### Starting the RESTful Interface Tool

#### Windows
1. Click the Start menu.
2. Click **Hewlett Packard Enterprise** → **HPE RESTful Interface Tool**.
3. Right-click the **HPE RESTful Interface Tool** prompt, and then click **Run as Administrator**.

#### Linux
1. Open a terminal window.
2. To start interactive mode, run the command **/usr/sbin/ilorest** (using administrator privileges).

