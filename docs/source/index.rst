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
deployed on a user's private server instance and accessed over TLS from
anywhere. Once authenticated, the data can be retrieved and decrypted using a
single passphrase.

The API is RESTful in nature and supports standard CRUD operations as well
as additional capabilities such as authentication and random pass-word/phrase
generation.


YAPM - yet another password manager?
====================================

The motivations for this project are several. With incidents of hacking
prolifirating in modern times, it is more important than ever to keep
sensitive data such as passwords and account information as secure as
possible. OpenPassPhare is intended for users who want complete control
over how that data is stored and managed. Most password managers store
your data in a cloud that's generally not accessible to you except via
their own interface. OpenPassPhrase lets you use your own cloud, hosted
anywhere you wish, be that on your own private home server or an AWS
instance. The bottom line is that you are the only one with access
to that server. And you can customize the interface to your liking.
Additionally, most password managers are client based solutions. While
the good ones give you a seamless experience of syncing between clients,
it is still somewhat of a nuisance to have to do that. Especially if you
want short (transient) access to your password data on a new system
(e.g. a library computer or a friend's PC). OpenPassPhrase shifts the
paradigm to a server based solution. Now your password data is accessible
from any internet-enabled device. Assuming of course you trust the
device/browser that you are using and you trust TLS to secure the
communication with your server. But the same trust issue exists with
client-based solutions as well. If you like what you've heard so far, 
read on!

Deploying
=========

.. toctree::
   :maxdepth: 1

   installation
   configuration

Using
=====

.. toctree::
   :maxdepth: 1

   architecture
   api_ref

Contributing
============

.. toctree::
   :maxdepth: 1

   devenv
   guidelines
   wishlist

Getting Support
===============

If you need help or have a question about OpenPassPhrase, send email to:
dev@openpassphrase.com and we will try to accomodate your inquiry to the best
of our ability.
