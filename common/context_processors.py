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

from django.conf import settings
from common import util
from common.models import Theme, ConfigData

def get_global_vars():
  params = getattr(settings, 'GLOBALS')
  params.update({'SITE_NAME':ConfigData.get_configdata('SITE_NAME'),
                'SITE_DESCRIPTION':ConfigData.get_configdata('SITE_DESCRIPTION'),
                'SITE_KEYWORDS':ConfigData.get_configdata('SITE_KEYWORDS'),
                'MEDIA_URL':settings.MEDIA_URL,
                'DOMAIN':settings.DOMAIN,
                'THEME_MEDIA_URL':settings.THEME_URL + Theme.get_active().directory_name + '/'})
  return params

def globals(request):
  return get_global_vars()

def flash(request):
  flash = {
    'success': util.get_success(request),
    'notice': util.get_notice(request),
    'error': util.get_error(request),
  }
  return { 'flash': flash }