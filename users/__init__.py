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
import datetime

from django.conf import settings
from users.models import AnonymousUser

def authenticate(request, user):
    logging.error(">> users.authenticate")
    if user is None:
      logging.error(" user is None")
      user = request.user
    user.last_login = datetime.datetime.now()
    user.save()

    if settings.SESSION_KEY in request.session:
      logging.info("   SESSION_KEY in request.session ")
      if request.session[settings.SESSION_KEY] != user.key():
        # To avoid reusing another user's session, create a new, empty
        # session if the existing session corresponds to a different
        # authenticated user.
        request.session.flush()
    else:
      logging.info("   cycle_key")
      request.session.cycle_key()
    request.session[settings.SESSION_KEY] = user.key()
    logging.info("   user.key(): %s " % user.key())
    
    if hasattr(request, 'user'):
        request.user = user

def logout(request):
  request.session.flush()
  if hasattr(request, 'user'):
    request.user = AnonymousUser()