

## HPE Scalable Persistent Memory commands

This section covers commands related to the configuration of Scalable Persistent Memory.

### Show Scalable Persistent Memory configuration command

> Example: Display the current Scalable Persistent Memory configuration.


```
iLOrest > showscalablepmemconfig

Overall Allocated Scalable Persistent Memory
--------------------------------------------

.----------------------------------------------------------.
|||||||||||||||||||                                        |
'----------------------------------------------------------'
250 GiB of 786 GiB allocated (536 GiB available)


Logical NVDIMMs
---------------

Size        Type               Location                Operation    
--------------------------------------------------------------------
  100 GiB   Single Processor   Processor 1, Index 1                 
  100 GiB   Single Processor   Processor 1, Index 2                 
   50 GiB   Single Processor   Processor 2, Index 1                 


```

> Example: Display the available Scalable Persistent Memory capacity.


```
iLOrest > showscalablepmemconfig --available

Available Scalable Persistent Memory
------------------------------------
Available capacity to create logical NVDIMMs is constrained by the system
hardware, including the number of backup storage devices selected.

By Processor (for single processor logical NVDIMMs):

Processor    Available For Scalable PMEM             
-----------------------------------------------------
  1             536 GiB (Max logical NVDIMMs created)
  2             536 GiB 

By Processor Pair (for spanned logical NVDIMMs):

Processors   Available For Scalable PMEM             
-----------------------------------------------------
  1,2           536 GiB 


```

#### Syntax


showscalablepmemconfig *[--available] [--json]*


#### Description

- Displays overall Scalable Persistent Memory configuration summary.
- Displays the logical NVDIMMs.
- Displays the available Scalable Persistent Memory capacity.
- Indicates if pending operations exist that require a reboot.

#### Parameters


- **-a, --available**

Show the available capacity per processor or processor pair.

- **-j, --json**

Optionally include this flag to change the output to JSON format.



### Enable Scalable Persistent Memory configuration command

> Example: Enable Scalable Persistent Memory functionality.


```
iLOrest > enablescalablepmem

The Scalable Persistent Memory feature has been set to: Enabled


```

#### Syntax


enablescalablepmem *[--disable]*


#### Description

- Enable or disable the Scalable Persistent Memory feature.
- Scalable Persistent Memory must be enabled before configuration is allowed.

#### Parameters

If no parameters are specified, the Scalable Persistent Memory feature will be enabled.


- **--off, --no, --disable**

Disable the Scalable Persistent Memory feature. Warning: any pending configuration changes will be lost.



### Show Backup Devices command

> Example: Display the supported Scalable Persistent Memory backup devices.


```
iLOrest > showbackupdevices

Scalable Persistent Memory Backup Storage Devices
-------------------------------------------------

ID     Location        Model        Type       Size    Status   Life PMEM Use  Operation           
---------------------------------------------------------------------------------------------------
2@1    Box 2 Bay 1     MO0800KEFHP  SSD (NVMe) 800 GB  OK       99%    Yes                         
2@2    Box 2 Bay 2     MO0800KEFHP  SSD (NVMe) 800 GB  OK       100%   Yes                         
3@3    Box 3 Bay 3     MO0800KEFHP  SSD (NVMe) 800 GB  OK       98%                                
3@4    Box 3 Bay 4     MO0800KEFHP  SSD (NVMe) 800 GB  OK       99%                                

Scalable Persistent Memory supported: 786 GiB


```

#### Syntax


showbackupdevices


#### Description

- Displays all devices that are supported for use as Scalable Persistent Memory backup storage.
- Indicates if a device is currently in use for Scalable Persistent Memory, is being added, or is being removed.
- Reports the amount of Scalable Persistent Memory that is supported by the configuration.
- Drives are identified by Box and Bay.
- Use this command to identify drives to use with the `setbackupdevices` command.

#### Parameters


None




### Set Backup Devices command

> Example: Set the backup devices 2@1 and 2@2


```
iLOrest > setbackupdevices --device=2@1 --device=2@2

ID     Location        Model        Type       Size    Status   Life PMEM Use  Operation           
---------------------------------------------------------------------------------------------------
2@1    Box 2 Bay 1     MO0800KEFHP  SSD (NVMe) 800 GB  OK       99%            Add,Initialize      
2@2    Box 2 Bay 2     MO0800KEFHP  SSD (NVMe) 800 GB  OK       100%           Add,Initialize      
3@3    Box 3 Bay 3     MO0800KEFHP  SSD (NVMe) 800 GB  OK       98%                                
3@4    Box 3 Bay 4     MO0800KEFHP  SSD (NVMe) 800 GB  OK       99%                                

Scalable Persistent Memory supported: 786 GiB


*** The pending configuration operations require a restart to take effect ***

```

