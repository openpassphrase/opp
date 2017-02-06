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

We would love to have a security expert review the implementation for holes
and suggest ways of plugging them.

UI Development
--------------

We are actively working on an Angular based responsive single page web
application. It is a complicated endeavor and could always use more
contributors. In addition, you are welcome to propose and work on any
other UI solution (including an app for mobile devices).

Deployment
----------
OpenPassPhrase is currently deployed using Apache server with mod_wsgi.
We would like to pursue other methods of deployment, including using 
various WSGI servers such as uWSGI, CherryPy and GreenUnicorn. Any help
creating the necessary collateral (setup files, etc.) would be highly
appreciated. Also, to reach a wider audience, it would be helpful to 
investigate deployment on PaaS providers (Google App Engine, Heroku, etc.)

Authentication
--------------

.. |openidc| raw:: html

    <a target="_blank" href="http://openid.net/connect/">OpenID Connect</a>

Currently only a single JWT based authentication scheme is implemented.
Integrating multiple additional authentication schemes, including social,
oauth2 and single-sign-on, e.g. |openidc| would make the end product much
more attractive and usable. If you have experience in this field, we welcome
your input.

Continuous Integration
----------------------

We are always looking to improve our flows: code reviews, CI, etc. If you
are knowledgeable in setting up CI, using GitHub webhooks and statuses,
and integrating 3rd party tools such as Jenkins, Gerrit and others, your
contribution and expertise would be very valuable and appreciated.

Miscellaneous Wishilst
----------------------

- Docs improvments (diagrams, etc.)
- Extensive and thorough review of entire code base
- Detailed and useful code comments
