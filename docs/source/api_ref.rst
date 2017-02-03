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

This is the backend API intended for consumption by the frontend applications
(web and mobile).

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
secret data. Required for the *fetchall* endpoint and for Categories/Items
create/update calls.

Authentication endpoint
-----------------------
``<base_url>/auth``

Authenticate
~~~~~~~~~~~~

**Request:** ``POST``

**Body:** JSON object containing mandatory ``username`` and ``password``
fields and an optional ``exp_delta`` parameter for customizing the expiration
time of the JWT that will be issued in response.

*Example:*

``{"username": "user1", "password": "mypass", "exp_delta": 3600}``

**Response:**

``{"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}``

Fetch All Endpoint
------------------
``<base_url>/fetchall``

**Request:** ``GET``

**Response:**

| ``{``
|   ``"result": "success",``
|   ``"categories": [``
|     ``{"id": 1, "name": "category1", "items": [{<item1>}, {<item2>}]},``
|     ``{"id": 2, "name": "category2", "items": [{<item3>}, {<item4>}]},``
|     ``{"id": null, "name": "default", "items": [{<item5>}, {<item6>}]}``
|   ``]``
| ``}``

Where ``item`` objects contain:

| ``{``
|   ``"id": 1,``
|   ``"name": "Wells Fargo",``
|   ``"url": "https://wellsfargo.com",``
|   ``"account": "01457XA8900",``
|   ``"username": "mylogin",``
|   ``"password": "mypassword",``
|   ``"blob": "any custom data, may be delimited"``
| ``}``

.. note:: The "default" category name is reserved. This category is
    automatically created for items that are not assigned a category
    id upon creation.

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
|     ``{"id": 1, "name": "category1"},``
|     ``{"id": 2, "name": "category2"}``
|   ``]``
| ``}``

Create Category
~~~~~~~~~~~~~~~

**Request:** ``PUT``

**Body:** ``category_names`` object containing a list of category names.

*Example:*

``{"category_names": ["category1", "category2"]}``

**Response:** ``{"result": "success", "categories": [{<category1>}, {<category2>}]}``

Where ``category`` objects contain:

| ``{"id": 1, "name": "category1"}``

Update Category
~~~~~~~~~~~~~~~

**Request:** ``POST``

**Body:** ``categories`` object containing a list of category IDs and
updated name values.

*Example:*

``{"categories": [{"id": 1, "name", "new_name"},
{"id": 2, "name": "new_name"}]}``

**Response:** ``{"result": "success"}``

Delete Category
~~~~~~~~~~~~~~~

**Request:** ``DELETE``

**Body:** ``ids`` object containing a list of category IDs and a boolean
``cascade`` value indicating whether to delete the corresponding rows from the
``items`` table for each deleted category or simply zero out their category
ID values.

*Example:*

``{"cascade": True, "ids": [1, 2]}``

**Response:** ``{"result": "success"}``

Items Endpoint
--------------
``<base_url>/items``

Create Item
~~~~~~~~~~~~

**Request:** ``PUT``

**Body:** ``items`` object containing a list of items.

*Example:*

``{ "items": [ {item1}, {item2} ] }``

Where ``item`` objects contain any of the following optional fields:

| ``{``
|   ``"name": "Wells Fargo",``
|   ``"url": "https://wellsfargo.com",``
|   ``"account": "01457XA8900",``
|   ``"username": "mylogin",``
|   ``"password": "mypassword",``
|   ``"blob": "any custom data, may be delimited",``
|   ``"category_id": 1``
| ``}``

.. Note:: If ``category_id`` field is omitted, the item will be assigned
   a category ID of 0 which will be mapped to a reserved **"default"**
   category in the ``fetchall`` response.

**Response:** ``{"result": "success, "items": [{<item1>}, {<item2>}]}``

Where ``item`` objects contain:

| ``{``
|   ``"name": "Wells Fargo",``
|   ``"url": "https://wellsfargo.com",``
|   ``"account": "01457XA8900",``
|   ``"username": "mylogin",``
|   ``"password": "mypassword",``
|   ``"blob": "any custom data, may be delimited",``
|   ``"category":``
|     ``{``
|       ``"id": 1, "name": "category1"``
|     ``}``
| ``}``


Update Item
~~~~~~~~~~~~

**Request:** ``POST``

**Body:** ``items`` object containing a list of items.

*Example:*

``{ "items": [ {item1}, {item2} ] }``

Where ``item`` objects contain any of the same optional fields used in
item creation, plus a mandatory item ``id`` fields used to refer to the
item being updated.

**Response:** ``{"result": "success"}``

Delete Item
~~~~~~~~~~~~~~

**Request:** ``DELETE``

**Body:** ``ids`` object containing a list of item IDs to be deleted.

*Example:*

``{"ids": [1, 2]}``

**Response:** ``{"result": "success"}``
