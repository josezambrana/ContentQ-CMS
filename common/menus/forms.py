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

from django import forms
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from common.models import Menu, MenuItem, Block
from common import forms as common_forms

class MenuForm(common_forms.CategoryForm):
  class Meta:
    model = Menu
    exclude = ['uuid', 'slug', 'block', 'deleted_at']

  def save(self):
    block_ref = self.save_block()
    self.cleaned_data['block'] = block_ref.uuid
    return super(MenuForm, self).save()

  def save_block(self):
    if self.instance:
      block = Block.get(uuid=self.instance.block)
      block.position = self.cleaned_data['position']
      return block.put()

    params = {'name':self.cleaned_data['name'],
              'slug':slugify(self.cleaned_data['name']),
              'position':self.cleaned_data['position'],
              'model':'common.blocks.MenuBlock',
              'args':{},}

    block = Block(**params)
    return block


class MenuItemForm(common_forms.BaseForm):
  class Meta:
    model = MenuItem
    exclude = ['uuid', 'slug', 'deleted_at']
    
  def __init__(self, *args, **kwargs):
    super(MenuItemForm, self).__init__(*args, **kwargs)
    self.fields['menu'].widget = forms.Select(choices=Menu.get_choices())

    exclude = []
    if self.instance:
      exclude.append(self.instance.uuid)
    items = [('', _('Top'))] + MenuItem.get_choices(exclude=exclude)
    self.fields['parentlink'].widget = forms.Select(choices=items, attrs={'size':10})

  def save(self):
    logging.info('>> MenuItemForm.save')
    item_ref = MenuItem.get(uuid=self.cleaned_data['parentlink'])
    logging.info('   self.cleaned_data[\'parentlink\']: %s' % self.cleaned_data['parentlink'])
    logging.info("   item_ref: %s " % item_ref)
    if not item_ref:
      if self.instance:
        self.instance.parentlink = None
        self.instance.put()
    return super(MenuItemForm, self).save()
