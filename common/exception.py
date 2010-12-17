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

from django.core.urlresolvers import reverse

class Error(Exception):
  @property
  def message(self):
    return "%s" % (self.__class__.__name__)

  def __str__(self):
    return self.message

class AuthenticationException(Error):
  """ an error to raise when a resource need authorization """
  pass

class AdminRequiredError(Error):
  """ an error to raise when a resource need administrator credentials """
  pass

class UnableActionError(Error):
  """ an error to raise when a action can not be done """
  pass

class PermissionDeniedError(Error):
  """ an error to raise when a user can not execute an action"""
  pass

class RedirectException(Error):
  base_url = '/'
  redirect = False

  def build_redirect(self, request):
    return "%s?%s" % (request.META['PATH_INFO'], request.META['QUERY_STRING'])

  def build_url(self, request):
    from common import util
    base_url = self.base_url
    if self.redirect:
      redirect_to = self.build_redirect(request)
      base_url = util.qsa(base_url, {'redirect_to': redirect_to})
    return base_url

class LoginRequiredException(RedirectException):
  base_url = '/users/login'
  redirect = True

class LogoutRequiredException(RedirectException):
  base_url = '/'
  redirect = False