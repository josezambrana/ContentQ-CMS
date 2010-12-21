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

from common.models import Block
from common import util

register = template.Library()

@register.tag
def render_blocks(parser, token):
  try:
    tag_name, position, request = token.split_contents()
  except ValueError:
    raise template.TemplateSyntaxError, "%r tag requires a position argument" % token.contents.split()[0]
  if not (position[0] == position[-1] and position[0] in ('"', "'")):
    raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
  return BlockNode(position[1:-1], request)

class BlockNode(template.Node):
  def __init__(self, position, request):
    self.position = position
    self.request = template.Variable(request)
    
  def render(self, context):
    logging.info("******** BlockNode.render")
    logging.info("         self.position: %s " % self.position)
    request = self.request.resolve(context)
    blocks = Block.get_by_position(self.position, request)
    res = ''
#    try:
    for block in blocks:
      res = res + self.render_block(block, context)
#    except:
#      logging.error("error rendering blocks from: %s" % self.position)
    return res

  def render_block(self, block, context):
    logging.info("******** BlockNode.render_block")
    logging.info("         block: %s" % block)
    params = {}
    for key, arg in block.args.iteritems():
      params[str(key)] = arg
    params['name'] = block.slug
    return block.get_block_class().render(context, **params)