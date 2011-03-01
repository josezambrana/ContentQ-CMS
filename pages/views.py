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

from django.core.urlresolvers import reverse

from pages.models import Page
from pages.forms import PageForm

from common import common_views
from common import decorator

ENTRIES_PER_PAGE=5
WORDS_NUM = 60

#@decorator.admin_required
def admin(request): 
  return common_views.content_admin(request, 'pages', Page, tpl='pages_admin.html')

def show(request, slug):
  return common_views.content_show(request, slug, 'pages', Page, tpl='pages_show.html')

#@decorator.admin_required
def new(request):
  return common_views.content_new(request, 'pages', PageForm, redirect_to=True, extra_context={'item_name':'Page'}, model=Page)

#@decorator.admin_required
def edit(request, uuid):
  return common_views.content_edit(request, uuid, 'pages', Page, PageForm, redirect_to=True)

#@decorator.admin_required
def delete(request, uuid):
  return common_views.content_delete(request, uuid, Page)