#### Syntax


setbackupdevices *(--device=ID... | --remove-all)*


#### Description

- Configures the specified devices for use as Scalable Persistent Memory backup storage
- Backup devices are not allowed to be removed while logical NVDIMMs exist
- The device IDs can be obtained from the `showbackupdevices` command


#### Parameters


- **--device=ID, --drive=ID**

ID of the backup device to set, e.g. '1@1'

- **--remove-all**

Remove all currently-configured backup devices





### Create Logical NVDIMM command

> Example: Create a 100 GiB logical NVDIMM on processor 1


```
iLOrest > createlogicalnvdimm --processor=1 --size=100

Size        Type               Location                Operation    
--------------------------------------------------------------------
  100 GiB   Single Processor   Processor 1, Index 1    Create       


*** The pending configuration operations require a restart to take effect ***


```

> Example: Create a 100 GiB spanned logical NVDIMM on processors 1 and 2.


```
iLOrest > createlogicalnvdimm --processors=1,2 --size=100

Size        Type               Location                Operation    
--------------------------------------------------------------------
  100 GiB   Spanned            Processors 1,2          Create       
  100 GiB   Single Processor   Processor 1, Index 1    Create       


*** The pending configuration operations require a restart to take effect ***


```

#### Syntax


createlogicalnvdimm *--size=SIZE [--processor=NUMBER | --pair=PAIR]*


#### Description

- Create a logical NVDIMM.
- If only `--size` is specified, the command automatically creates a single processor or spanned logical NVDIMM based on the size requested.
- Two logical NVDIMMs may be created per processor.
- One spanned logical NVDIMM may be created for processors 1 and 2.

#### Parameters


- **--size=SIZE**

Specify the size (GiB) of the logical NVDIMM to create.

- **--proc=NUMBER, --processor=NUMBER**

Use to create a logical NVDIMM. Specify the processor (auto, 1, 2).

- **--pair=PAIR, --processors=PAIR**

Use to create a spanned logical NVDIMM. Specify the pair of processors (auto or 1,2).





### Remove Logical NVDIMM command

> Example: Remove a logical NVDIMM on processor 1, index 1.


```
iLOrest > removelogicalnvdimm --processor=1 --index=1

Size        Type               Location                Operation    
--------------------------------------------------------------------
  128 GiB   Single Processor   Processor 1, Index 1    Remove       


*** WARNING ***

The pending configuration operations require a restart to take effect.

All backup storage devices will be initialized during restart.
Data on any existing logical NVDIMMs will be lost.

The pending configuration changes can be discarded by running:

     revertscalablepmemconfig

*** Any data that needs to be preserved should be backed up before restarting ***

```

> Example: Remove a spanned logical NVDIMM from processors 1 and 2.


```
iLOrest > removelogicalnvdimm --processors=1,2

Size        Type               Location                Operation    
--------------------------------------------------------------------
  100 GiB   Spanned            Processors 1,2          Remove       


*** WARNING ***

The pending configuration operations require a restart to take effect.

All backup storage devices will be initialized during restart.
Data on any existing logical NVDIMMs will be lost.

The pending configuration changes can be discarded by running:

     revertscalablepmemconfig

*** Any data that needs to be preserved should be backed up before restarting ***

```

#### Syntax


removelogicalnvdimm *(--processor=NUMBER --index=INDEX | --pair=PAIR)*


#### Description

- Remove an existing logical NVDIMM.
- This operation causes the data stored on the NVDIMM to be lost. Back up all necessary data first.
- Obtain information about existing logical NVDIMMs using `showscalablepmemconfig`.

#### Parameters


- **--proc=NUMBER, --processor=NUMBER**

Specify the processor number of the logical NVDIMM to remove (1, 2).

- **-i INDEX, --index=INDEX**

Specify the index of the logical NVDIMM to remove (use with --processor).

- **--pair=PAIR, --processors=PAIR**

Specify the pair of processors of the spanned logical NVDIMM to remove (1,2)





### Revert Scalable Persistent Memory configuration command

> Example: Remove a logical NVDIMM and revert the changes.


```
iLOrest > removelogicalnvdimm --processor=1 --index=1

Size        Type               Location                Operation    
--------------------------------------------------------------------
  128 GiB   Single Processor   Processor 1, Index 1    Remove       


*** WARNING ***

The pending configuration operations require a restart to take effect.

All backup storage devices are initialized during restart.
Data on any existing logical NVDIMMs will be lost.

The pending configuration changes can be discarded by running:

     revertscalablepmemconfig

*** Any data that needs to be preserved should be backed up before restarting ***

```


