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

from django import forms
from pages import models

from common import forms as common_forms

class PageForm(common_forms.BaseContentForm):
  tags = forms.CharField(max_length=256, required=False)

  def __init__(self, *args, **kwargs):
    super(PageForm, self).__init__(*args, **kwargs)
    self.fields.keyOrder = ['name', 'status', 'body', 'meta_desc', 'tags']

  class Meta:
    model = models.Page
    exclude = ['uuid', 'slug', 'description', 'plain_description', 'deleted_at']