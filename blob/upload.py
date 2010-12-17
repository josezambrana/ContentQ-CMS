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

import urllib
import logging

from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app

__author__="Jose Maria Zambrana Arze <contact@josezambrana.com>"
__date__ ="$29-09-2010 02:39:57 PM$"

logging.info(" upload.py ".center(60, '*'))

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    upload_files = self.get_uploads('file')
    blob_info = upload_files[0]
    _url = '/blobstore/serve/%s/%s' % (blob_info.key(), blob_info.filename)
    logging.info("   _url: %s " % _url)
    self.redirect('/media/admin')

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource, filename):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)

def main():
  application = webapp.WSGIApplication(
    [('/blobstore/upload', UploadHandler),
     ('/blobstore/serve/([^/]+)/([^/]+)', ServeHandler),
    ], debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()