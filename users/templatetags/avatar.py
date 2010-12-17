import logging

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

from users.models import User

register = template.Library()

@register.filter
def avatar(value, arg=None):
  arg = arg or 's'
  if arg not in settings.AVATAR_SIZES.keys():
    arg = 's'
    
  if not value:
    return "%simg/avatar/default_%s.png" % (settings.MEDIA_URL, arg)
  
  return reverse("blob_serve", args=["%s_%s" % (value, arg)])

@register.tag
def url_avatar(parser, token):
  logging.info("**** templatetags.url_avatar")
  try:
    tag_name, username, size = token.split_contents()
    logging.info("     tag_name, username, size: %s, %s, %s" % (tag_name, username, size))
  except:
    raise template.TemplateSyntaxError, "%r tag requires a username" % token.contents.split()[0]

  return AvatarURLNode(username, size[1:-1])

class AvatarURLNode(template.Node):
  def __init__(self, username, size):
    self.username = template.Variable(username)
    self.size = size

  def render(self, context):
    username = self.username.resolve(context)

    user_ref = User.get_safe(username=username)
    _avatar = user_ref.extra.get('avatar', None)

    return avatar(_avatar, self.size)