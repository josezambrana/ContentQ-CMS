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

from blog.models import PostCategory
from blog.forms import PostCategoryForm

# categories
urlpatterns = patterns('common.common_views',
  url(r'^category/admin$', 'category_admin', {"model": PostCategory}, name='postcategory_admin'),
  url(r'^category/new$', 'category_new', {"category_form": PostCategoryForm, "model": PostCategory}, name='postcategory_new'),
  url(r'^category/edit/(?P<slug>[-_\w\d]+)$', 'category_edit', {"model": PostCategory, "category_form": PostCategoryForm}, name='postcategory_edit'),
  url(r'^category/delete/(?P<slug>[-_\w\d]+)$', 'category_delete', {"model": PostCategory}, name='postcategory_delete'),
)

urlpatterns += patterns('blog.views',
  url(r'^admin/?$', 'admin', name='post_admin'),
  url(r'^$', 'index', name='post_list'),
  url(r'^category/(?P<category>[^/]+)$', 'index', name='post_category'),
  url(r'^category/(?P<category>[^\.]+)\.(?P<format>json|xml|html)$', 'index', name='post_category_format'),
  url(r'^tag/(?P<tag>[^/]+)$', 'index', name='post_tag'),
  url(r'^(?P<format>atom|rss)$', 'index', name='post_list'),
  url(r'^new/?$', 'new', name='post_new'),
  url(r'^edit/(?P<slug>[\w\d\-]+)$', 'edit', name='post_edit'),
  url(r'^delete/(?P<slug>[\w\d\-]+)$', 'delete', name='post_delete'),
  url(r'^(?P<slug>[\w\d\-]+)$', 'show', name='post_show'),
  url(r'^(?P<slug>[\w\d\-]+)\.(?P<format>json|xml|html)$', 'show', name='post_show_format'),
)
