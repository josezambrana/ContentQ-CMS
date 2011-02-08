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

from django.conf import settings
from django.core.urlresolvers import reverse

from users.models import User, UserDoesNotExist, InvalidPassword
from common.test.base import BaseTestCase, ViewTestCase

def debug_test(function):
  def wrapper(*args, **kwargs):
    _str = " START %s " % function.__name__
    logging.info(_str.center(60, '+'))
    logging.info("###starttest# >> %s.%s" % (function.__module__, function.__name__))
    res = function(*args, **kwargs)
    logging.info("###endtest#")
    logging.info(" END test ".center(60, '-'))
    return res
  return wrapper

class UserModelTest(BaseTestCase):
  fixtures = ViewTestCase.fixtures
  def setUp(self):
    BaseTestCase.setUp(self)
    self.admin = User.get(username='admin')
    self.editor = User.get(username='editor')
    self.authuser = User.get(username='authuser')
    self.unactive = User.get(username='unactived')
    
  @debug_test
  def test_check_password(self):
    self.assertEquals(self.authuser.check_password('fakepass'), True)

  @debug_test
  def test_set_password(self):
    self.authuser.set_password('newpass')
    self.assertEquals(self.authuser.check_password('newpass'), True)

  @debug_test
  def test_is_admin(self):
    self.assertEquals(self.admin.is_admin(), True)
    self.assertEquals(self.editor.is_admin(), True)
    self.assertEquals(self.authuser.is_admin(), False)

  @debug_test
  def test_authenticate(self):
    self.assertRaises(UserDoesNotExist, User.authenticate, 'nouser', '')
    self.assertRaises(InvalidPassword, User.authenticate, 'authuser', 'nopass')
    self.assertEquals(User.authenticate('authuser', 'fakepass').username, 'authuser')

class UsersTest(ViewTestCase):
  def setUp(self):
    ViewTestCase.setUp(self)
    self.form_data = {
      "username":"userfake",
      "first_name":"User",
      "last_name":"Fake",
      "email": "fake@mail.com",
      "password1":"passfake",
      "password2":"passfake",
    }
    self.authuser = User.get(username='authuser')
    self.front_url = "http://%s%s" % (settings.DOMAIN, reverse("front"))
    self.settings_url = "http://%s%s" % (settings.DOMAIN, reverse("users_settings"))
    self.success_url = "http://%s%s" % (settings.DOMAIN, reverse('success'))
    
  @debug_test
  def test_register(self):
    r = self.client.post(reverse("users_register"), self.form_data)
    #self.assertRedirects(r, self.front_url)
    self.assertEquals(r.status_code, 302)
    user_ref = User.authenticate('userfake', 'passfake')
    self.assertEquals(user_ref.username, 'userfake')

  @debug_test
  def test_login(self):
    r = self.client.post(reverse("users_login"), {"username":"authuser", "password":"fakepass"})
    self.assertEquals(r.status_code, 302)
    r = self.client.get(reverse("users_login"))
    self.assertEquals(r.status_code, 302)

  @debug_test
  def test_logout(self):
    r = self.client.post(reverse("users_login"), {"username":"authuser", "password":"fakepass"})
    #self.assertRedirects(r, self.front_url)
    self.assertEquals(r.status_code, 302)
    r = self.client.post(reverse("users_logout"), {"username":"authuser", "password":"fakepass"})
    #self.assertRedirects(r, self.front_url)
    self.assertEquals(r.status_code, 302)
#    r = self.client.get(reverse("front"))
#    self.assertNotContains(r, '<a href="/users/settings">Settings</a>')

  @debug_test
  def test_profile(self):
    res = self.client.get(reverse("users_profile_username", args=['authuser']))
    self.assertEquals(res.status_code, 200)
    self.assertContains(res, 'authuser')
    r = self.client.get(reverse("users_profile_username", args=['nouser']))
    self.assertEquals(r.status_code, 404)

  @debug_test
  def test_settings(self):
    r = self.login_and_get('authuser', reverse("users_settings"))
    self.assertEquals(r.status_code, 200)
    self.assertContains(r, 'id_first_name', 2)

  @debug_test
  def test_settings_change(self):
    r = self.login_and_post('editor', reverse("users_settings"), {"first_name":"FirstChanged", "last_name":"LastChanged"})
    self.assertRedirects(r, self.settings_url)
    r = self.client.get(reverse("users_profile"))
    self.assertContains(r, 'FirstChanged')
    self.assertContains(r, 'LastChanged')

  @debug_test
  def test_forgot_success(self):
    r = self.client.get(reverse("users_forgot"))
    self.assertEquals(r.status_code, 200)
    r = self.client.post(reverse("users_forgot"), {"email":"editor@mail.com"})
    self.assertRedirects(r, self.success_url)

  @debug_test
  def test_forgot_invalid_mail(self):
    r = self.client.post(reverse("users_forgot"), {"email":"asdf@mail.com"})
    self.assertContains(r, "We could not find an account that matched that email")

  @debug_test
  def test_passwordreset(self):
    r = self.client.get(reverse("users_passwordreset", args=[self.authuser.code]))
    self.assertEquals(r.status_code, 200)

  @debug_test
  def test_passwordreset_success(self):
    _code = self.authuser.code
    r = self.client.post(reverse("users_passwordreset", args=[_code]), {"password1":"asdf123", "password2":"asdf123"})
    self.assertRedirects(r, self.success_url)
    _user = User.get(username='authuser')
    self.assertTrue(_code != _user.code)
    r = self.client.post(reverse("users_login"), {"username":"authuser", "password":"asdf123"})
    #self.assertRedirects(r, self.front_url)
    self.assertEquals(r.status_code, 302)

  @debug_test
  def test_passwordreset_fail(self):
    r = self.client.post(reverse("users_passwordreset", args=[self.authuser.code]), {"password1":"asdf123", "password2":"nomatch"})
    self.assertContains(r, "The two password fields didn")
    r = self.client.get(reverse("users_passwordreset", args=['asdf']))
    self.assertEquals(r.status_code, 302)