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

from common import mail
from contact.models import ContactMessage

def email_contact(name, email, message):
  params = {'name':name, 'email':email, 'message':message}
  message = mail.get_mail_message('mail_contact.txt', **params)
  html_message = mail.get_mail_message('mail_contact.html', **params)
  
  subject = "Contact: %s (%s)" % (name, email)
  for to_mail in ContactMessage.get_mails():
    mail.send_mail(to_mail, subject, message, html_message=html_message)