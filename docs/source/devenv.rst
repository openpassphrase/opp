..
      Copyright 2017 OpenPassPhrase
      All Rights Reserved.

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

Development Environment
=======================

**Welcome Contributors!**

This project is in the very early stages of development. Thus, the development
environment (not to mention the API and the documentation) is very fluid and
may change radically as more contributors join. Please bear that in mind when
starting out.

System setup
------------

The recommended development platform is Ubuntu Xenial. At a minimum, you
will need several packages in order to start development. There is a handy
`setup <dev/opp_setup.sh>`_ script that you may use to initialize your dev
system. Refer to the script for a full list of required and useful packages.

Repository
----------

.. |openpassphrase| raw:: html

       <a target="_blank" href="https://github.com/openpassphrase">
       OpenPassPhrase</a>

The code is managed with Git and lives in a GitHub repository under the
|OpenPassPhrase| ogranization:

    ``git@github.com:openpassphrase/opp.git``

All the code modules reside in the ``opp`` folder inside the repository. The
following PyPI packages are used inside the code to implement various
capabilities:

    - **config** - read and parse configuration files
    - **pycrypto** - encryption/decryption using AES cipher
    - **click** - command line option parsing
    - **SQLAlchemy** - ORM interface to RDBMS
    - **Flask** - web server request/response routing
    - **PyJWT** - JSON Web token implementation in Python
    - **testtools** - unit testing framework
    - **mock** - mocking framework for unit tests
    - **xkcdpass** - secure multiword passphrases

Additionally, the following packages are used to accomplish various tasks:

    - **tox** - virtual environment automation and task aggregation
    - **pytest** - run unit and functional tests
    - **pytest-cov** - code coverage plugin for pytest
    - **flake** - PEP8 source code checker
    - **Spinx** - python documentation generator from reStructuredText

Testing, etc...
---------------

The *tox* tool reads a *tox.ini* file which resides at the top level of the
repository and instructs tox on how to setup the various jobs.

To run syntax checker::

    tox -e pep8

To run tests::

    tox -e py27

To generate docs::

    tox -e docs

To have tox recreate the virtual environment from scratch, either ``rm -rf
.tox`` folder or use the -r flag in the tox command, e.g.: ``tox -r -e py27``.


Please refer to the :ref:`guidelines` section for information on how to get
your contributions merged, and to the :ref:`wishlist` section for ideas on
where to contribute.

**Happy Hacking!**
