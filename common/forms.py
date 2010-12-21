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

from google.appengine.ext.db import djangoforms

import logging

from django import forms
from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from common.models import Block, MenuItem, Theme, ConfigData, Comment
from common.widgets import SelectMultiple
from common import util

from users.models import User, UserDoesNotExist

from beautifulsoup.BeautifulSoup import BeautifulSoup

class StringListProperty(djangoforms.StringListProperty):
  __metaclass__ = djangoforms.monkey_patch

  def get_value_for_form(self, instance):
    logging.info(">> StringListProperty.get_value_for_form ")
    value = super(StringListProperty, self).get_value_for_form(instance)
    if not value:
     return None
    if isinstance(value, list):
     value = ', '.join(value)
    return value

  def make_value_from_form(self, value):
    logging.info(">> StringListProperty.make_value_from_form ")
    if not value:
      return []
    if isinstance(value, basestring):
      value = util.get_tags(value.lower())
    return value

class Input(forms.widgets.Input):
  __metaclass__ = djangoforms.monkey_patch
  
  def build_attrs(self, extra_attrs=None, **kwargs):
    attrs = super(Input, self).build_attrs(extra_attrs=extra_attrs, **kwargs)
    
    _class = attrs.get('class', '')
    if _class:
      _class = "%s %s" % (_class, self.input_type)
    else:
      _class = self.input_type
      
    attrs.update({'class':_class})
    return attrs
      
class Form(forms.Form):
  __metaclass__ = djangoforms.monkey_patch

class ModelForm(djangoforms.ModelForm):
  __metaclass__ = djangoforms.monkey_patch

class CategoryForm(ModelForm):
  class Meta:
    exclude = ['uuid', 'slug', 'created_at', 'updated_at', 'deleted_at']

  def save(self):
    if self.instance is None:
      params = {'slug':unicode(slugify(self.cleaned_data['name']))}
      self.cleaned_data.update(params)
      
    return super(CategoryForm, self).save()

class BaseForm(ModelForm):
  class Meta:
    exclude = ['uuid', 'slug', 'created_at', 'updated_at', 'deleted_at']

  def __init__(self, *args, **kwargs):
    res = super(BaseForm, self).__init__(*args, **kwargs)
    return res
  
  def clean(self):
    data = self.cleaned_data
    if 'name' in data:
      data['slug'] = unicode(slugify(data['name']))
    else:
      raise forms.ValidationError(_("Name is required"))
    return data
  
  def save(self):
    if self.instance is None:
      params = {'uuid':util.generate_uuid()}
      self.cleaned_data.update(params)
      
    return super(BaseForm, self).save()
  
class BaseContentForm(BaseForm):
  class Meta:
    exclude = ['uuid', 'slug', 'plain_description', 'created_at', 'updated_at', 'deleted_at']

  def __init__(self, *args, **kwargs):
    logging.info(">> BaseContentForm")
    super(BaseContentForm, self).__init__(*args, **kwargs)
    self.fields['tags'].widget = forms.TextInput()
    self.fields['meta_desc'].widget = forms.Textarea(attrs={'class':'ckexclude'})

  def save(self):
    plain_description = ''
    if 'description' in self.cleaned_data:
      plain_description = mark_safe(''.join(BeautifulSoup(self.cleaned_data['description']).findAll(text=True)))
    params = {"plain_description":plain_description}
    self.cleaned_data.update(params)
    return super(BaseContentForm, self).save()
  
class CommentForm(ModelForm):
  class Meta:
    model = Comment
    exclude = ['uuid', 'author', 'owner', 'deleted_at', 'content', 'content_type']

  def __init__(self, *args, **kwargs):
    self.extra_params = {}
    if "extra_params" in kwargs:
      self.extra_params = kwargs.pop("extra_params")
    super(CommentForm, self).__init__(*args, **kwargs)
    
  def save(self):
    self.cleaned_data.update(self.extra_params)
    return super(CommentForm, self).save()
    
class BlockNewForm(BaseForm):
  class Meta:
    model = Block
    exclude = ['uuid', 'slug', 'args', 'deleted_at', 'params']

  def __init__(self, *args, **kwargs):
    super(BlockNewForm, self).__init__(*args, **kwargs)
    self.fields['menus'].widget = forms.RadioSelect(choices=settings.BLOCK_MENUS_OPTION.items(),
                                                    attrs={'class':'radioselect'})
    attrs={'disabled':'disabled'}
    self.fields['visibility'].widget = SelectMultiple(choices=MenuItem.get_choices(), attrs=attrs)
    self.fields['model'].widget = forms.Select(choices=Block.get_models_choices())

  def save(self):
    if not self.cleaned_data['visibility'] == '[]':
      self.cleaned_data['visibility'] = util.get_tags(self.cleaned_data['visibility'])
    else:
      self.cleaned_data['visibility'] = []
    return super(BlockNewForm, self).save()

