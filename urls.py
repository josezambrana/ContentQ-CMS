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

from django.conf.urls.defaults import *

urlpatterns = patterns('',)

urlpatterns += patterns('', (r'^', include('common.urls')))

# front
urlpatterns += patterns('front.views', url(r'^$', 'page_front', name='front'),)

# blob
urlpatterns += patterns('', (r'media/', include('blob.urls')))

# contact
urlpatterns += patterns('', (r'contact/', include('contact.urls')))

# users
urlpatterns += patterns('', (r'users/', include('users.urls')))

# blog
urlpatterns += patterns('', (r'^blog/', include('blog.urls')),)

# pages
urlpatterns += patterns('', (r'^pages/', include('pages.urls')),)

#Server Errors
handler404 = 'common.common_views.error_404'
handler500 = 'common.common_views.error_500'