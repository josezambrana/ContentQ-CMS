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

from common import exception
from common import util

def login_required(handler):
  def _wrapper(request, *args, **kw):
    if not request.user:
      util.add_notice(request, 'Please login')
      raise exception.LoginRequiredException()
    return handler(request, *args, **kw)
  _wrapper.__name__ = handler.__name__
  return _wrapper

def logout_required(handler):
  def _wrapper(request, *args, **kw):
    if request.user:
      util.add_notice(request, 'You are already logged in')
      raise exception.LogoutRequiredException()
    return handler(request, *args, **kw)
  _wrapper.__name__ = handler.__name__
  return _wrapper
