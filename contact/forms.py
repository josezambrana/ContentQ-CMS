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
from google.appengine.ext.db import djangoforms

from django import forms
from django.core.validators import validate_email

from common.forms import ModelForm, Form
from common import util
from contact.mail import email_contact
from contact.models import ContactMessage

class MultiEmailField(forms.Field):
  def to_python(self, value):
    if not value:
      return []
    return util.get_tags(value.lower())

  def validate(self, value):
    super(MultiEmailField, self).validate(value)
    for email in value:
      validate_email(email)

class ContactForm(ModelForm):
  class Meta:
    model = ContactMessage
    exclude = ['uuid', 'deleted_at']

  def save(self):
    email_contact(self.cleaned_data['name'], self.cleaned_data['email'],
                  self.cleaned_data['message'])
    return super(ContactForm, self).save()

class ContactSettings(Form):
  mails = MultiEmailField()
  intro = forms.CharField(widget=forms.Textarea)

  def __init__(self, *args, **kwargs):
    super(ContactSettings, self).__init__(*args, **kwargs)
    self.fields['mails'].initial = ', '.join(ContactMessage.get_mails())
    self.fields['intro'].initial = ContactMessage.get_intro()

  def save(self):
    ContactMessage.set_mails(self.cleaned_data['mails'])
    ContactMessage.set_intro(self.cleaned_data['intro'])