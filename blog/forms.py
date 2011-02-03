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

from google.appengine.ext.db import djangoforms

from django import forms
from blog import models

from common.forms import BaseContentForm, CategoryForm

TYPE_CHOICES = (('page','Page'),('post','Post'))

class PostCategoryForm(CategoryForm):
  class Meta(CategoryForm.Meta):
    model = models.PostCategory
  
class PostItemForm(BaseContentForm):
  class Meta(BaseContentForm.Meta):
    model = models.PostItem
    
  def __init__(self, *args, **kwargs):
    super(PostItemForm, self).__init__(*args, **kwargs)
    self.fields['category'].widget = forms.Select(choices=models.PostCategory.get_choices())
    self.fields.keyOrder = ["name", "category", "status","description", "body", "tags", "meta_desc"]
