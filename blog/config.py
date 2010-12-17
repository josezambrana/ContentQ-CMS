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

from common.models import Block
from blog.models import PostItem, PostCategory

def get_content():
  return {"Post Item":PostItem.all(), "Post Category":PostCategory.all()}

def install():
  logging.error(">> installing post")
  params = {
    "name":"Hello world!",
    "slug":"hello-world",
    "plain_description":"Welcome to ContentQ CMS. This is your first post. Edit or delete it, then start blogging!",
    "description":"Welcome to ContentQ CMS. This is your first post. Edit or delete it, then start blogging!",
    "status":"published",
    "tags":[],
    "meta_desc":"hello world",
    "category":"uncategorized",
    "body":"<p>this is an example content</p>"
  }
  post_ref = PostItem(**params)
  post_ref.put()
  category_ref = PostCategory(name='Uncategorized', slug='uncategorized')
  category_ref.put()

  latestpost_ref = Block.add_model('latestpost', 'blog.blocks.LatestPostBlock')
  postcategories_ref = Block.add_model('postcategories', 'blog.blocks.PostCategoriesBlock')
  
  block = Block(name='Post Categories', slug='post-categories',
                position='rightsidebar', model='blog.blocks.PostCategoriesBlock',
                args={})
  block.save()