```
iLOrest > revertscalablepmemconfig

Logical NVDIMMs
---------------

Size        Type               Location                Operation    
--------------------------------------------------------------------
  128 GiB   Single Processor   Processor 1, Index 1                 

Scalable Persistent Memory Backup Storage Devices
-------------------------------------------------

ID     Location        Model        Type       Size    Status   Life PMEM Use  Operation           
---------------------------------------------------------------------------------------------------
2@1    Box 2 Bay 1     MO0800KEFHP  SSD (NVMe) 800 GB  OK       99%    Yes                         
2@2    Box 2 Bay 2     MO0800KEFHP  SSD (NVMe) 800 GB  OK       100%   Yes                         
3@3    Box 3 Bay 3     MO0800KEFHP  SSD (NVMe) 800 GB  OK       98%                                
3@4    Box 3 Bay 4     MO0800KEFHP  SSD (NVMe) 800 GB  OK       99%                                

Scalable Persistent Memory supported: 786 GiB



```

#### Syntax


revertscalablepmemconfig


#### Description

- Revert any pending Scalable Persistent Memory configuration changes so the changes are not applied during restart.

#### Parameters


None





### Replace Backup Device command

> Example: Replace a backup device (existing device 2@1 with new device 2@2).


```
iLOrest > replacebackupdevice 2@1 2@2

ID     Location        Model        Type       Size    Status   Life PMEM Use  Operation           
---------------------------------------------------------------------------------------------------
2@1    Box 2 Bay 1     MO0800KEFHP  SSD (NVMe) 800 GB  OK       99%            Remove,Initialize   
2@2    Box 2 Bay 2     MO0800KEFHP  SSD (NVMe) 800 GB  OK       100%           Add,Initialize      
3@3    Box 3 Bay 3     MO0800KEFHP  SSD (NVMe) 800 GB  OK       98%                                
3@4    Box 3 Bay 4     MO0800KEFHP  SSD (NVMe) 800 GB  OK       99%                                

Scalable Persistent Memory supported: 393 GiB


*** The pending configuration operations require a restart to take effect ***

```

#### Syntax


replacebackupdevice *OLD-ID NEW-ID*


#### Description

- Replace a backup storage device for Scalable Persistent Memory.
- Specify devices by ID from the `showbackupdevices` command.

<aside class="notice">Caution: This operation initializes all backup storage devices. Data on any existing logical NVDIMMs will be lost. Back up all data first.</aside>

#### Parameters

- **OLD-ID**

ID of the original (in-use) backup device to replace, e.g. '1@1'

- **NEW-ID**

The new backup device to use as a replacement, e.g. '2@1'






### Auto Select Backup Devices command

> Example: Simulate the selection of backup storage devices to support 900 GiB of Scalable Persistent Memory:


```
iLOrest > autoselectbackupdevices --size=900

The following backup devices have been automatically selected for Scalable PMEM:
[1] Box 2 Bay 1     (800 GB)
[2] Box 2 Bay 2     (800 GB)
[3] Box 3 Bay 3     (800 GB)

```

> Example: Auto-select enough backup storage devices to support 1024 GiB of Scalable Persistent Memory.


```
iLOrest > autoselectbackupdevices --size=1024 --confirm

The following backup devices have been automatically selected for Scalable PMEM:
[1] Box 2 Bay 1     (800 GB)
[2] Box 2 Bay 2     (800 GB)
[3] Box 3 Bay 3     (800 GB)


ID     Location        Model        Type       Size    Status   Life PMEM Use  Operation           
---------------------------------------------------------------------------------------------------
2@1    Box 2 Bay 1     MO0800KEFHP  SSD (NVMe) 800 GB  OK       99%            Add,Initialize      
2@2    Box 2 Bay 2     MO0800KEFHP  SSD (NVMe) 800 GB  OK       100%           Add,Initialize      
3@3    Box 3 Bay 3     MO0800KEFHP  SSD (NVMe) 800 GB  OK       98%            Add,Initialize      
3@4    Box 3 Bay 4     MO0800KEFHP  SSD (NVMe) 800 GB  OK       99%                                

Scalable Persistent Memory supported: 1180 GiB


*** The pending configuration operations require a restart to take effect ***

```

#### Syntax


autoselectbackupdevices *--size=SIZE [--confirm]*


#### Description

- Automatically select the correct number of backup storage devices necessary for the desired amount of Scalable Persistent Memory.
- Only works if no logical NVDIMMs have been created and no backup devices have been configured.

<aside class="notice">Caution: using the `--confirm` flag will automatically change the device operation mode. All backup storage devices will be initialized. Back up all data first.</aside>

#### Parameters


- **-s SIZE, --size=SIZE**

Amount (in GiB) of Scalable Persistent Memory to be supported by the new backup storage device configuration.

- **--confirm**

Confirm the configuration of the automatically selected backup devices. If not specified, no changes will occur.


