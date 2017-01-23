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

.. _configuration:

Configuration
=============

OpenPassPhrase is configurable via configuration files aggregated from several
sources:

    1. User supplied file: this can be passed into various tools such as
       ``opp-db`` on the command line.
    2. User's home directory: ``~/.opp/opp.cfg``.
    3. System directory: ``/etc/opp/opp.cfg``.

Config files (if exist) from all three sources are cascaded together in such
a manner where duplicate values which occur later are simply ignored.
Thus, highest override priority is afforded to the user supplied config and
lowest to the system config.

The config files contain options for configuring various parts of the service
one per line in the following format:

    ``<option_name>: '<option_value>'``

The following options are currently configurable for OpenPassPhrase:

``sql_connect``

    ============    ======
    **Type:**       string

    **Default:**    None
    ============    ======

    Used by SQLAlchemy to establish a connection to the database.

    **Example:**

    | ``sql_connect: 'mysql://<user>:<password>@<host>/<db>'``
    |   or
    | ``sql_connect: 'sqlite:////<full_path_to_db_file>'``

``jwt_secret_key``

    ============    =================================
    **Type:**       string

    **Default:**    'default-insecure'
    ============    =================================

    Used by the web server to encode and decode the signature component of the
    JSON Web Token (JWT). Refer to :ref:`front-end` description for more
    information about JWT.

    **Example:**

    | ``jwt_secret_key: 'large random value'``

``jwt_exp_delta``

    ============    =======
    **Type:**       integer

    **Default:**    300
    ============    =======

    This is the value in **seconds** that determines when the JWT will expire
    starting from issue time. After expiration, the token will not be
    accepted and users will have to login to generate a new token.

    **Example:**

    | ``jwt_exp_delta: 300``
