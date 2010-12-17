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

from django.utils.translation import ugettext as _
from common.blocks import Block

from blog.models import PostItem, PostCategory

class LatestPostBlock(Block):
  name = 'latestpost'

  @classmethod
  def render(cls, context, * args, ** kwargs):
    post_list = PostItem.all()[:3]
    return cls.render_block(template_name='block_latest.html',
                            block_title=_('Latest post'),
                            context={'post_list': post_list})

class PostCategoriesBlock(Block):
  name = 'postcategories'

  @classmethod
  def render(cls, context, * args, ** kwargs):
    categories_list = PostCategory.all()
    return cls.render_block(template_name='block_blogcategories.html',
                            block_title=_('Categories'),
                            context={'categories_list': categories_list})
