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

OpenPassPhrase API backend is written entirely in Python 2.7. Thus, it can in
theory be deployed on any platform with a modern Python interpreter. However,
at the moment it is only officially tested on Ubuntu and CentOS Linux
distributions. This guide presupposes the use of one of these platforms. More
platforms will probably be added in the future. In addition, the possibility
of deploying OpenPassPhrase on a Platform as a Service (PaaS) hosted system
such as `Heroku <https://www.heroku.com/>`_ and `Google App Engine
<https://cloud.google.com/appengine/docs>`_

Since the backend is intended to run as a web service, a Web Server Gateway
Interface (WSGI) server is typically required to route requests to the
application from the web server. Among the most popular WSGI servers are:

.. |mod_wsgi| image:: _static/weblink.ico
   :target: http://www.modwsgi.org
.. |gunicorn| image:: _static/weblink.ico
   :target: http://gunicorn.org/
.. |cherrypy| image:: _static/weblink.ico
   :target: http://cherrypy.org
.. |uwsgi| image:: _static/weblink.ico
   :target: http://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html

* **mod_wsgi** |mod_wsgi| - an Apache module that implements a WSGI compliant
    interface for hosting Python based web applications on top of the Apache
    web server.

* **Green Unicorn** |gunicorn| - a Python WSGI HTTP Server for UNIX. It’s a
    pre-fork worker model ported from Ruby’s Unicorn project. 

* **CherryPy** |cherrypy| - a pythonic, object-oriented HTTP framework, which
    includes a WSGI server.

* **uWSGI** |uwsgi| - a full stack for building hosting services, wchich
    includes a plugin for Python support.

Current guide only covers deployment using mod_wsgi. Stay tuned for additional
deployment options in the future.

Deploying with mod_wsgi
~~~~~~~~~~~~~~~~~~~~~~~

The following steps assume an aptly configured Linux with the following minimal
set of packages installed:

* *python (2.7)*
* *git*
* *virtualenv*
* *pip*
* *tox* (optional for running tests and doc builds)

Get the source code:
--------------------
::

    git clone ssh://git@bashmak.com:7999/bg/openpassphrase.git

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

Configure mod_wsgi:
-------------------
Make sure the ``mod_wsgi`` Apache module is installed (e.g. ``yum install
mod_wsgi`` on CentOS or ``sudo apt-get install mod_wsgi`` on Ubuntu.

The following is a sample Apache config file to enable routing of requests to
to the OpenPassPhrase API::

    <VirtualHost *:443>
        ServerName bashmak.com
        SSLEngine on
        SSLCipherSuite RC4-SHA:AES128-SHA:HIGH:!aNULL:!MD5
        SSLHonorCipherOrder on
        SSLCertificateKeyFile "<path to your private key file>"
        SSLCertificateFile "<path to your certificate file>"
        SSLCertificateChainFile "<path to your certificate chain file>"

        WSGIScriptAlias <path to desired root url> /var/www/openpassphrase/setup.wsgi

        <Directory /var/www/openpassphrase>
            Order deny,allow
            Allow from all
        </Directory>
    </VirtualHost>

.. Note:: The values inside <> brackets must be set specifically for your
   environment.

Place the above conf file in the Apache config directory (e.g.
``/etc/httpd/conf.d``) and restart your Apache server.
