# Copyright 2010 Jose Maria Zambrana Arze <contact@josezambrana.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.conf.urls.defaults import *

urlpatterns = patterns('users.views',
  url(r'^$', 'admin', name='users_admin'),
  url(r'^login$', 'login', name='users_login'),
  url(r'^logout$', 'logout', name='users_logout'),
  url(r'^register$', 'register', name='users_register'),
  url(r'^settings$', 'settings', name='users_settings'),
  url(r'^profile$', 'profile', name='users_profile'),
  url(r'^forgot$', 'forgot', name='users_forgot'),
  url(r'^passwordreset/(?P<code>[^/]+)$', 'passwordreset', name='users_passwordreset'),
  url(r'^(?P<username>[\w]+)$', 'profile', name='users_profile_username'),
)