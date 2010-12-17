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
from django import template

from common.models import Menu

register = template.Library()

@register.tag
def render_menu(parse, token):
  try:
    tag_name, request, name = token.split_contents()
  except ValueError:
    raise template.TemplateSyntaxError, "%r tag requires two arguments" % token.contents.split()[0]
  return MenuNode(request, name)

class MenuNode(template.Node):
  def __init__(self, request, name):
    self.request = template.Variable(request)
    self.name = template.Variable(name)

  def render(self, context):
    menu = Menu.get(name=self.name.resolve(context))
    res = "<ul id=\"menu-%s\" class=\"menu clearfix %s\">" % (menu.key().id(), menu.name)
    items = menu.top_items()
    for item in items:
      res = res + MenuNode.render_item(self.request.resolve(context), item, context)
    res = res + "</ul>"
    return res

  @classmethod
  def render_item(cls, request, item, context):
    res = "<li id=\"menuitem-%s\" class=\"menuitem" % item.key().id()
    if item.current(request):
      res += ' current'
    res += ('"><a href="%s"><span>%s</span></a>' % (item.link, item.name))

    if item.has_childs():
      res += "<ul class=\"submenu clearfix\">"
      res += "<li class=\"first\"></li>"
      for child in item.get_childs():
        res += cls.render_item(request, child, context)
      res += "<li class=\"last\"></li></ul>"
      
    res += "</li>"

    return res