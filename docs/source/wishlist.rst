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

.. _wishlist:

Project Wishlist
================

OpenPassPhrase is still in its infancy and we need help to make this a viable
project. Following are some of the areas where we could use the expertise of
skilled developers:

Security
--------

We need a security expert to review the implementation for holes and
suggest ways of plugging them. We also need to implement an API feature
which allows for secure random passprhase generation.

Authentication
--------------

.. |openidc| raw:: html

    <a target="_blank" href="http://openid.net/connect/">OpenID Connect</a>

Currently only single JWT based authentication is implemented, which is
really only suitable for programmatic consumption of the API (e.g. from
a mobile app). It is not so friendly for a web app front-end. Integrating
multiple authentication schemes, including social, oauth2 and single-sign-on,
e.g. |openidc| would make this solution much more attractive and usable.
If you have experience in this field, we welcome your input.

Continuous Integration
----------------------

We are always looking to improve our flows: code reviews, CI, etc. If you
are knowledgeable in setting up CI, using GitHub webhooks and statuses,
and integrating 3rd party tools such as Jenkins, Gerrit and others, your
contribution and expertise would be very valuable and appreciated.

UI
--

If you've gotten this far in the docs, you are probably wondering why there's
hardly been any mention of UI or end-user experience. Rest assured, it's not
forgotten. The front-end will require at least two more separate projects in
the OpenPassPhrase ecosystem. Firstly, a responsive single-page html5-based web
app needs to be written to consume the backend API. Second, a mobile app will
definitely be required soon after. Discussions and ideas about native
(Android, iOS) versus cross-platform (Xamarin, PhoneGap) implementations
will be entertained. Experts in web and mobile developements are welcome.

Miscellaneous Features
----------------------

- Add database backup to opp-db utility
