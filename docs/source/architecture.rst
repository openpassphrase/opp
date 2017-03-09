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

.. _architecture:

Architecture
=============

At its most basic level, OpenPassPhrase is a data storage service. All the
other details are just bells and whistles for securing and retrieving that
data. Therefore, it is best to begin by describing what is actually being
stored.

The below diagram shows the very simple entity-relationship schema used
by OpenPassPhrase. Of interest, are the fields with an * next to their
name. These are always stored in encrypted form and are never in clear
text except when decrypted in RAM for transmission over TLS. The fields
in the *items* table are likely to change or expand as more usage cases
arise.

.. figure:: _static/erd.png
   :figwidth: 100%
   :align: center

.. centered:: OpenPassPhrase DB schema

Database layer
--------------

An abstaction layer for communicating with the database is implemented by the
`opp.db.api <https://github.com/openpassphrase/opp/blob/master/opp/db/api.py>`_
module. The module uses `SQLAlchemy <http://www.sqlalchemy.org/>`_ Object
Relational Mapper (ORM) to access and manipulate the specific RDBMS. The ORM
models are defined in the `opp.db.models <https://github.com/openpassphrase/
opp/blob/master/opp/db/models.py>`_ module.

Bells and whistles
------------------

The rest of OpenPassPhrase can be logically partitioned into two distinct
components:

1. A backend API web service.

2. A fronted web application.

Both parts are actively being developed. In the future, a 3rd component may
be added in the future in the form of a native app running on a client mobile
device.

Server Architecture
~~~~~~~~~~~~~~~~~~~

OpenPassPhrase uses a `Flask <http://flask.pocoo.org/>`_-enabled WSGI
application to interface with the outside world. Flask takes care of
routing requests to appropriate endpoints and sending responses out to
the WSGI server. The application contains two Flask modules: one for
serving up HTML for browser based access and one for delivering JSON
responses for API access.

.. _backend:

Backend Web Service
+++++++++++++++++++

The backend API provides several endpoints exposing OpenPassPhrase capabilities
capabilities. In a typical flow consumers of the API would first call into the
:ref:`authenticate` endpoint with the user's credentials and passphrase. In
response a JSON Web Token (JWT) will be issued. This token, along with the
passphrase, must be included in the header of all subsequent data access
requests. For more information about JWT refer to the full `JWT specification
<https://tools.ietf.org/html/rfc7519>`_. The token has an expiration time after
which it will no longer be accepted and the user will have to re-authenticate.
See the :ref:`expdelta` configuration setting for more details.

.. warning:: Once issued, the server has no way of invalidating a JWT short
    of manually changing the secret signing key on the server. To mitigate
    this vulnerability the ``exp_delta`` configuration setting should be
    set to a value that represents a reasonable tradeoff between security
    and convenience. The authentication endpoint also accepts an override
    parameter for this setting, allowing full control through API.

Frontend Web App
++++++++++++++++

The frontend of OpenPassPhrase is a responsive single-page application
written in Angular2. It utilizes the backend API for all operations.
Login sessions are accomplished by obtaining a JWT with the expiration
date fully controllable by the user. This UI app is hosted in its own
repo, please refer to `Opp-Web <https://github.com/openpassphrase/opp-web>`_
for details and source code.

Request Handlers
~~~~~~~~~~~~~~~~~
The backend API consists of request handlers which service the individual
enpdoints for retrieving data from the ``categories`` and ``items`` tables
respectively. These handlers implement the specific CRUD functionality for
each endpoint. They take care of checking request parameters, performing
data ciphering (encryption/decryption), data retrievale using the database
layer described above, and constructing responses. The responses are in JSON
format and are consumed by both JSON- and HTML-based Flask applications.
The latter will use the JSON data to populate web forms via a jQuery-based
library.
