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

from google.appengine.api import memcache

from django import http
from django.core import exceptions
from django.core.urlresolvers import reverse, get_resolver
from django.conf import settings

from common import exception
from common import util
from common import theming
from common.models import Action, ConfigData, Permission

class VerifyInstallMiddleware(object):
  def process_request(self, request):
    if not ConfigData.get_configdata('site_installed', default=False):
      theming.check_themes()
      if not request.path.startswith('/install'):
        return http.HttpResponseRedirect(reverse('install'))
      
    if not request.path.startswith('/install'):
      for app in settings.INSTALLED_APPS:
        if not ConfigData.is_installed(app):
          try:
            Action.register_action(app)
          except exceptions.ImproperlyConfigured:
            pass #logging.error("   can not register %s actions" % app)

        if not ConfigData.is_installed(app):
          try:
            _install = util.get_attr_from("%s.config.install" % app)
            _install()
          except exceptions.ImproperlyConfigured:
            pass #logging.error("ImproperlyConfigured -> %s.config.install" % app)

          areas = util.get_config_value(app, "areas", {})
          areas_vals = sorted(areas.values(), key=lambda x: x.get("order", 1000))
          
          ConfigData.set_configdata(app, True, label='installed_app',
                                    extra={'adminareas':areas_vals})
            

class ExceptionMiddleware(object):
  def process_exception(self, request, exc):
    # Authentication Error
    if isinstance(exc, exception.AuthenticationException):
      response = http.HttpResponse()
      response.status_code = 401
      return response

    # Redirect Error
    if isinstance(exc, exception.RedirectException):
      url = exc.build_url(request)
      return http.HttpResponseRedirect(url)
    
    # Redirect Error
    if isinstance(exc, exception.Error):
      logging.warning("RedirectError: %s", traceback.format_exc())
      return util.RedirectError(request, exc.message)

    if not isinstance(exc, Http404):
      logging.error("5xx: %s", traceback.format_exc())
      
    # Shows traceback
    if settings.DEBUG and not isinstance(exc, http.Http404):
      import sys
      from django.views import debug
      exc_info = sys.exc_info()
      reporter = debug.ExceptionReporter(request, *exc_info)
      html = reporter.get_traceback_html()
      response = http.HttpResponse(html, mimetype='text/html')
      response.status_code = 500
      return response
    return None

class AuthorizationMiddleware(object):
  def process_request(self, request):
    resolver = get_resolver(None)
    pattern = self._get_pattern(resolver, request.path)
    if pattern is not None:
      request.action_pattern = pattern
      if not request.user.superuser and \
         Action.get(name=pattern.name) and \
         not Permission.can_access(request.user.roles, pattern.name):
        if request.user.username == 'anonymous':
          return util.RedirectLoginError(request, "You can not access to this page, try to login")
        logging.error("   the user %s can NOT access to %s " % (request.user.username, pattern.name))
        return util.RedirectError(request, "   the user %s can NOT access to %s " % (request.user.username, pattern.name))
    return None

  def _get_pattern(self, resolver, path):
    match = resolver.regex.search(path)
    if match:
      new_path = path[match.end():]
      if not hasattr(resolver, 'url_patterns'):
        return resolver
      else:
        for pattern in resolver.url_patterns:
          res = self._get_pattern(pattern, new_path)
          if res is not None:
            return res
    return None