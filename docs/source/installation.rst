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

============
Installation
============

OpenPassPhrase API backend is written entirely in Python (v2.7). Thus, it can
theoretically be deployed on any platform with a modern Python interpreter.
However, at the moment it is only officially tested on Ubuntu and CentOS Linux
distributions. This guide presupposes the use of one of these platforms. More
platforms will probably be added in the future. In addition, the possibility
of deploying OpenPassPhrase on a PaaS hosted system such as
`Heroku <https://www.heroku.com/>`_ and `Google App Engine
<https://cloud.google.com/appengine/docs>`_ will be explored in the future.

Since the backend is intended to run as a web service, a Web Server Gateway
Interface (WSGI) server is typically required to route requests to the
application from the web server. Among the most popular WSGI servers are:

.. |mod_wsgi| raw:: html

    <a target="_blank"
    href="http://www.modwsgi.org">
    <img src="_static/weblink.ico"></a>

.. |gunicorn| raw:: html

    <a target="_blank"
    href="http://gunicorn.org/">
    <img src="_static/weblink.ico"></a>

.. |cherrypy| raw:: html

    <a target="_blank"
    href="http://cherrypy.org">
    <img src="_static/weblink.ico"></a>

.. |uwsgi| raw:: html

    <a target="_blank"
    href="http://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html">
    <img src="_static/weblink.ico"></a>

* **mod_wsgi** |mod_wsgi| - an Apache module that implements a WSGI compliant
    interface for hosting Python based web applications on top of the Apache
    web server.

* **Green Unicorn** |gunicorn| - a Python WSGI HTTP Server for UNIX. It’s a
    pre-fork worker model ported from Ruby’s Unicorn project. 

* **CherryPy** |cherrypy| - a pythonic, object-oriented HTTP framework, which
    includes a WSGI server.

* **uWSGI** |uwsgi| - a full stack for building hosting services, wchich
    includes a plugin for Python support.

This guide only covers deployment using **mod_wsgi**. Stay tuned for additional
deployment options in the future.

Deploying with mod_wsgi
~~~~~~~~~~~~~~~~~~~~~~~

The following steps assume an aptly configured Linux system with the following
minimal set of packages installed:

* *python (2.7)*
* *git*
* *virtualenv*
* *pip*
* *tox* (optional for running tests and doc builds)

Get the source code:
--------------------
::

    git clone https://github.com/openpassphrase/opp.git

A typical place to put the repository is in: ``/var/www/``, so that after
running above command, you will have the following path:

    ``/var/www/openpassphrase``

Setup the virtual environment:
-------------------------------
To avoid having to install all of the OpenPassPhrase dependencies system-wide,
it is advisable to use a virtual environment::

    cd /var/www/openpassphrase
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt

.. Note:: The ``venv/bin/activate`` is a bash shell script, if using csh or
   tcsh, use the ``venv/bin/activate.csh`` script.

Setup the database:
-------------------
OpenPassPhrase uses an RDBMS for storing data. It is currently only tested with
SQLite and MySQL databases, but others such as Postgresql, Oracle, MS-SQL,
Firebird, and Sybase may be used at user's discretion.

To setup the database run the provided utility::

    opp-db init

This tool will use the ``sql_connect`` config option to connect to the database
and create the schema. For more information refer to the :ref:`configuration`
section.

User management is also accomplished by the opp-db utility. This a deliberate
design decision not to expose user creation capabilities externally. To
add/delete users, run the following commands::

    opp-db add-user -u <username> -p <passsword>
    opp-db del-user -u <username> -p <passsword>

Configure mod_wsgi:
-------------------
Make sure the ``mod_wsgi`` Apache module is installed (e.g. ``yum install
mod_wsgi`` on CentOS or ``sudo apt-get install mod_wsgi`` on Ubuntu. Or
follow the `mod_wsgi Quick Installation Guide <https://modwsgi.readthedocs.io
/en/develop/user-guides/quick-installation-guide.html>`_ of the **mod_wsgi**
documentation.

The following is a sample Apache config file to enable routing of requests to
the OpenPassPhrase API::

    LoadModule wsgi_module <path/to/mod_wsgi.so>
    WSGISocketPrefix run/wsgi

    <VirtualHost *:443>
        ServerName <yourserver.com>
        SSLEngine on
        SSLHonorCipherOrder on
        SSLCipherSuite <colon-separated list of allowed and disallowed ciphers>
        SSLCertificateKeyFile "<path/to/your/private/key/file>"
        SSLCertificateFile "<path/to/your/certificate/file>"
        SSLCertificateChainFile "<path/to/your/certificate/chain/file>"

        WSGIScriptAlias <path/to/desired/root/url> <path/to/openpassphrase/repo/setup.wsgi>
        WSGIDaemonProcess <yourserver.com> processes=2 threads=15 display-name=%{GROUP}
        WSGIProcessGroup <yourserver.com>

        <Directory <path/to/openpassphrase/repo>
            Order deny,allow
            Allow from all
        </Directory>
    </VirtualHost>

.. Note:: The values inside the <> brackets must be set specifically for
   your environment. Also note the WSGIScriptAlias setting which points to
   ``setup.wsgi`` file, which resides in the top level of the repository.
   The contents of this file need to be altered based on your particular
   directory structure setup.

Place the above conf file in the Apache config directory (e.g.
``/etc/httpd/conf.d``) and restart your Apache server.
