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

import os
from common.settings import *

APP_ID = 'contentq-dev'

ugettext = lambda s: s # dummy ugettext function, as said on django docs

BASEDIR = path.dirname(path.abspath(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR = False
HTTP_ERRORS_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'appengine'  # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Madrid'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

SITE_ID = 1
SITE_REGISTER_ID = 2
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'
THEME_URL = '/themes/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '*^t=5_u0c#-06calw!9^6*eg8+1&9sxbye@=umutgn^t_sg_nx'

# Ensure that email is not sent via SMTP by default to match the standard App
# Engine SDK behaviour. If you want to sent email via SMTP then add the name of
# your mailserver here.
EMAIL_HOST = ''

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
    'common.middleware.VerifyInstallMiddleware',
    'users.middleware.AuthenticationMiddleware',
    'common.middleware.ExceptionMiddleware',
    'common.middleware.AuthorizationMiddleware',
)

TEMPLATE_DIRS = (
  path.join(BASEDIR, 'templates'),
) + TEMPLATE_DIRS

TEMPLATE_CONTEXT_PROCESSORS = (
) + TEMPLATE_CONTEXT_PROCESSORS

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/account/login/'

INSTALLED_APPS += (
  'blog',
  'front',
  'pages',
  'blob',
  'contact',
)

ROOT_URLCONF = 'urls'

SECRET_KEY = 'collabuzzbG9ycQFLAXMu3jfHS84'

############################################
# Other Variables
############################################

BLOCK_POSITIONS = ['adminsidebar',
                   'header',
                   'mainmenu',
                   'homepage',
                   'leftsidebar',
                   'rightsidebar',
                   'footer']
                   
BLOCK_MENUS_OPTION = {'all':'All', 'none':'None',
                      'select': 'Select Menu Item(s) from the List'}
                      
# Config DOMAIN
GAE_DOMAIN = "%s.appspot.com" % APP_ID
HOSTED_DOMAIN = "collabqcms.com"
DEFAULT_HOSTED_SUBDOMAIN = 'www'
HOSTED_DOMAIN_ENABLED = False

if HOSTED_DOMAIN_ENABLED:
  DOMAIN = '%s.%s' % (DEFAULT_HOSTED_SUBDOMAIN, HOSTED_DOMAIN)
else:
  DOMAIN = GAE_DOMAIN

###### APP VARS ######
SITE_NAME = 'ContentQ'
SITE_DESCRIPTION = 'ContentQ CMS is an open source cloud CMS to manage a site on google app engine'
SITE_KEYWORDS = 'ContentQ, Google App Engine, CMS, Django, GAE, Cloud'

SITE_MAIL = 'contact@josezambrana.com'
DEFAULT_FROM_EMAIL = SITE_MAIL

AVATAR_SIZES = {'u':(30, 30),
                's':(50, 50),
                'm':(75, 75),
                'l':(175, 175)}
                
###### END VARS ######

MANAGE_PY = os.path.exists('manage.py')

# Set up the settings for the dev server if we are running it
if MANAGE_PY:
  try:
    from dev_settings import *
  except ImportError:
    pass

# Allow local overrides, useful for testing during development
try:
  from local_settings import *
except ImportError:
  pass

GLOBALS = { 'DEBUG':DEBUG,
            'DOMAIN':DOMAIN,
            'GAE_DOMAIN':GAE_DOMAIN,
            'SITE_NAME':SITE_NAME,
            'SITE_DESCRIPTION':SITE_DESCRIPTION,
            'MEDIA_URL':MEDIA_URL,
            'LANGUAGE_CODE':LANGUAGE_CODE,
          }
