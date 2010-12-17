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

from google.appengine.ext import db
from django.core.urlresolvers import reverse

from common import models

DEFAULT_TEMPLATE = "<p>Contact with us by filling the following form:</p><div class=\"clearfix\">{{form}}<div>"

class ContactMessage(models.BaseModel):
  name = db.StringProperty(required=True)
  email = db.StringProperty(required=True)
  message = db.TextProperty(required=True)

  def url(self):
    return reverse('contact_show', args=[self.key().name()])

  @classmethod
  def form_url(cls):
    return reverse('contact_form')

  @classmethod
  def set_mails(cls, mails):
    return models.ConfigData.set_configdata('contact_mails', mails,
                                            label='contact')

  @classmethod
  def get_mails(cls):
    mails = models.ConfigData.get_configdata('contact_mails', label='contact')
    if mails is None:
      mails = [models.ConfigData.get_configdata('SITE_MAIL')]
    return mails

  @classmethod
  def set_intro(cls, intro):
    return models.ConfigData.set_configdata('contact_intro', intro,
                                            label='contact')
  @classmethod
  def get_intro(cls):
    return  models.ConfigData.get_configdata('contact_intro', label='contact', default=DEFAULT_TEMPLATE)
