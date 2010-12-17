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

from blog.models import PostItem, PostCategory

from common import handlers
from common.filters import PropertyFilter, CategoryFilter, TagFilter

class BlogShowHandler(handlers.CommentableHandler):
  def __init__(self, request, slug, format='html'):
    super(BlogShowHandler, self).__init__(request, slug, area='post',
                                          model=PostItem,
                                          tpl='blog_show',
                                          format=format)

class BlogIndexHandler(handlers.ContentListViewHandler):
  def __init__(self, request, category=None, tag=None, format='html'):
    super(BlogIndexHandler, self).__init__(request, area='post',
                                                    model=PostItem,
                                                    order='-created_at',
                                                    tpl='blog_list',
                                                    format=format)
    if category is not None:
      self.filters.append(CategoryFilter(category))
    if tag is not None:
      self.filters.append(TagFilter(tag))
    self.filters.append(PropertyFilter('status', 'published'))

    self.update_context({"category":category})