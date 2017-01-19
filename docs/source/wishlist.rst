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

Authentication
--------------

.. |openidc| raw:: html

    <a target="_blank" href="http://openid.net/connect/">OpenID Connect</a>

This is one of the major components of the backend API that's currently
missing. We need help creating a secure authentication solution. Current
plan is to use |openidc|, but other solutions may be suggested.

Security
--------

We need a security expert to review the implementation for holes and
suggest ways of plugging them. We also need to implement an API feature
which allows for secure random passprhase generation.

Continuous Integration
----------------------

If you are knowledgeable in setting up CI, using GitHub webhooks and statuses,
and integrating 3rd party tools such as Jenkins, Gerrit and others, then
OpenPassPhrase desperately needs you. If, on top of that, you can donate or
help procure an inexpensive platform for running CI, then you are a true godsend
and the open source community will send all kinds of good karma your way!

UX
--

If you've gotten this far in the docs, you are probably wondering why there's
been no mention of end-user experience. Rest assured, it's not forgotten. The
front-end will require at least two more separate projects in the
OpenPassPhrase ecosystem. Firstly, a responsive single-page html5-based web app
needs to be written to consume the backend API. Second, a mobile app will
definitely be required soon after. Discussions and ideas about native
(Android, iOS) versus cross-platform (Xamarin, PhoneGap) implementations
will be entertained. Experts in web and mobile developements are welcome.