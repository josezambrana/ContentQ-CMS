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
from django.conf import settings
from django.core import serializers
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _

from common import decorator
from common import util

from users import decorator as users_decorator
from users import authenticate

from common.models import Action, Block, ConfigData, Permission, Role, Theme
from common.forms import AdminSiteForm, InstallForm, BlockForm, BlockNewForm

ENTRIES_PER_PAGE = 10

def _flag_as_admin(context):
  logging.info("** common.common_views._flag_as_admin")
  admin_theme_url = settings.THEME_URL + Theme.get_admin().directory_name + '/'
  context.update({"admin":True, "THEME_MEDIA_URL":admin_theme_url})

def _get_content(id, model):
  content = model.get(uuid=id)
  if not content:
    content = model.get(slug=id)
    if not content:
      raise http.Http404(_("Item not found"))
  return content

@decorator.admin_required
@users_decorator.login_required
def dashboard(request):
  for app in settings.INSTALLED_APPS:
    adminareas = []
    _config = ConfigData.get(name=app, label='installed_app')
    if _config:
      adminareas += _config.extra.get('adminareas')

  c = template.RequestContext(request, locals())
  _flag_as_admin(c)
  return render_to_response("dashboard.html", c)

@decorator.admin_required
@users_decorator.login_required
def admin_site(request):
  area = 'site'
  form = AdminSiteForm()
  if request.method == 'POST':
    form = AdminSiteForm(request.POST)
    if form.is_valid():
      form.save()
      return http.HttpResponseRedirect(reverse('admin_dashboard'))
  
  c = template.RequestContext(request, locals())
  _flag_as_admin(c)
  return render_to_response("admin_site.html", c)

@decorator.admin_required
def install(request):
  area = 'install'

  if ConfigData.get_configdata('site_installed', default=False):
    util.add_error(request, "Site is already installed")
    return http.HttpResponseRedirect(reverse('front'))
  
  form = InstallForm()
  if request.method == 'POST':
    form = InstallForm(request.POST)
    if form.is_valid():
      user = form.save()
      ConfigData.set_configdata('site_installed', True)
      authenticate(request, user)
      util.add_success(request, "Site has been installed successfully")
      return http.HttpResponseRedirect(reverse('admin_dashboard'))

  c = template.RequestContext(request, locals())
  _flag_as_admin(c)
  return render_to_response('install.html', c)

@decorator.admin_required
def config_admin(request):
  return content_admin(request, 'config', ConfigData,
                      extra_context={},
                      tpl='config_admin', order='label')

@decorator.admin_required
def category_new(request, area='category', category_form=None, model=None, tpl='category_new.html'):
  return content_new(request, area, category_form, tpl, model.admin_url(), model=model)

@decorator.admin_required
def category_edit(request, slug, area='category', model=None, tpl='category_edit.html', category_form=None):
  return content_edit(request, slug, area, model, category_form, tpl, model.admin_url())

@decorator.admin_required
def category_admin(request, area='category', tpl='category_admin', model=None):
  return content_admin(request, area, model, [], tpl, extra_context={})

@decorator.admin_required
def category_delete(request, slug, model=None):
  return content_delete(request, slug, model)

def content_admin(request, area='content', model=None, filters=[], tpl='content_admin', format='html', extra_context={}):
  extra_context.update({'admin':True})
  return content_list(request, area, model, filters, tpl, format, extra_context)
  
def content_list(request, area='content', model=None, filters=[], tpl='content_list', format='html', extra_context={}, order=None):
  items = model.all()
  
  if order is not None:
    items.order(order)

  for filter in filters:
    try:
      items = filter.filter(items)
    except AttributeError:
      items = []

  items = util.paginate(request, items, ENTRIES_PER_PAGE)
  
  c = template.RequestContext(request, locals())
  c.update(extra_context)

  if not tpl.endswith(('html', 'json', 'atom', 'rss', 'json')):
    tpl = '%s.%s' % (tpl, format)

  if format == 'atom':
    return render_to_response(tpl, c,
                              mimetype='application/atom+xml; charset=utf-8')
  elif format == 'rss':
    return render_to_response(tpl, c,
                              mimetype='application/rss+xml; charset=utf-8')
  elif format == 'json':
    return util.HttpJsonResponse(serializers.serialize('json', items.object_list), request)
  
  return render_to_response(tpl, c)


