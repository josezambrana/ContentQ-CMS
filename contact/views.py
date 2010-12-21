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

from django import http, template
from django.shortcuts import render_to_response
from django.template import loader
from django.core.urlresolvers import reverse

from common import common_views
from common.common_views import _flag_as_admin
from common import util

from contact.models import ContactMessage
from contact.forms import ContactForm, ContactSettings

def contact_admin(request):
  return common_views.content_admin(request, 'contact', ContactMessage, tpl='contact_admin.html')

def contact_settings(request):
  form = ContactSettings()
  if request.method == 'POST':
    form = ContactSettings(request.POST)
    if form.is_valid():
      form.save()
      util.add_success(request, "Contact Settings saved successfully")
      return http.HttpResponseRedirect(reverse('contact_admin'))
  
  c = template.RequestContext(request, locals())
  _flag_as_admin(c)
  return render_to_response('contact_settings.html', c)

def contact_show(request, key_name):
  entry = ContactMessage.get(key_name)
  area = 'contact'
  
  c = template.RequestContext(request, locals())
  _flag_as_admin(c)
  return render_to_response('contact_entry.html', c)


def contact_form(request):
  contact_form = loader.render_to_string("contact_form.html", {"form":ContactForm()})
  tpl = ContactMessage.get_intro()
  contact_content = tpl.replace('{{form}}', contact_form)
  model=ContactMessage

  if request.method == 'POST':
    form = ContactForm(request.POST)
    if form.is_valid():
      item = form.save()
      msg_key = "success_%s_new" % ContactForm._meta.model.object_name()
      message = util.get_message(msg_key, 'success_content_new')
      util.add_success(request, message)
      return http.HttpResponseRedirect(ContactMessage.form_url())

  c = template.RequestContext(request, locals())
  return render_to_response('contact_send.html', c)