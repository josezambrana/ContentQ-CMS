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

from django.conf.urls.defaults import *

from common.models import Menu
from common.menus.forms import MenuForm

urlpatterns = patterns('common.common_views',
  url(r'^admin/dashboard$', 'dashboard', name='admin_dashboard'),
  url(r'^admin/site$', 'admin_site', name='admin_site'),
  url(r'^config/?$', 'config_admin', name='config_admin'),
  url(r'^install$', 'install', name='install'),
  url(r'^error$', 'flash_view', name='error'),
  url(r'^notice$', 'flash_view', name='notice'),
  url(r'^success$', 'flash_view', name='success'),
  url(r'^permissions$', 'permissions', name='permissions'),
  url(r'^roles$', 'roles', name='roles'),
)
urlpatterns += patterns('',
  url(r'^admin$', 'django.views.generic.simple.redirect_to', {'url': 'admin/dashboard'}),
)

urlpatterns += patterns('common.common_views',
  url(r'^blocks/new$', 'blocks_new', name='blocks_new'),
  url(r'^blocks/$', 'blocks_admin', name='blocks_admin'),
  url(r'^blocks/edit/(?P<uuid>[-_\w\d]+)$', 'blocks_edit', name='blocks_edit'),
  url(r'^blocks/publish/(?P<uuid>[-_\w\d]+)$', 'blocks_publish', name='blocks_publish'),
  url(r'^blocks/unpublish/(?P<uuid>[-_\w\d]+)$', 'blocks_unpublish', name='blocks_unpublish'),
  url(r'^blocks/delete/(?P<uuid>[-_\w\d]+)$', 'blocks_delete', name='blocks_delete'),
)

urlpatterns += patterns('common.menus.views',
  url(r'^menus/$', 'admin', name='menuitem_admin'),
  url(r'^menus/new/?$', 'new', name='menuitem_new'),
  url(r'^menus/edit/(?P<slug>[\w\d\-]+)$', 'edit', name='menuitem_edit'),
  url(r'^menus/delete/(?P<slug>[\w\d\-]+)$', 'delete', name='menuitem_delete'),
  url(r'^menus/(?P<slug>[\w\d\-]+)$', 'show', name='menuitem_show'),
)

# categories
urlpatterns += patterns('common.common_views',
  url(r'^menus/menu/admin$', 'category_admin', {"model": Menu, "area":"menus"}, name='menu_admin'),
  url(r'^menus/menu/new$', 'category_new', {"category_form": MenuForm, "model": Menu, "area":"menus"}, name='menu_new'),
  url(r'^menus/menu/edit/(?P<slug>[-_\w\d]+)$', 'category_edit', {"model": Menu, "category_form": MenuForm, "area":"menus"}, name='menu_edit'),
  url(r'^menus/menu/delete/(?P<slug>[-_\w\d]+)$', 'category_delete', {"model": Menu, "area":"menus"}, name='menu_delete'),
)