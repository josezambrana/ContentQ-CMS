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
import os
import urllib
import yaml

from django import http
from django.conf import settings
from django.core import exceptions
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.utils import safestring
from django.utils.importlib import import_module

from google.appengine.api import memcache

ITEMS_BY_PAGE = 10

try:
  import uuid
  _generate_uuid = lambda: uuid.uuid4().hex
except ImportError:
  logging.info("No uuid module, using fake")
  _generate_uuid = lambda: str(random.randint(10000000, 20000000))

def qsa(url, params):
  # TODO termie make better
  sep = "?"
  if sep in url:
    sep = "&"
  url = url + sep + urllib.urlencode(params)
  return url

def get_page(request):
  try:
    page=int(request.REQUEST.get('page', 1))
    if page < 1:
      page=1
  except:
    page=1
    
  return page

def get_tags(tags):
  if tags:
    try:
      res = tags.split(',')
      res = [tag.strip(', ') for tag in res]
    except:
      res = []
  else:
    return []
  return res

def generate_uuid():
  return _generate_uuid()

def paginate(request, items, num_items=ITEMS_BY_PAGE):
  paginator = Paginator(items, num_items)
  page = get_page(request)

  try:
    items_paginated = paginator.page(page)
  except (EmptyPage, InvalidPage):
    raise http.Http404

  return items_paginated

def HttpRssResponse(content, request):
  response = http.HttpResponse(content)
  response['Content-type']  = 'application/rss+xml; charset=utf-8'
  return response

def HttpAtomResponse(content, request):
  response = http.HttpResponse(content)
  response['Content-type']  = 'application/atom+xml; charset=utf-8'
  return response

def HttpJsonResponse(content, request):
  response = http.HttpResponse(content)
  response['Content-type']  = 'text/javascript; charset=utf-8'
  return response

def RedirectError(request, message, redirect_to=None):
  add_error(request, message)
  if redirect_to is None:
    redirect_to = reverse('error')
  return http.HttpResponseRedirect(redirect_to)

def RedirectLoginError(request, message):
  redirect_to = "%s?redirect_to=%s" % (reverse('users_login'), request.get_full_path())
  return RedirectError(request, message, redirect_to)

def proccess_form(form, fieldclass, attr, value):
  for field in form:
    if isinstance(field.field.widget, fieldclass):
      field.field.widget.attrs[attr]=value

def get_attr_from(path):
  try:
    dot = path.rindex('.')
    _module, _attr = path[:dot], path[dot+1:]
    mod = import_module(_module)
  except ImportError, e:
    logging.error('   Error importing %s: "%s"' % (_module, e))
    raise exceptions.ImproperlyConfigured, 'Error importing %s: "%s"' % (_module, e)

  try:
    attr = getattr(mod, _attr)
  except AttributeError:
    logging.error('   Module "%s" does not define a "%s" attribute' % (_module, _attr))
    raise exceptions.ImproperlyConfigured, 'Module "%s" does not define a "%s" attribute' % (_module, _attr)
  return attr

def get_attr_from_safe(path, default=None):
  try:
    return get_attr_from(path)
  except exceptions.ImproperlyConfigured:
    logging.error('   get_attr_from_safe>> "%s" is not defined' % (path))
    return default

def get_config(app):
  app_config_file = os.path.join(os.path.join(settings.BASEDIR, app), 'config.yaml')
  
  if os.path.isfile(app_config_file):
    _file = file(app_config_file, 'r')
    return yaml.load(_file)
  
  return None

def get_config_value(app, var, default=None):
  config = get_config(app)
  if config:
    return config.get(var, default)
  return default

# Messages
def cached_messages():
  messages = {}
  for app in settings.INSTALLED_APPS:
    try:
      msgs = get_attr_from('%s.messages.messages' % app)
    except:
      logging.error("   messages not found for %s" % app)
      msgs = {}
    messages.update(msgs)
    
  #memcache.set("global_messages", messages)
  return messages

def get_messages():
  messages = memcache.get("global_messages")
  if messages:
    return messages
  
  return cached_messages()

def get_message(key, default_key='default_message'):
  message = get_messages().get(key, None)
  if message is None:
    message = get_messages().get(default_key)
  return message

def add_success(request, msg):
  return add_msg(request, 'success', msg)

def add_notice(request, msg):
  return add_msg(request, 'notice', msg)

def add_error(request, msg):
  return add_msg(request, 'error', msg)

def add_msg(request, type, msg):
  wrapper = request.session.setdefault(type, [])
  wrapper.append(msg)
  request.session[type] = wrapper
  return True

def get_success(request):
  return request.session.pop('success', [])

def get_notice(request):
  return request.session.pop('notice', [])

def get_error(request):
  return request.session.pop('error', [])

def set_flash(request, msg_key, type='success'):
  _msg = get_message(msg_key)
  return add_msg(request, type, _msg)

def safe(f):
  def _wrapper(value, arg=None):
    rv = f(value, arg)
    return safestring.mark_safe(rv)
  #_wrapper.func_name = f.func_name
  _wrapper.__name__ = f.__name__
  return _wrapper