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

The rest of OpenPassPhrase can be logically partitioned into three distinct
components:

1. A fronted web application which runs on the server and presents a UI on
   a client browser.

2. A native app running on a client mobile device.

3. A backend API to service both the web and mobile applications.

Parts 1 & 3 are actively being developed. The native mobile app is planned
for the future.

Server
~~~~~~
The frontmost facing portion of OpenPassPhrase is a
`Flask <http://flask.pocoo.org/>`_-enabled WSGI application. Flask takes care
of routing requests to appropriate endpoints and sending responses out to
the WSGI server. The application contains two Flask modules: one for serving
up HTML for browser based access and one for delivering JSON responses for
mobile access.

HTML (web app) flow
+++++++++++++++++++

On a brand new session the user is presented with a login screen. A registered
user would log in with valid credentials in order to gain access to the site.
The user would then supply a passphrase in order to decrypt and be able to
view/modify his/her stored data. The login session expires as soon as the
browser process exits. This is a conscious design decision to deal with a
slight UX incovenience in favor of greater security. Motivated power consumers
of OpenPassPhrase can change this in their own downstream implementation.

.. _jsonflow:

JSON (native app) flow
++++++++++++++++++++++

In manner similar to the web app, the user would log in by sending credentials
to the ``/auth`` endpoint. In lieu of a browser login session, the user would
be issued a JSON Web Token (JWT). This token, along with the passphrase, will
be included in the header of all subsequent data requests. For more information
about JWT refer to the full `JWT specification
<https://tools.ietf.org/html/rfc7519>`_. The token has an expiration time after
which it will no longer be accepted and the user will have to re-authenticate.
See the :ref:`expdelta` configuration setting for more details.

.. warning:: Once issued, the server has no way of invalidating a JWT short
    of manually changing the secret signing key on the server. To mitigate
    this vulnerability the ``exp_delta`` configuration setting must be
    set to a reasonable tradeoff between security and convenience.

Request  handlers
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
