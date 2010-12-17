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

from google.appengine.api import users
from django import http
from common import exception

def admin_required(function):
  def _wrap(request, *args, **kw):
    q = request.META['PATH_INFO']

    user = users.get_current_user()
    if not user:
      return http.HttpResponseRedirect(users.create_login_url(q))
    else:
      if not users.is_current_user_admin():
        raise exception.AdminRequiredError

    return function(request, *args, **kw)
  return _wrap

def permission(roles):
  def _decorator(function):
    def _wrap(request, *args, **kwargs):
      has_access = False
      for role in roles:
        if role in request.user.roles:
          has_access = True
      if has_access:
        return function(request, *args, **kwargs)
      raise exception.PermissionDeniedError
    return _wrap
  return _decorator