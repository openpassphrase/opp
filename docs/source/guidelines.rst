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

.. _guidelines:

Contribution Guidelines
=======================

Workflow
--------

Currently the workflow consists of a protected *master* branch which allows
merging only via pull requests from other branches. Pull requests must be
reviewed and approved by at least one other contributor.

As the project matures, we expect to add details here about gating checkins
via continuous integration (CI) runs.

Coding
------

Please keep your code pythonic as much as possible. Your contributions will
have a better chance of getting approved if your code follows the conventions
of the Python community and uses the language in the way it is intended to be
used. Any help making existing code more pythonic will be appreciated.

Any code implementing a new feature or functionality is expected to be
accompanied by unit and functional tests. Pull requests without tests will most
likely be denied!

API changes
-----------

Once released, OpenPassPhrase will strive to keep the API consistent and fully
backwards compatible. Major breaking API changes will either be disallowed or
require a new API version to be introduced. Appropriate exceptions may be
given on a case by case basis, but the spirit of this guideline shall be
followed as much as possible.

Reviewing
---------

When performing code reviews, reviewers are encouraged to keep the comments
constructive and to the point. Concentrate on the functionality and potential
impact of the changes on the ecosystem, rather than style and trivial matters.
This is not meant to discourage feedback of the latter type. Simply state the
intent of your suggestion as stylistic or *nitpick* if that is the case. On the
other hand, don't hesitate to express strong opinions if you feel that a change
is not appropriate or incompatible with the project.

In order to perform due dilligence, reviewers should pull down the change
and try to test it out in their environment. Don't approve a change without
testing it first!
