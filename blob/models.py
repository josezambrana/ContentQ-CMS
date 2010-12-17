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
  def create_blob_from_file(cls, file, user, **kwargs):
    _name = util.generate_uuid()[:6] + kwargs.pop('filename', file.name)
    return cls.create_blob(name=_name,
                       content=file.read(),
                       content_type=file.content_type,
                       user=user)
  
  @classmethod
  def create_blob(cls, name='', content=None, content_type=None, user=None):
    params = {
      'name':name,
      'slug':unicode(slugify(name)),
      'uuid':util.generate_uuid(),
      'user':user.username,
      'content':content,
      'content_type': content_type,
      #'privacy': user.privacy
    }
    blob_ref = cls(**params)
    blob_ref.put()
    return blob_ref