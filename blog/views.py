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
from django.shortcuts import render_to_response

from blog.handlers import BlogShowHandler, BlogIndexHandler
from blog.models import PostItem, PostCategory
from blog.forms import PostItemForm

from common import common_views
from common.filters import CategoryFilter, TagFilter
from common import decorator

from users import decorator as user_decorator

ENTRIES_PER_PAGE=5
WORDS_NUM = 60

@user_decorator.login_required
def admin(request, format='html'):
  return common_views.content_list(request, 'post', PostItem, [], 'blog_admin.html')

def index(request, format='html', category=None, tag=None):
  view_handler = BlogIndexHandler(request, format=format, category=category, tag=tag)
  return view_handler.handle()

def show(request, slug, format='html'):
  view_handler = BlogShowHandler(request, slug, format=format)
  return view_handler.handle()

@user_decorator.login_required
def new(request):
  return common_views.content_new(request, 'post', PostItemForm, 'blog_new.html', redirect_to=True,  model=PostItem)

@user_decorator.login_required
def edit(request, slug):
  return common_views.content_edit(request, slug, 'post', PostItem, PostItemForm, 'blog_edit.html', redirect_to=True,)

@user_decorator.login_required
def delete(request, slug):
  return common_views.content_delete(request, slug, PostItem)
