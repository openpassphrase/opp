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

Welcome to OpenPassPhrase!
==========================

OpenPassPhrase is an open source password manager project. It is primarily
targeted at knowledgeable users with access to their own private server
(virtual or dedicated). Future support for a Platform-as-a-Service (PaaS)
implementation is also planned.

The main objective of this project is to provide a secure backend API for
aggregation, storage, retrieval and management of arbitrary secret data, e.g.
account numbers, usernames and passwords. This backend service can then be
deployed on a user's private server instance and accessed from anywhere.
Once authenticated, the data can be retrieved and decrypted using a single
passphrase.

The API is RESTful in nature and supports standard CRUD operations as well
as additional capabilities such as authentication and random pass-word/phrase
generation.

Deployment
==========

.. toctree::
   :maxdepth: 1

   installation
   configuration

User Guide
==========

.. toctree::
   :maxdepth: 1

   api_ref

Contributing to the project
===========================

.. toctree::
   :maxdepth: 1

   devenv
   guidelines
   wishlist
