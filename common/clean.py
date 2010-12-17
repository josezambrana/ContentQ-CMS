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

import urlparse

from django.conf import settings

def redirect_to(value):
  if not value.startswith('/') and not value.startswith('http'):
    value = 'http://' + value

  if '\n' in value or '\r' in value:
    return '/'

  scheme, netloc, path, params, query, fragment = urlparse.urlparse(value.lower())

  if not scheme and not netloc and path:
    # Check for a relative URL, which is fine
    return value
  elif scheme in ('http', 'https'):
    if (netloc.endswith(settings.HOSTED_DOMAIN) or
        netloc.endswith(settings.GAE_DOMAIN)):
      if netloc.find('/') == -1:
        return value