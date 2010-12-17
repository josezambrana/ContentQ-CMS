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

from django import template
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect

from common import clean
from common import common_views
from common import util

from common.models import ConfigData
from common.exception import UnableActionError

from users import decorator as user_decorator
from users import authenticate, logout as _logout
from users.mail import mail_welcome
from users.models import User, UserDoesNotExist
from users.forms import ForgotPasswordForm, ResetPassword, LoginForm, RegisterForm, SettingsForm

@user_decorator.logout_required
def login(request):

  redirect_to = request.REQUEST.get('redirect_to', reverse('front'))
  redirect_to = clean.redirect_to(redirect_to)

  form = LoginForm()
  if request.method == 'POST':
    form = LoginForm(data=request.POST)
    if form.is_valid():
      user = form.get_user()
      authenticate(request, user)
      util.set_flash(request, "success_users_login")
      return redirect(redirect_to)
  
  c = template.RequestContext(request, locals())
  return render_to_response('users_login.html', c)

def logout(request):
  if request.user:
    _logout(request)
    util.set_flash(request, "success_users_logout")
  else:
    util.set_flash(request, "error_users_alreadyloggedout", type='error')
    
  return redirect(reverse('front'))

@user_decorator.logout_required
def register(request):
  form = RegisterForm()
  if request.method == 'POST':
    form = RegisterForm(request.POST)
    if form.is_valid():
      user = form.save()
      mail_welcome(user)
      authenticate(request, user)
      util.add_success(request, "Welcome to %s" % ConfigData.get_configdata('SITE_NAME'))
      return redirect(reverse('admin_dashboard'))

  c = template.RequestContext(request, locals())
  return render_to_response('users_register.html', c)

@user_decorator.login_required
def profile(request, username=None):
  logging.info("** users.views.profile ")
  logging.info("   username: %s " % username)
  user = request.user
  if username is not None:
    user = User.get(username=username)
  logging.info("   user: %s" % user.username)

  c = template.RequestContext(request, locals())
  return render_to_response('users_profile.html', c)

@user_decorator.login_required
def settings(request):
  logging.info("** users.views.settings ")
  user = request.user
  form = SettingsForm(instance=request.user)
  if request.method == 'POST':
    form = SettingsForm(request.POST, instance=request.user)
    if form.is_valid():
      user_ref = form.save()
      avatar = request.FILES.get('avatarfield')
      if avatar is not None:
        user_ref.create_avatar(avatar)
      util.set_flash(request, "success_users_settings")
      return redirect(reverse('users_settings'))
      
  c = template.RequestContext(request, locals())
  return render_to_response('users_settings.html', c)


def admin(request):
  return common_views.content_admin(request, 'users', User, tpl='users_admin.html')

def forgot(request):
  form = ForgotPasswordForm()
  if request.method == 'POST':
    form = ForgotPasswordForm(request.POST)
    if form.is_valid():
      form.send_instructions()
      util.set_flash(request, "success_users_forgot")
      return redirect(reverse("success"))

  c = template.RequestContext(request, locals())
  return render_to_response('users_forgot.html', c)

def passwordreset(request, code):
  try:
    user_ref = User.get(code=code)
  except UserDoesNotExist:
    raise UnableActionError
  
  form = ResetPassword(user=None)
  if request.method == 'POST':
    form = ResetPassword(request.POST, user=user_ref)
    if form.is_valid():
      form.save()
      util.add_success(request, 'success_users_passwordreset')
      return redirect(reverse("success"))

  c = template.RequestContext(request, locals())
  return render_to_response('users_passwordreset.html', c)