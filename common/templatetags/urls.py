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
from django.core.urlresolvers import reverse

register = template.Library()

@register.tag
def url_for(parser, token):
  try:
    tag_name, linkname = token.split_contents()
  except ValueError:
    raise template.TemplateSyntaxError, "%r tag requires a position argument" % token.contents.split()[0]
  except:
    pass
  return URLForNode(linkname)

class URLForNode(template.Node):
  def __init__(self, linkname):
    self.linkname = template.Variable(linkname)

  def render(self, context):
    linkname = self.linkname.resolve(context)
    return reverse(linkname)