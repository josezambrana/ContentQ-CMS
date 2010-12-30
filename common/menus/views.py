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
from django.conf import settings

from common.models import ConfigData, MenuItem, Menu
from common.menus.forms import MenuItemForm

from common import common_views
from common import decorator
from common import util

from common.handlers import NewHandler

@decorator.admin_required
def admin(request):
  return common_views.content_admin(request, 'menus', MenuItem, [],
                                'menuitems_admin.html')
                                
def list(request):
  return common_views.content_list(request, 'menus', MenuItem, [], 'menuitems_list.html')

@decorator.admin_required
def new(request):
  content_dir = {}
  for app in settings.INSTALLED_APPS:
    _config = ConfigData.get(name=app, label='installed_app')
    if _config:
      _config = "%s.config.get_content" % app
      get_content = util.get_attr_from_safe(_config)
      if get_content is not None:
        content_dir.update({app:get_content()})
        
  handler = NewHandler(request, area='menus', 
                                model=MenuItem,
                                model_form=MenuItemForm, 
                                tpl='menuitems_new.html', 
                                redirect_to=MenuItem.admin_url(), 
                                extra_context={"content_dir":content_dir})
  return handler.handle() 

@decorator.admin_required
def edit(request, slug):
  return common_views.content_edit(request, slug, 'menus', MenuItem, MenuItemForm, 'menuitems_edit.html', redirect_to=MenuItem.admin_url())

def show(request, slug):
  return common_views.content_show(request, slug, 'menus', MenuItem, 'menuitems_show.html')

@decorator.admin_required
def delete(request, slug):
  return common_views.content_delete(request, slug, MenuItem)