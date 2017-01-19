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
~~~~~~~~

**Base URL:** ``https://<your domain>/opp/api/<version>``

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

``x-opp-phrase`` - authorization passphrase used for decoding secret data.

Authentication headers: TBD

Authentication: TBD
~~~~~~~~~~~~~~~~~~~

Get Categories
~~~~~~~~~~~~~~

**Request:** ``GET <base_url>/categories``

**Response:**

| ``{``
|   ``"result": "success",``
|   ``"categories": [``
|     ``{"id": 1, "category": "category1"}``
|     ``{"id": 2, "category": "category2"}``
|   ``]``
| ``}``

Create Category
~~~~~~~~~~~~~~~

**Request:** ``PUT <base_url>/categories``

**Body:** ``payload`` object containing a list of category names.

*Example:*

``{"payload": ["category1", "category2"]}``

**Response:** ``{"result": "success"}``

Update Category
~~~~~~~~~~~~~~~

**Request:** ``POST <base_url>/categories``

**Body:** ``payload`` object containing a list of category IDs and
updated name values.

*Example:*

``{"payload": [{"id": 1, "category", "category1"},
{"id": 2, "category", "category2"}]}``

**Response:** ``{"result": "success"}``

Delete Category
~~~~~~~~~~~~~~~

**Request:** ``DELETE <base_url>/categories``

**Body:** ``payload`` object containing a list of category IDs and a boolean
``cascade`` value indicating whether to delete the corresponding rows from the
``entries`` table for each deleted category or simply zero out their category
ID values.

*Example:*

``{"payload": {"cascade": True, "ids": [1, 2]}}``

**Response:** ``{"result": "success"}``

Get Entries
~~~~~~~~~~~

**Request:** ``GET <base_url>/entries``

**Response:**

| ``{``
|   ``"result": "success",``
|   ``"entries": [``
|     ``{"id": 1, "entry": "entry1", "category_id": 1, "category": "category1"}``
|     ``{"id": 2, "entry": "entry2", "category_id": 2, "category": "category2"}``
|   ``]``
| ``}``

Create Entry
~~~~~~~~~~~~

**Request:** ``PUT <base_url>/entries``

**Body:** ``payload`` object containing a list of entry/category_id pairs.

*Example:*

``{"payload": [{"entry", "entry1", "category_id": 1}, {"entry": "entry2", "category_id": 2}]}``

**Response:** ``{"result": "success"}``

Update Entry
~~~~~~~~~~~~

**Request:** ``POST <base_url>/entries``

**Body:** ``payload`` object containing a list of updated entry values.

*Example:*

| ``{``
|   ``"payload": [``
|     ``{"id": 1, "entry": "entry1", "category_id": 1, "category": "category1"}``
|     ``{"id": 2, "entry": "entry2", "category_id": 2, "category": "category2"}``
|   ``]``
| ``}``

**Response:** ``{"result": "success"}``

Delete Entry
~~~~~~~~~~~~~~

**Request:** ``DELETE <base_url>/entries``

**Body:** ``payload`` object containing a list of entry IDs to be deleted.

*Example:*

``{"payload": [1, 2]}``

**Response:** ``{"result": "success"}``

