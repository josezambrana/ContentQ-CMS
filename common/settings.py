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

from os import path

ugettext = lambda s: s # dummy ugettext function, as said on django docs

COMMONDIR = path.dirname(path.abspath(__file__))

TEMPLATE_DIRS = (
    path.join(COMMONDIR, 'templates'),
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'common.theming.loader.load_template_source', # for enabling theme support in Merengue
    'django.template.loaders.app_directories.load_template_source',
    'django.template.loaders.filesystem.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.csrf.middleware.CsrfMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'common.context_processors.globals',
    'common.context_processors.flash',
)

# ContentQ usual installed apps. you can use this variable in your INSTALLED_APPS project settings
INSTALLED_APPS = (
     'appengine_django',
     'common',
     'test',
     'users',
)

# Status list for contents workflow.
STATUS_LIST = ['draft', 'pending', 'published']

# Privacy list for objects
PRIVACY_LEVELS = ['public', 'authenticated', 'privated']
PRIVACY_DEFAULT = 'public'

# The module to store session data
SESSION_ENGINE = 'common.sessions.engine'
SECRET_KEY = 'GAEdjangoCMSG9ycQFLAXMuhFsekE2728'
SESSION_SAVE_EVERY_REQUEST = True
SESSION_KEY = '_auth_user_id'

# The appengine_django code doesn't care about the address of memcached
# because it is a built in API for App Engine
CACHE_BACKEND = 'memcached://'

DEFAULT_THEME = 'contentq'

MEMCACHE_CONFIG = False