# Known Issues

The following are known issues present in the current release of ilorest. If available, a link to the relevant CA has been included:

Issue | CA | Issue Description  | Workaround
---------- |---------- |---------- |---------- 
--ilossa option in serverclone command is not yet supported.|NA |Smartarray cloning is not yet supported by serverclone command.|Smartarray has to be created using createlogicaldrive.
Chif login error out in SLES 12 SP4. |[SID7946](https://si.its.hpecorp.net/si/?ObjectType=52&Object=SID7946).| Logging into iLO in SLES 12SP4 may error out. | Use remote or vnic login.
Certificate login in ESXi 7.0 does not work.|NA| On ESXi 7.0 server, user certificate login does not work.| Use remote login or user credentials login.
Updating recovery set on SLES 12 SP5 may fail with iLOInitialError.|[SID7996](https://si.its.hpecorp.net/si/?ObjectType=52&Object=SID7996).|On SLES 12 SP5, iLOInitialError may occur when trying to update recovery set FW.| Use remote or vnic login or GUI to update the recovery set.
Directory group clone does not work with serverclone command.|NA |Serverclone save, create a directory grp, serverclone load to old config and directory group is not erased.|Directory Groups need to be manually created/erased.
smartnic --id 2 --reset may not work|NA |This may happen due to post request not sent to iLO|Use rawpost command to reset the smartnic.
smartnic --id 2 --bootprogress and --logs may not work without -j option|NA |This may happen due to an error in code|Always use -j option if --bootprogress and --logs are used.
