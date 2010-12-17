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

class PropertyFilter(object):
  def __init__(self, property, value):
    self.property = property
    self.value = value

  def filter(self, query):
    return query.filter("%s =" % self.property, self.value)

class CategoryFilter(PropertyFilter):
  def __init__(self, category):
    super(CategoryFilter, self).__init__('category', category)

class TagFilter(PropertyFilter):
  def __init__(self, tag):
    super(TagFilter, self).__init__('tags', tag)