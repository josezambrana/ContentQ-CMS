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

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from common.models import Menu, ConfigData

class BaseBlock:
  @classmethod
  def render_block(cls, template_name='block.html', block_title=None, context=None):
    if context is None:
      context = {}
            
    block_context = {
      'block_title': block_title,
      'block': {"name":block_title},
    }
    context.update(block_context)
    return render_to_string(template_name, context)


class Block(BaseBlock):
  @classmethod
  def render(cls, place, context, * args, ** kwargs):
    raise NotImplementedError()

class MenuBlock(Block):
  @classmethod
  def render(cls, context, name=''):
    menu = Menu.get(name=name)
    context.update({'menu': menu})
    return cls.render_block(template_name='block_menu.html',
                            block_title=_(name),
                            context=context)

class UserMenuBlock(Block):
  @classmethod
  def render(cls, context, name=''):
    return cls.render_block(template_name='block_usermenu.html',
                            block_title=_(name),
                            context=context)

class AdminMenuBlock(Block):
  @classmethod
  def render(cls, context, name=''):
    adminareas = []
    for app in settings.INSTALLED_APPS:
      _config = ConfigData.get(name=app, label='installed_app')
      if _config:
        adminareas += _config.extra.get('adminareas', [])

    context.update({"adminareas":adminareas})
    return cls.render_block(template_name='block_adminmenu.html',
                            block_title=_(name),
                            context=context)