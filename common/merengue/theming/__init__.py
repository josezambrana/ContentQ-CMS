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
import os
import ConfigParser
from os import path

from django.conf import settings
from django.utils._os import safe_join

from common import util
from common.models import Theme

def get_theme_root_dirs(template_dirs=None):
  """ Returns all themes root directories found """
  if not template_dirs:
    template_dirs = settings.TEMPLATE_DIRS

  for template_dir in template_dirs:
    template_path = safe_join(template_dir, 'themes')
    if os.path.isdir(template_path):
      yield template_path

def get_theme_dirs(template_dirs=None):
  """ Returns all theme directories"""
  for themes_root in get_theme_root_dirs(template_dirs):
    for theme_dir in os.listdir(themes_root):
      if path.isdir(safe_join(themes_root, theme_dir)) and \
        not theme_dir.startswith('.'):
          yield theme_dir, safe_join(themes_root, theme_dir)

def get_theme_path(directory_name=None):
  for theme_dir, theme_path in get_theme_dirs():
    if directory_name == theme_dir:
      return theme_path

def create_from_fs(path):
  """ update theme info from filesystem """
  theme_info_file = os.path.join(path, 'theme.info')
  directory_name = os.path.basename(path)

  ref = Theme.get(directory_name=directory_name)
  if ref:
    return False

  if os.path.isfile(theme_info_file):
    config = ConfigParser.ConfigParser()
    config.read(theme_info_file)
    theme_name = config.get(ConfigParser.DEFAULTSECT, 'name', directory_name)
    theme_description = config.get(ConfigParser.DEFAULTSECT, 'description')
  else:
    theme_name = directory_name
    theme_description = ''

  params = {'name': theme_name,
            'description': theme_description,
            'installed': True,
            'active': False,
            'directory_name': directory_name}
  theme_ref = Theme(**params)
  return theme_ref.put()

def check_themes():
  """ check themes found in file system and compare with registered one in database """
  # first disable all themes
  for theme in Theme.all():
    theme.installed = False
    theme.put()

  # now look for all themes in filesystem and enable them
  for theme_dir, theme_path in get_theme_dirs():
    #theme, created = Theme.objects.get_or_create(directory_name=theme_dir)
    create_from_fs(theme_path)
    
  active_theme = Theme.get_active()
  if not active_theme:
    ref = Theme.get(directory_name=settings.DEFAULT_THEME)
    ref.active = True
    ref.put()
