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

"""
Loading templates from active theme looking for directories in TEMPLATE_DIRS/themes
"""
import os

from common.merengue.theming import check_themes
from common.merengue.theming import get_theme_root_dirs
from django.conf import settings
from django.template import TemplateDoesNotExist
from django.utils._os import safe_join


def get_template_sources(template_name, template_dirs=None):
  from common.models import Theme
  
  active_theme = Theme.get_active()

  if not active_theme:
    check_themes()

  for themes_dir in get_theme_root_dirs(template_dirs):
    active_theme_dir = safe_join(themes_dir, active_theme.directory_name)
    try:
      yield safe_join(active_theme_dir, template_name)
    except UnicodeDecodeError:
      raise
    except ValueError:
      pass


def load_template_source(template_name, template_dirs=None):
  tried = []
  for filepath in get_template_sources(template_name, template_dirs):
    try:
      return (open(filepath).read().decode(settings.FILE_CHARSET), filepath)
    except IOError:
      tried.append(filepath)
  if tried:
    error_msg = "Tried %s" % tried
  else:
    error_msg = "Your TEMPLATE_DIRS setting is empty. Change it to point to at least one template directory."
  raise TemplateDoesNotExist(error_msg)
load_template_source.is_usable = True
load_template_source.is_usable = True
