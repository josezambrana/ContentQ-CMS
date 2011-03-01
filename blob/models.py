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

from google.appengine.api import images
from google.appengine.ext import db

from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from common.models import Base
from common import util

class Blob(Base):
  user = db.StringProperty(required=True)
  content = db.BlobProperty(required=True)
  content_type = db.StringProperty(required=True)
  #privacy = models.IntegerProperty()

  def url(self):
    return reverse('blob_serve', args=[self.uuid])

  def url_json(self):
    raise NotImplementedError

  def edit_url(self):
    raise NotImplementedError

  def delete_url(self):
    raise NotImplementedError

  @classmethod
  def create_blob_from_file(cls, file, username, **kwargs):
    _name = util.generate_uuid()[:6] + kwargs.pop('filename', file.name)
    return cls.create_blob(name=_name,
                       content=file.read(),
                       content_type=file.content_type,
                       username=username)
  
  @classmethod
  def create_blob(cls, name='', content=None, content_type=None, username=None):
    params = {
      'name':name,
      'slug':unicode(slugify(name)),
      'uuid':util.generate_uuid(),
      'user':username,
      'content':content,
      'content_type': content_type,
      #'privacy': user.privacy
    }
    blob_ref = cls(**params)
    blob_ref.put()
    return blob_ref

  @classmethod
  def create_thumbails(cls, name, content, content_type, username='admin', sizes={}):
    _name = _name = util.generate_uuid()[:6] + name
    blob_ref = cls.create_blob(_name, content, content_type, username)
    
    thumbails = {}

    for size, dimensions in sizes.iteritems(): 
      image = images.Image(blob_ref.content)

      original_width, original_height = float(image.width), float(image.height)
      width, height = dimensions
      f_width, f_height = float(width), float(height)

      if original_width > original_height:
        right_x = (f_width * original_height)/(f_height * original_width)
        bottom_y = 1.0
        if right_x > 1.0:
          bottom_y = 1.0 / right_x
          right_x = 1.0
      else:
        right_x = 1.0
        bottom_y = (f_height * original_width)/(f_width * original_height)
        if bottom_y > 1.0:
          right_x = 1.0 / bottom_y
          bottom_y = 1.0
      
      image.crop(0.0, 0.0, right_x, bottom_y)

      image.resize(width, height)

      img_content = image.execute_transforms(images.JPEG)

      thumbail_name = "thumbail_%s_%s" % (blob_ref.name, size)
      cls.create_blob(name=thumbail_name,
                      content=img_content,
                      content_type=content_type,
                      username=username)
      thumbails[size] = reverse('blob_serve', args=[thumbail_name])
    return thumbails