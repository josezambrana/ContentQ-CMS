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

from blog.handlers import BlogHandler
from users import decorator as user_decorator

ENTRIES_PER_PAGE=5
WORDS_NUM = 60

handler = BlogHandler()

@user_decorator.login_required
def admin(request, format='html'):
  return handler.admin(request, tpl='blog_admin.html', format=format)

def index(request, format='html', category=None, tag=None):
  return handler.list(request, category=category, tag=tag, format=format)

def show(request, slug, format='html'):
  return handler.show(request, slug, tpl='blog_show', format=format)

@user_decorator.login_required
def new(request):
  return handler.new(request, tpl='blog_new', redirect_to=True)

@user_decorator.login_required
def edit(request, slug):
  return handler.edit(request, slug, tpl='blog_edit', redirect_to=PostItem.admin_url())

@user_decorator.login_required
def delete(request, slug):
  return handler.delete(request, slug, redirect_to=PostItem.admin_url())
