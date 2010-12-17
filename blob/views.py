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

from google.appengine.ext import blobstore
from google.appengine.ext.blobstore import BlobInfo

from django import http, template
from django.shortcuts import render_to_response

from blob.models import Blob

from common import decorator
from common import common_views

@decorator.admin_required
def blobinfo_upload(request):
  redirect_to = request.get_full_path()
  upload_url = blobstore.create_upload_url('/blobstore/upload')

  c = template.RequestContext(request, locals())
  return render_to_response("blob_upload.html", c)

@decorator.admin_required
def blob_admin(request):
  return common_views.content_admin(request, 'blob', model=BlobInfo, tpl='blob_admin.html')

def blob_serve(request, slug):
  _file = Blob.get(slug=slug)
  response = http.HttpResponse(content_type=_file.content_type)
  response.write(_file.content)
  return response