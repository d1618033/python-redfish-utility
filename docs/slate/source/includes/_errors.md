# Error Codes

<aside class="notice">The error codes listed below are returned by the RESTful Interface Tool, not the managed server.</aside>

The RESTful Interface Tool uses the following error codes:

Error Code | Description
---------- | -------
1	| Error occurred while reading the configuration file. See the error message for details.
2	| Error occurred when user tried to invoke a command that isn't enabled.
3	| Invalid iLOrest command line syntax. Use the **-h** parameter for complete command line parameters.
4	| The input JSON file is in an invalid format.
5	| Windows User not admin.
6	| No contents found for operation.
7	| Invalid File input error.
8	| No changes made or found.
9	| No Valid info error.
10	| Error occurred while parsing user command line inputs. See the error message for details.
11	| Warning occurred during command line inputs parsing. See the error message for details.
12	| Invalid individual command usage. Use the **-h** parameter for individual command line parameters.
13	| Error occurred when user tries to invoke a command that doesn’t exist.
21	| Occurs when there are no clients active (usually when user hasn't logged in).
22	| Error occurred when attempting to operate on another instance while logged in.
23	| Error occurred when attempting to select an instance that does not exist.
24	| Error occurred when attempting to access an object type without first selecting it.
25	| Error occurred when attempting to access an object type without first selecting it while using filters.
26	| Error occurred when attempting to set an object type without first selecting it.
27	| Error occurred when selection argument fails to match anything.
28	| Error occurred when validating user input against schema files.
29	| RIS Missing ID token.
30	| RIS session expired.
31	| Error occurred when retry attempts to reach the selected server have been exhausted.
32	| Occurs when invalid iLO credentials have been provided.
33	| Error occurred when correct credentials have been provided and server is unresponsive.
34	| CHIF driver missing.
35	| CHIF missing DLL.
36	| Error occurred due to an unexpected response.
37	| Error occurred due to iLO error.
38	| Error occurred while trying to create BLOB.
39	| Error occurred while trying to read BLOB.
40	| Same settings error.
41	| Firmware update error.
42	| Boot order entry error.
43	| NIC missing or invalid error.
44	| No current session established.
45	| Failure during commit operation
51	| Multiple server configuration failure
52	| Multiple server input file error.
53	| Load skip setting error.
54	| Incompatible iLO version error.
55	| Invalid command list file error.
56	| Unable to mount BB error.
57	| Birthcertificate parse error.
58	| Incompatible server type.
59	| iLO license error.
60	| Account exists error. 
61	| Error occurred when trying to change a value.
62	| Reference path not found error.
63	| iLO response error.
64	| Unable to open a channel with iLO error.
65	| Error parsing schema. Try running with the “--latestschema flag”.
70	| Error occurred while trying to write BLOB.
71	| Error occurred while trying to delete BLOB.
72	| Error occurred while trying to finalize BLOB.
73	| BLOB could not be found.
74	| JSON decoder error.
75	| Security state error. 
76	| iLO RESTful API BLOB override error.
77	| Error occurred during the blob operation after maximum retries.
80	| Resource allocation errors. 
83	| The requested path is unavailable. 
100	| BIOS provider is unregistered. Please refer to the documentation for details on this issue.
101	| Failed to download component.
102	| Update service busy.
103	| Failed to upload component. 
255	| A general error occurred while manipulating server settings. See the error message for details.

<aside class="warning">You might encounter the following error message: <b>Missing token required for operation</b>. <b>Please add the proper token</b>. To resolve this error, add the BIOS password for the server when executing the commands.</aside>
