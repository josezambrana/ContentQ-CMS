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

from django import http, template
from django.template import loader
from django.utils.translation import ugettext as _

from common import util

from blog.models import PostItem

def page_front(request):
  area="front"
  topnews = PostItem.get_latest()
  words_num = 30
  page = "front"

  items = util.paginate(request, PostItem.get_latest())
  
  c = template.RequestContext(request, locals())
  t = loader.get_template('front.html')
  return http.HttpResponse(t.render(c))
