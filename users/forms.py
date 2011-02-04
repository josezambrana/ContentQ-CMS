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
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from common import util
from common.forms import ModelForm, Form

from users.models import User, UserDoesNotExist, InvalidPassword
from users.mail import mail_password_instructions
from users.templatetags.avatar import avatar

class AvatarFileInput(forms.FileInput):
  user = None
  def set_user(self, user):
    self.user = user

  def render(self, name, value, attrs=None):
    html = super(AvatarFileInput, self).render(name, None, attrs=attrs)
    if self.user is not None:
      avatar_url = avatar(self.user.extra.get('avatar', None), 's')
      avatar_html = "<div class=\"avatar span\"><img src=\"%s\" alt=\"%s\"/></div>%s"
      avatar_html = avatar_html % (avatar_url, self.user.username, html)
      return mark_safe(avatar_html)
    return mark_safe(html)

class AvatarField(forms.FileField):
    widget = AvatarFileInput

    def set_user(self, user):
      self.widget.set_user(user)
    
class RegisterForm(ModelForm):
  """
  A form that creates a user, with no privileges, from the given username and password.
  """
  username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^\w+$',
    error_message = _("This value must contain only letters, numbers and underscores."))
  password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput, min_length=5, max_length=15)
  password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput)

  class Meta:
    model = User
    exclude = ['uuid', 'deleted_at', 'extra', 'superuser', 'is_superuser', 'active', 'code', 'roles', 'last_login', 'privacy', 'password']

  def clean_username(self):
    username = self.cleaned_data["username"].lower()
    try:
      User.get(username=username)
    except UserDoesNotExist:
      return username
    raise forms.ValidationError(_("A user with that username already exists."))
  
  def clean_email(self):
    email = self.cleaned_data["email"]
    try:
      User.get(email=email)
    except UserDoesNotExist:
      return email
    raise forms.ValidationError(_("A user with that email already exists."))

  def clean_password2(self):
    password1 = self.cleaned_data.get("password1", "")
    password2 = self.cleaned_data["password2"]
    if password1 != password2:
      raise forms.ValidationError(_("The two password fields didn't match."))
    return password2

  def save(self, commit=True):
    self.cleaned_data["username"] = self.cleaned_data["username"].lower()
    user = super(RegisterForm, self).save(commit=False)
    user.code = util.generate_uuid()
    user.set_password(self.cleaned_data["password1"])
    if commit:
      user.save()
    return user

class SettingsForm(ModelForm):
  avatarfield = AvatarField(label=_("Avatar"), required=False, help_text='Max file size 500 Kb')
  password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput, min_length=5, max_length=15, required=False)
  password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput, required=False)
  
  class Meta:
    model = User
    exclude = ['username', 'email', 'uuid', 'deleted_at', 'code', 'last_login', 
              'superuser', 'is_superuser', 'active', 'roles', 'privacy',
              'password', 'extra']

  def __init__(self, *args, **kwargs):
    super(SettingsForm, self).__init__(*args, **kwargs)
    self.fields.keyOrder = ('avatarfield', 'first_name', 'last_name', 'password1', 'password2')
    self.fields['password1'].initial = ''
    self.fields['password2'].initial = ''
    self.fields['avatarfield'].set_user(self.instance)

  def clean_password2(self):
    password1 = self.cleaned_data.get("password1", "")
    password2 = self.cleaned_data["password2"]
    if password1 != password2:
      raise forms.ValidationError(_("The two password fields didn't match."))
    return password2

  def save(self, commit=True):
    user = super(SettingsForm, self).save(commit=False)
    if self.cleaned_data["password1"]:
      user.set_password(self.cleaned_data["password1"])
    if commit:
      user.save()
    return user

class LoginForm(Form):
  username = forms.CharField(label=_("Username/Email"), max_length=30)
  password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

  def __init__(self, request=None, *args, **kwargs):
    self.request = request
    self.user_cache = None
    super(LoginForm, self).__init__(*args, **kwargs)

  def clean(self):
    username = self.cleaned_data.get('username')
    password = self.cleaned_data.get('password')
    
    if username and password:
      try:
        self.user_cache = User.authenticate(username=username, password=password)
      except (UserDoesNotExist, InvalidPassword):
        raise forms.ValidationError(_("Invalid username or password"))
        
      if not self.user_cache.is_active():
        raise forms.ValidationError(_("This account is inactive."))

    logging.info("   returning")
    return self.cleaned_data

  def get_user(self):
    return self.user_cache

class ForgotPasswordForm(Form):
  email = forms.EmailField()

  def clean_email(self):
    email = self.cleaned_data.get('email')
    try:
      user = User.get(email=email)
      self.user = user
    except UserDoesNotExist:
      logging.warning(" UserDoesNotExist ")
      raise forms.ValidationError(_("We could not find an account that matched that email."))
    return email
  
  def send_instructions(self):
    self.user.code = util.generate_uuid()
    self.user.put()
    mail_password_instructions(self.user, self.user.code)

class ResetPassword(Form):
  password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput, min_length=5, max_length=15, required=False)
  password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput, required=False)
  
  def __init__(self, *args, **kwargs):
    self.user = kwargs.pop('user', None)
    super(ResetPassword, self).__init__(*args, **kwargs)

  def clean_password2(self):
    password1 = self.cleaned_data.get("password1", "")
    password2 = self.cleaned_data["password2"]
    if password1 != password2:
      raise forms.ValidationError(_("The two password fields didn't match."))
    return password2

  def save(self):
    logging.info("***** Form save")
    self.user.set_password(self.cleaned_data["password1"])
    self.user.code = util.generate_uuid()
    logging.info("    * code: %s" % self.user.code)
    self.user.put()