def content_new(request, area='content', model_form=None, tpl='content_new.html', redirect_to=None, extra_context={}, model=None):
  form = model_form()
  if request.method == 'POST':
    form = model_form(request.POST)
    if form.is_valid():
      item = form.save()

      msg_key = "success_%s_new" % model_form._meta.model.object_name()
      message = util.get_message(msg_key, 'success_content_new')
      util.add_success(request, message)

      if redirect_to is not None:
        if redirect_to == True:
          return http.HttpResponseRedirect(item.url())
        return http.HttpResponseRedirect(redirect_to)
    
  ckeditor = '.ckeditor textarea'
  
  c = template.RequestContext(request, locals())
  c.update(extra_context)
  _flag_as_admin(c)
  return render_to_response(tpl, c)

def content_edit(request, id, area='content', model=None, model_form=None, tpl='content_edit.html', redirect_to=None, extra_context={}):
  content = _get_content(id, model)

  form = model_form(instance=content)
  if request.method == 'POST':
    form = model_form(request.POST, instance=content)
    if form.is_valid():
      content = form.save()

      msg_key = "success_%s_edit" % model_form._meta.model.object_name()
      message = util.get_message(msg_key, 'success_content_edit')
      util.add_success(request, message)
      
      if redirect_to is not None:
        if redirect_to == True:
          return http.HttpResponseRedirect(content.url())
        return http.HttpResponseRedirect(redirect_to)

  ckeditor = '.ckeditor textarea'
  
  c = template.RequestContext(request, locals())
  c.update(extra_context)
  _flag_as_admin(c)
  return render_to_response(tpl, c)

def content_show(request, id, area='content', model=None, tpl='content_show.html', extra_context={}, format='html'):
  content = _get_content(id, model)
                                    
  if format == 'html':
    c = template.RequestContext(request, locals())
    c.update(extra_context)
    return render_to_response(tpl, c)
  elif format == 'json':
    return util.HttpJsonResponse(serializers.serialize('json', [content]), request)
  
def content_delete(request, slug, model=None):
  content = _get_content(slug, model)
  content.delete()
  
  msg_key = "success_%s_delete" % model.object_name()
  message = util.get_message(msg_key, 'success_content_delete')
  util.add_success(request, message)

  return http.HttpResponseRedirect(content.admin_url())

@decorator.admin_required
def blocks_admin(request):
  return content_admin(request, 'blocks', Block, extra_context={}, tpl='blocks_admin.html')

@decorator.admin_required
def blocks_new(request):
  return content_new(request, 'blocks', BlockNewForm, redirect_to=Block.admin_url(), model=Block)
                                
@decorator.admin_required
def blocks_publish(request, uuid):
  block_ref = Block.get(uuid=uuid)
  block_ref.publish()
  return http.HttpResponseRedirect(Block.admin_url())

@decorator.admin_required
def blocks_unpublish(request, uuid):
  block_ref = Block.get(uuid=uuid)
  block_ref.unpublish()
  return http.HttpResponseRedirect(Block.admin_url())

@decorator.admin_required
def blocks_edit(request, uuid):
  return content_edit(request, uuid, 'blocks', Block, BlockForm, tpl='blocks_edit.html', redirect_to_admin=True)

@decorator.admin_required
def blocks_delete(request, uuid):
  return content_delete(request, uuid, Block)

def flash_view(request):
  c = template.RequestContext(request, locals())
  return render_to_response('flash_view.html', c)

@decorator.permission(['administrator'])
def roles(request):
  if request.method == 'POST':
    action = request.POST.get('action', None)
    if action == 'role_delete':
      _ref = Role.get(uuid=request.POST.get('role_uuid'))
      _ref.delete()
    elif action == 'role_create':
      _ref = Role(name=request.POST.get('role_name'))
      _ref.put()

  area = "users"
  items = util.paginate(request, Role.all())

  c = template.RequestContext(request, locals())
  _flag_as_admin(c)
  return render_to_response('roles.html', c)

@decorator.permission(['administrator'])
def permissions(request):
  logging.info(">> users.views.permissions")
  roles = Role.all()
  area = "users"

  if request.method == 'POST':
    for role in roles:
      _list = request.POST.getlist(role.name)
      _ref = Permission.get(role=role.name)
      if _ref is None:
        _ref = Permission(role=role.name)
      _ref.actions = _list
      _ref.put()

  apps = {}
  actions = []
  for app in settings.INSTALLED_APPS:
    app_actions = [x for x in Action.filter('appname =', app) if x.authorizable ]
    if app_actions:
      apps[app] = app_actions
    actions +=  app_actions

  permissions = {}
  for role in roles:
    permission = Permission.get_by_role(role=role.name)
    permissions[role.name] = {}
    for action in actions:
      permissions[role.name].setdefault(action.name, (action.name in permission.actions and True))

  c = template.RequestContext(request, locals())
  _flag_as_admin(c)
  return render_to_response('permissions.html', c)