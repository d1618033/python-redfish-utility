python-redfish-utility
==============
.. image:: https://travis-ci.org/HewlettPackard/python-redfish-utility.svg?branch=master
    :target: https://travis-ci.org/HewlettPackard/python-redfish-utility
.. image:: https://img.shields.io/github/release/HewlettPackard/python-redfish-utility.svg?maxAge=2592000
	:target: 
.. image:: https://img.shields.io/badge/license-Apache%202-blue.svg
	:target: https://raw.githubusercontent.com/HewlettPackard/python-redfish-utility/master/LICENSE
.. image:: https://img.shields.io/pypi/pyversions/python-redfish-utility.svg?maxAge=2592000
	:target: https://pypi.python.org/pypi/python-redfish-utility
.. image:: https://api.codacy.com/project/badge/Grade/1283adc3972d42b4a3ddb9b96660bc07
	:target: https://www.codacy.com/app/rexysmydog/python-redfish-utility?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=HewlettPackard/python-ilorest-library&amp;utm_campaign=Badge_Grade


.. contents:: :depth: 1

Description
----------

 The Redfish Utility is a command line interface that allows you to manage servers that take advantage of Redfish APIs. For this release of the utility, you can manage any server running a Redfish API. You can install the utility on your computer for remote use. In addition to using the utility manually to execute individual commands, you can create scripts to automate tasks.

Running the utility from command line
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

	python.exe rdmc.py
	
Building an executable from file source
~~~~~~~~~~~~~~~~~~~~~~~~~

 For this process you will need to install pyinstaller for python.

.. code-block:: console

	python.exe pyinstaller rdmc-pyinstaller-windows.spec

Requirements
----------
 No special requirements.

Usage
----------
 For further usage please refer to our slate documentation: `https://hewlettpackard.github.io/python-redfish-utility/ <https://hewlettpackard.github.io/python-redfish-utility/>`_

Contributing
----------

 1. Fork it!
 2. Create your feature branch: `git checkout -b my-new-feature`
 3. Commit your changes: `git commit -am 'Add some feature'`
 4. Push to the branch: `git push origin my-new-feature`
 5. Submit a pull request :D

History
----------

  * 01/12/2017: Initial Commit

License
----------

Copyright 2017 Hewlett Packard Enterprise Development LP

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Authors
----------

* [Jack Garcia](http://github.com/LumbaJack)
* [Matthew Kocurek](http://github.com/Yergidy)
* [Prithvi Subrahmanya](http://github.com/PrithviBS)
