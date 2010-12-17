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

from google.appengine.ext import db

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from common.models import BaseCategory, BaseContent, Categorizable, Commentable

class PostCategory(BaseCategory):
  class Meta:
    verbose_name = _('post category')
    verbose_name_plural = _('post categories')

  @classmethod
  def urltag(cls):
    return 'postcategory'

  @classmethod
  def subitems_admin_url(cls):
    return PostItem.admin_url()

  @classmethod
  def subitems_classname(cls):
    return PostItem.class_name()

  def url(self):
    return reverse('post_category', args=[self.slug])
  
class PostItem(BaseContent, Categorizable, Commentable):
  body = db.TextProperty(required=True)
  commentable = db.BooleanProperty(required=True, default=True)

  def is_commentable(self):
    return self.commentable

  @classmethod
  def get_latest(cls, limit=5):
    return cls.published().order('-created_at')[:limit]

  @classmethod
  def category_model(cls):
    return PostCategory
  
  @classmethod
  def urltag(cls):
    return 'post'
