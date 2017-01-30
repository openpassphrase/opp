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

API Reference
=============

Overview
--------

**Base URL:** ``https://<your domain>/api/<version>``

Where *<version>* is provided in anticipation of multiple API versions in the
future. Current latest version is *v1*.

**Web Server success codes:** 20x

**Web Server error codes:** 4xx, 500

**Request format:** JSON

**Response format:** JSON

All 200 responses are returned in the following form:

| ``{"result": "success", <optional payload object or array>}``
|   or
| ``{"result": "error", "message": "error message"}``

**Required headers:**

``"Content-Type: application/json"`` - Required for all API requests.

``"x-opp-jwt: "<token>"`` - JSON Web Token authentication header. Required for
all Categories and Items endpoints.

``"x-opp-phrase: <phrase>"`` - Authorization passphrase used for decoding
secret data. Required for all Categories and Items endpoints.

|

Authentication endpoint
-----------------------
``<base_url>/auth``

Authenticate
~~~~~~~~~~~~

**Request:** ``POST``

**Body:** JSON object containing ``username`` and ``password`` fields.

*Example:*

``{"username": "user1", "password": "mypass"}``

**Response:**

``{"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}``

|

Categories endpoint
-------------------
``<base_url>/categories``

Get Categories
~~~~~~~~~~~~~~

**Request:** ``GET``

**Response:**

| ``{``
|   ``"result": "success",``
|   ``"categories": [``
|     ``{"id": 1, "name": "category1"}``
|     ``{"id": 2, "name": "category2"}``
|   ``]``
| ``}``

Create Category
~~~~~~~~~~~~~~~

**Request:** ``PUT``

**Body:** ``payload`` object containing a list of category names.

*Example:*

``{"payload": ["category_name1", "category_name2"]}``

**Response:** ``{"result": "success"}``

Update Category
~~~~~~~~~~~~~~~

**Request:** ``POST``

**Body:** ``payload`` object containing a list of category IDs and
updated name values.

*Example:*

``{"payload": [{"id": 1, "name", "new_name"},
{"id": 2, "name", "new_name"}]}``

**Response:** ``{"result": "success"}``

Delete Category
~~~~~~~~~~~~~~~

**Request:** ``DELETE``

**Body:** ``payload`` object containing a list of category IDs and a boolean
``cascade`` value indicating whether to delete the corresponding rows from the
``items`` table for each deleted category or simply zero out their category
ID values.

*Example:*

``{"payload": {"cascade": True, "ids": [1, 2]}}``

**Response:** ``{"result": "success"}``

|

Items Endpoint
--------------
``<base_url>/items``

Get Items
~~~~~~~~~

**Request:** ``GET``

**Response:**

| ``{``
|   ``"result": "success",``
|   ``"items": [ {item1_data}, {item2_data} ]``
| ``}``

Where ``item_data`` objects contain:

| ``{``
|   ``"id": 1,``
|   ``"name": "Wells Fargo",``
|   ``"url": "https://wellsfargo.com",``
|   ``"account": "01457XA8900",``
|   ``"username": "mylogin",``
|   ``"password": "mypassword",``
|   ``"blob": "any custom data, may be delimited",``
|   ``"category": {"id": 1, "name": "Credit Cards"}``
| ``}``

Create Item
~~~~~~~~~~~~

**Request:** ``PUT``

**Body:** ``payload`` object containing a list of items.

*Example:*

``{ "payload": [ {item1_data}, {item2_data} ] }``

.. Note:: For item creation, the ``id`` and ``category.name`` fileds are
   ignored. All of the other fields are optional and may be omitted.

**Response:** ``{"result": "success"}``

Update Item
~~~~~~~~~~~~

**Request:** ``POST``

**Body:** ``payload`` object containing a list of items.

*Example:*

``{ "payload": [ {new_item1_data}, {new_item2_data} ] }``

.. Note:: For item update, the ``category.name`` filed is ignored, while the
   ``id`` field is mandatory. All of the other files are optional and may be
   omitted.

**Response:** ``{"result": "success"}``

Delete Item
~~~~~~~~~~~~~~

**Request:** ``DELETE``

**Body:** ``payload`` object containing a list of item IDs to be deleted.

*Example:*

``{"payload": [1, 2]}``

**Response:** ``{"result": "success"}``
