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
from google.appengine.api import images

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import get_hexdigest, check_password

from blob.models import Blob

from common import models
from common import properties

class UserDoesNotExist(Exception):
  pass

class AnonymousUser(object):
  username = 'anonymous'
  first_name = ''
  last_name = ''
  roles = ['anonymous']
  superuser = False
  extra = {}

  def __nonzero__(self):
    return False
  
class User(models.BaseModel):
  username = db.StringProperty(required=True)
  first_name = db.StringProperty(required=True)
  last_name = db.StringProperty(required=True)
  email = db.EmailProperty(required=True)
  password = db.StringProperty()
  active = db.BooleanProperty(required=True, default=True)
  code = db.StringProperty()
  last_login = db.DateTimeProperty(auto_now_add=True, required=True)
  
  superuser = db.BooleanProperty(required=True, default=False)
  roles = db.StringListProperty(required=True, default=['authenticated'])
  
  privacy = db.StringProperty(required=True, default=settings.PRIVACY_DEFAULT)
  extra = properties.DictProperty(default={})
  
  def set_password(self, raw_password):
    import random
    salt = get_hexdigest('sha1', str(random.random()), str(random.random()))[:5]
    hsh = get_hexdigest('sha1', salt, raw_password)
    self.password = '%s$%s$%s' % ('sha1', salt, hsh)

  def check_password(self, raw_password):
    return check_password(raw_password, self.password)

  def is_active(self):
    return self.active
  
  def is_active(self):
    return self.active

  def is_admin(self):
    return self.superuser or 'administrator' in self.roles

  def url(self):
    return reverse('users_profile_username', args=[self.username])

  def create_avatar(self, avatar):
    blob_ref = Blob.create_blob_from_file(avatar, self, filename=self.username)
    self.set_avatar("avatar_%s" % blob_ref.name)
    
    for size, dimensions in settings.AVATAR_SIZES.iteritems():
      image = images.Image(blob_ref.content)
      
      original_width, original_height = float(image.width), float(image.height)
      if original_width > original_height:
        right_x = original_height/original_width
        bottom_y = 1.0
      else:
        right_x = 1.0
        bottom_y = original_width/original_height

      image.crop(0.0, 0.0, right_x, bottom_y)

      width, height = dimensions
      image.resize(width, height)
      
      img_content = image.execute_transforms(images.JPEG)
                         
      Blob.create_blob(name= "avatar_%s_%s" % (blob_ref.name, size),
                       content=img_content,
                       content_type="image/jpeg",
                       user=self)
    
  def set_avatar(self, avatar):
    self.extra['avatar'] = avatar
    self.put()

  @classmethod
  def get_user_from_request(cls, request):
    user_ref = AnonymousUser()
    if settings.SESSION_KEY in request.session:
      user_ref = cls.get(request.session[settings.SESSION_KEY])
    return user_ref
    

  @classmethod
  def authenticate(cls, username=None, password=None):
    user = cls.get_safe(username=username)
    if not user:
      try:
        user = cls.get(email=username)
      except UserDoesNotExist:
        return None
      
    if user.check_password(password):
      return user
    return None

  @classmethod
  def get(cls, *args, **kwargs):
    ref = super(User, cls).get(*args, **kwargs)
    if ref is None:
      raise UserDoesNotExist
    return ref

  @classmethod
  def get_safe(cls, *args, **kwargs):
    try:
      ref = cls.get(*args, **kwargs)
    except UserDoesNotExist:
      ref = AnonymousUser()
      
    return ref
  