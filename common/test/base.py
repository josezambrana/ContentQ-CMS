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

import logging

from django import test
from django.conf import settings
from django.test import client
from django.core.urlresolvers import reverse

__author__="Jose Maria Zambrana Arze <contact@josezambrana.com>"
__date__ ="$22-dic-2010 14:38:55$"

class BaseTestCase(test.TestCase):
  def setUp(self):
    settings.DEBUG = False
    settings.TESTING = True

class ViewTestCase(test.TestCase):
  fixtures = ['actions', 'roles', 'permissions', 'configdata', 'themes', 'users']
  passwords = {'admin':'.admin.'}
  def setUp(self):
    settings.DEBUG = False
    settings.TESTING = True
    self.client = client.Client(SERVER_NAME=settings.DOMAIN)

  def login(self, username, password=None):
    if password is None:
      password = self.passwords.get(username)
    return self.client.post(reverse('users_login'), {'username':username, 'password':password})

  def login_and_get(self, user, url, data={}):
    l = self.login(user, self.passwords.get(user))
    return self.client.get(url, data)
  
  def login_and_post(self, user, url, data={}):
    l = self.login(user, self.passwords.get(user))
    return self.client.post(url, data)