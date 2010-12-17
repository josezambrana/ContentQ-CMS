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

from django.conf import settings
from django.core.urlresolvers import reverse

from common.models import ConfigData
from common import mail

def mail_welcome(user):
  params = {'user':user}
  message = mail.get_mail_message('mail_welcome.txt', **params)
  html_message = mail.get_mail_message('mail_welcome.html', **params)

  subject = "Welcome to %s" % ConfigData.get_configdata('SITE_NAME')
  mail.send_mail(user.email, subject, message, html_message=html_message)

def mail_confirm(user, mail):
  _link = "http://%s%s" % (settings.DOMAIN, reverse("users_validate_email", args=[code]))
  params = {'user':user, "link": _link}
  message = mail.get_mail_message('mail_validate_email.txt', **params)
  html_message = mail.get_mail_message('mail_validate_email.html', **params)

  subject = "Confirm your %s account" % ConfigData.get_configdata('SITE_NAME')
  
  mail.send_mail(user.email, subject, message, html_message=html_message)

def mail_password_instructions(user, code):
  _link = "http://%s%s" % (settings.DOMAIN, reverse("users_passwordreset", args=[code]))
  params = {'user':user, "link": _link}
  message = mail.get_mail_message('mail_password_instructions.txt', **params)
  html_message = mail.get_mail_message('mail_password_instructions.html', **params)

  subject = "Reset your %s password" % settings.SITE_NAME

  mail.send_mail(user.email, subject, message, html_message=html_message)