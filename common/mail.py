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
import copy

from google.appengine.api import mail as gae_mail

from django.conf import settings
from django.template.loader import render_to_string

from common.context_processors import get_global_vars

def get_context(params):
  context = copy.copy(get_global_vars())
  context.update(params)
  return context

def get_mail_message(tpl, **kw):
  return render_to_string(tpl, get_context(kw))

def send_mail(to_email, subject, message, on_behalf=None, html_message=None):
  on_behalf = on_behalf and on_behalf or settings.DEFAULT_FROM_EMAIL
  _message = gae_mail.EmailMessage(sender=on_behalf,
                                   to=to_email,
                                   subject=subject,
                                   body=message,
                                   html=html_message)
  try:
    _message.send()
    return True
  except:
    logging.error('Email can not be sent')
    return False