# Copyright 2010 Jose Maria Zambrana Arze <contact@josezambrana.com>
# Copyright 2010 http://www.collabq.com
# Copyright 2009 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
__author__ = 'termie@google.com (Andy Smith)'

import re
import time, datetime
try:
  import cPickle as pickle
except ImportError:
  import pickle

from google.appengine.ext import db
from google.appengine.api.datastore_types import Blob

class DictProperty(db.Property):
  def validate(self, value):
    value = super(DictProperty, self).validate(value)
    if not isinstance(value, dict):
      raise Exception("NOT A DICT %s" % value)
    return value

  def default_value(self):
    return {}

  def datastore_type(self):
    return Blob

  def get_value_for_datastore(self, model_instance):
    value = super(DictProperty, self).get_value_for_datastore(model_instance)
    return Blob(pickle.dumps(value, protocol=-1))

  def make_value_from_datastore(self, model_instance):
    value = super(DictProperty, self).make_value_from_datastore(model_instance)
    return pickle.loads(str(value))