class BlockForm(BaseForm):
  class Meta:
    model = Block
    exclude = ['uuid', 'slug', 'model', 'args', 'deleted_at', 'params']

  def __init__(self, *args, **kwargs):
    super(BlockForm, self).__init__(*args, **kwargs)
    self.fields['menus'].widget = forms.RadioSelect(choices=settings.BLOCK_MENUS_OPTION.items(),
                                                    attrs={'class':'radioselect'})
    attrs = {}
    if self.instance.menus == 'all' or self.instance.menus == 'none':
      attrs={'disabled':'disabled'}
    self.fields['visibility'].widget = SelectMultiple(choices=MenuItem.get_choices(), attrs=attrs)

  def save(self):
    if not self.cleaned_data['visibility'] == '[]':
      self.cleaned_data['visibility'] = util.get_tags(self.cleaned_data['visibility'])
    else:
      self.cleaned_data['visibility'] = []
    return super(BlockForm, self).save()

class StaticBlockForm(BlockForm):
  static_content = forms.CharField(widget=forms.Textarea, label=_("Static Content"))
  
  class Meta:
    model = Block
    exclude = ['uuid', 'slug', 'model', 'args', 'deleted_at']
  
  def __init__(self, *args, **kwargs):
    logging.info("****** common.forms.StaticBlockForm")
    super(StaticBlockForm, self).__init__(*args, **kwargs)
    logging.info("       instance: %s " % self.instance)
    logging.info("       params: %s " % self.instance.params)
    self.fields['static_content'].initial = self.instance.params.get('content', '')
    self.fields.keyOrder = ['name', 'position', 'menus', 'visibility', 'order', 'static_content']
    
  def save(self):
    logging.info("** common.forms.StaticBlockForm")
    block_ref = super(StaticBlockForm, self).save()
    block_ref.params['content'] = self.cleaned_data['static_content']
    block_ref.put()
    return block_ref

class AdminSiteForm(Form):
  site_name = forms.CharField()
  meta_description = forms.CharField(widget=forms.Textarea)
  meta_keywords = forms.CharField(widget=forms.Textarea)
  theme = forms.ChoiceField(choices=Theme.get_choices())
  
  def __init__(self, *args, **kwargs):
    logging.info(">> AdminSiteForm")
    super(AdminSiteForm, self).__init__(*args, **kwargs)
    self.fields['site_name'].initial = ConfigData.get_configdata('SITE_NAME')
    self.fields['meta_description'].initial = ConfigData.get_configdata('SITE_DESCRIPTION')
    self.fields['meta_keywords'].initial = ConfigData.get_configdata('SITE_KEYWORDS')
    self.fields['theme'].widget = forms.Select(choices=Theme.get_choices())
    self.fields['theme'].initial = Theme.get_active().uuid

  def save(self):
    ConfigData.set_configdata('SITE_NAME', self.cleaned_data['site_name'])
    ConfigData.set_configdata('SITE_DESCRIPTION', self.cleaned_data['meta_description'])
    ConfigData.set_configdata('SITE_KEYWORDS', self.cleaned_data['meta_keywords'])
    Theme.check_for_duplicated_active_themes(self.cleaned_data['theme'])
    return True

class InstallForm(AdminSiteForm):
  username = forms.RegexField(label=_("Admin Username"), max_length=30, regex=r'^\w+$',
    error_message = _("This value must contain only letters, numbers and underscores."))
  first_name = forms.CharField(label=_("First Name"))
  last_name = forms.CharField(label=_("Last Name"))
  email = forms.EmailField(label=_("Email"))
  password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput, min_length=5, max_length=15)
  password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput)
  
  class Meta:
    fields = ("site_name", "meta_description", "meta_keywords", "theme",
              "username", "first_name", "last_name", "email")

  def __init__(self, *args, **kwargs):
    super(InstallForm, self).__init__(*args, **kwargs)
    self.fields['username'].initial = 'admin'
    
  def clean_username(self):
    username = self.cleaned_data["username"].lower()
    try:
      User.get(username=username)
    except UserDoesNotExist:
      return username.lower()
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

  def save(self):
    super(InstallForm, self).save()
    params = {"username":self.cleaned_data["username"].lower(),
              "first_name":self.cleaned_data["first_name"],
              "last_name":self.cleaned_data["last_name"],
              "email":self.cleaned_data["email"],
              "active":True,
              "superuser":True,
              "roles":['authenticated', 'administrator']}
    user = User(**params)
    user.code = util.generate_uuid()
    user.set_password(self.cleaned_data["password1"])
    user.save()
    ConfigData.set_configdata('ADMIN_USERNAME', user.username)
    return user