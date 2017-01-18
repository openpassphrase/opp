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

Development Environment
=======================

**Welcome Contributors!**

This project is in the very early stages of development. Thus, the development
environment (not to mention the API and the documentation) is very fluid and
may change radically as more contributors join. Please bear that in mind when
starting out.

Repo
----

The OpenPassPhrase code is managed by Git and currently lives in two
repositories:

- **Bitbucket**: ``ssh://git@bashmak.com:7999/bg/openpassphrase.git``
- **GitHub**: ``git@github.com:openpassphrase/opp.git``

Mirroring is currently accomplished manually, by pushing to both remotes.
Therefore, when setting up your repo, follow this recommended procedure:

- First clone from bitbucket::

    git clone ssh://git@bashmak.com:7999/bg/openpassphrase.git
    cd openpassphrase
- Then add the github remote and configure it as a push mirror::

    git remote add --mirror=push github_origin git@github.com:openpassphrase/opp.git
