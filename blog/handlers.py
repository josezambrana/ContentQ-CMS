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

from blog.forms import PostItemForm
from blog.models import PostItem

from common.handlers import ModelHandler
from common.filters import PropertyFilter, CategoryFilter, TagFilter

class BlogHandler(ModelHandler):
  def __init__(self):
    ModelHandler.__init__(self, PostItem, PostItemForm)

  def list(self, request, format='html', category=None, tag=None):
    filters = []
    if category is not None:
      filters.append(CategoryFilter(category))
    if tag is not None:
      filters.append(TagFilter(tag))
    filters.append(PropertyFilter('status', 'published'))

    return ModelHandler.list(self, request, tpl='blog_list', format=format, filters=filters)