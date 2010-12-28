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
from operator import itemgetter
from datetime import datetime

from appengine_django import models

from google.appengine.ext import db
from google.appengine.api import memcache

from common import properties
from common import util

from django.conf import settings
from django.core import exceptions
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

class BaseModel(models.BaseModel):
  uuid = db.StringProperty(required=True)
  created_at = db.DateTimeProperty(auto_now_add=True)
  updated_at = db.DateTimeProperty(auto_now=True)
  deleted_at = db.DateTimeProperty()
  
  key_template = '%(uuid)s'

  class Meta:
    verbose_name = _('item')
    verbose_name_plural = _('items')
    
  def __init__(self, *args, **kw):
    if not 'uuid' in kw or not kw['uuid']:
      kw['uuid'] = util.generate_uuid()
      
    if not 'key_name' in kw and 'key' not in kw:
      kw['key_name'] = self.key_from(**kw)
      
    super(BaseModel, self).__init__(*args, **kw)

  @classmethod
  def key_from(cls, **kw):
    if hasattr(cls, 'key_template'):
      try:
        return cls.key_template % kw
      except KeyError:
        logging.warn('Automatic key_name generation failed: %s <- %s',
                     cls.key_template, kw)
    return None
  
  @classmethod
  def get(cls, *args, **kwargs):
    if args:
      return super(BaseModel, cls).get(*args)
    all_content = cls.all()
    for k, v in kwargs.iteritems():
      all_content.filter(k, v)
    obj_ref = all_content.get()
    if obj_ref:
      return obj_ref
    return None
  
  @classmethod
  def all(cls):
    return super(BaseModel, cls).all().filter('deleted_at', None)

  @classmethod
  def filter(cls, *args, **kwargs):
    return super(BaseModel, cls).all().filter(*args, **kwargs)
    
  def delete(self):
    self.deleted_at = datetime.now()
    self.put()

  def save(self):
    return self.put()

  @classmethod
  def object_name(cls, lower=True):
    return cls.class_name(lower=lower)

  @classmethod
  def class_name(cls, lower=False):
    if lower:
      return cls._meta.object_name.lower()
    return cls._meta.object_name

class Theme(BaseModel):
  name = db.StringProperty(required=True)
  description = db.TextProperty(required=True)
  installed = db.BooleanProperty()
  active = db.BooleanProperty(default=False)
  directory_name = db.StringProperty(required=True)

  key_template = '%(directory_name)s'

  def __unicode__(self):
    return self.name

  def get_theme_media_url(self):
    return '%s%s/' % (settings.THEME_URL, self.directory_name)

  @classmethod
  def get_admin(cls):
    return cls.get(directory_name=settings.DEFAULT_THEME)
  
  @classmethod
  def get_active(cls):
    return super(Theme, cls).get(active=True)
  
  @classmethod
  def get_choices(cls):
    return [(item.uuid, item.name) for item in cls.all()]

  @classmethod
  def check_for_duplicated_active_themes(cls, uuid):
    logging.info(">> check_for_duplicated_active_themes")
    instance = cls.get(uuid=uuid)
    instance.active = True
    instance.put()
    logging.info("   instance: %s" % instance.name)
    
    for theme in cls.all().filter('active =', True):
      if theme.uuid != instance.uuid:
        theme.active = False
        theme.put()

class ConfigData(BaseModel):
  name = db.StringProperty(required=True)
  order = db.IntegerProperty(required=True, default=0)
  extra = properties.DictProperty()
  label = db.StringProperty(required=True)

  key_template = '%(label)s/%(name)s'

  def get_value(self):
    return self.extra.get('value', None)

  @classmethod
  def set_configdata(cls, name, value, order=0, label='global', extra={}):
    _key = "configdata_%s_%s" % (label, name)
    configdata_ref = cls.get(name=name, label=label)

    if not configdata_ref:
      configdata_ref = cls(name=name, order=order,
                           extra={}, label=label)

    if extra:
      configdata_ref.extra.update(extra)

    configdata_ref.extra.setdefault('value', value)
    configdata_ref.extra['value'] = value
    configdata_ref.put()

    if settings.MEMCACHE_CONFIG:
      memcache.delete(_key)
      memcache.set(_key, value)

    return configdata_ref

  @classmethod
  def get_configdata(cls, name, default=None, label='global'):
    _key = "configdata_%s_%s" % (label, name)
    if settings.MEMCACHE_CONFIG:
      value = memcache.get(_key)
      if value is not None:
        return value

    _ref = cls.get(name=name, label=label)
    if _ref:
      return _ref.get_value()

    if label == 'global' and default is None:
      try:
        default = getattr(settings, name)
      except AttributeError:
        logging.warning("AttributeError, %s is not in settings" % name)

    res = default

    if settings.MEMCACHE_CONFIG:
      memcache.set(_key, res)

    return res

  @classmethod
  def get_data(cls, label):
    return cls.filter("label =", label)

  @classmethod
  def is_installed(cls, appname):
    return cls.get_configdata(appname, False, label='installed_app')


  @classmethod
  def set_installed(cls, appname):
    return cls.set_configdata(appname, True, label='installed_app')

  @classmethod
  def admin_url(cls):
    return reverse('config_admin')

  def active_url(self):
    return reverse('config_active', args=[self.uuid])

  def desactive_url(self):
    return reverse('config_desactive', args=[self.uuid])

class Base(BaseModel):
  name = db.StringProperty(verbose_name=_('name'), required=True)
  slug = db.StringProperty(verbose_name=_('slug'), required=True)

  def __str__(self):
    return self.name or ugettext('Without name')

  def __unicode__(self):
    return self.name or ugettext('Without name')

  def urltag(self):
    raise NotImplementedError

  def url(self):
    return reverse('%s_show' % self.urltag(), args=[self.slug])

  def url_json(self):
    return reverse('%s_show_format' % self.urltag(), args=[self.slug, 'json'])

  def edit_url(self):
    return reverse('%s_edit' % self.urltag(), args=[self.slug])

  def delete_url(self):
    return reverse('%s_delete' % self.urltag(), args=[self.slug])

  @classmethod
  def new_url(cls):
    return reverse('%s_new' % cls.urltag())

  @classmethod
  def admin_url(cls):
    return reverse('%s_admin' % cls.urltag())

class BaseCategory(Base):
  class Meta:
    verbose_name = _('base category')
    verbose_name_plural = _('base categories')

  @classmethod
  def get_choices(cls):
    return [(item.slug, item.name) for item in cls.all()]

  @classmethod
  def subitems_admin_url(cls):
    raise NotImplementedError

  @classmethod
  def subitems_classname(cls):
    raise NotImplementedError
    
class Categorizable(models.BaseModel):
  category = db.StringProperty(required=True)

  @classmethod
  def category_admin(cls):
    return cls.category_model().admin_url()

  @classmethod
  def category_model(cls):
    raise NotImplementedError

  def get_category(self):
    return self.category_model().get(slug=self.category)

class BaseContent(Base):
  plain_description = db.TextProperty(verbose_name=_('description'))
  description = db.TextProperty(verbose_name=_('description'))

  status = db.StringProperty(verbose_name=_('Publication status'),
                             choices=settings.STATUS_LIST,
                             default='published')
                             
  tags = db.StringListProperty(verbose_name=_('Tags'))
  meta_desc = db.TextProperty(verbose_name=_('meta description'))

  owner = db.StringProperty(required=True,
                default=ConfigData.get_configdata('ADMIN_USERNAME', default='admin'),
                verbose_name=_('Owner'))

  def is_published(self):
    return self.status == 'published'

  @classmethod
  def published(cls):
    return cls.all().filter('status =', 'published')

class Comment(BaseModel):
  comment = db.TextProperty(required=True, verbose_name=_('Comment'))
  content = db.StringProperty(required=True)
  content_type = db.StringProperty(required=True)

  author = db.StringProperty(required=True)
  owner = db.StringProperty(required=True,
              default=ConfigData.get_configdata('ADMIN_USERNAME',
                                                default='admin'))

class Commentable:
  def is_commentable(self):
    return True
  
  def add_comment(self, author, comment):
    comment_ref = Comment(author=author, comment=comment, content_type=self.urltag())
    comment_ref.put()
    return comment_ref

  def get_comments(self):
    return Comment.all().filter("content_type =", self.urltag()).filter("content =", self.uuid).order('created_at')

class Block(Base):
  position = db.StringProperty(required=True, choices=settings.BLOCK_POSITIONS)
  model = db.StringProperty(required=True)
  args = properties.DictProperty()
  menus = db.StringProperty(default='all', choices=settings.BLOCK_MENUS_OPTION.keys())
  visibility = db.StringListProperty()

  params = properties.DictProperty(default={})

  active = db.BooleanProperty(default=True)
  order = db.IntegerProperty(required=True, default=0)
  
  key_template = '%(model)s/%(slug)s'
  
  def __unicode__(self):
    return self.name

  def __str__(self):
    return self.name

  @classmethod
  def urltag(cls):
    return 'blocks'

  @classmethod
  def get_by_position(self, position, request):
    items = Block.all().filter('active', True).filter('position =', position).order('order')
    try:
      return [item for item in items if item.is_visible(request.get_full_path())]
    except:
      return None

  @classmethod
  def add_model(self, name, model_path):
    _ref = ConfigData.set_configdata(name, model_path, label='model_block')
    return _ref

  @classmethod
  def get_models_choices(cls):
    return [(x.get_value(), x.name) for x in ConfigData.get_data('model_block')]

  def unpublish(self):
    self.active = False
    self.put()

  def publish(self):
    self.active = True
    self.put()

  def get_block_class(self):
    logging.info("**** common.models.Block.get_block_class")
    return util.get_attr_from_safe(self.model)

  def get_block_form(self):
    logging.info("**** common.models.Block.get_block_form")
    _class = self.get_block_class()
    logging.info("     _class: %s " % _class)
    _form = _class.get_form()
    logging.info("     _form: %s " % _form)
    return self.get_block_class().get_form()

  def put(self):
    return super(Block, self).put()
  
  def save(self):
    return super(Block, self).save()

  def publish_url(self):
    return reverse('blocks_publish', args=[self.uuid])

  def unpublish_url(self):
    return reverse('blocks_unpublish', args=[self.uuid])

  def is_visible(self, url):
    if self.menus == 'all':
      return True;
    elif self.menus == 'none':
      return False
    menuitem = MenuItem.get_by_url(url)
    if menuitem:
      if menuitem.uuid in self.visibility:
        return True
    return False

class Menu(BaseCategory):
  position = db.StringProperty(choices=settings.BLOCK_POSITIONS)
  block = db.StringProperty()

  key_template = '%(slug)s'
  
  def items(self):
    return MenuItem.all().filter('menu =', self.uuid)

  def top_items(self):
    return MenuItem.all().filter('active', True).filter('menu = ', self.slug).filter('parentlink =', None).order('order')

  @classmethod
  def urltag(cls):
    return 'menu'
    
  @classmethod
  def subitems_admin_url(cls):
    return MenuItem.admin_url()

  @classmethod
  def subitems_classname(cls):
    return MenuItem.class_name()

  @classmethod
  def get(cls, *args, **kw):
    menu = super(BaseCategory, cls).get(*args, **kw)
    return menu

  def get_block(self):
    return Block.get(uuid=self.block)

  def delete(self):
    try:
      self.get_block().delete()
    except:
      pass
    return super(Menu, self).delete()

  def __str__(self):
    return self.name

  def __unicode__(self):
    return self.name

class MenuItem(Base):
  link = db.StringProperty(required=True)
  active = db.BooleanProperty(default=True)
  parentlink = db.StringProperty(verbose_name=_('Parent Link'))
  menu = db.StringProperty(required=True)
  order = db.IntegerProperty(required=True, default=0)

  key_template = '%(menu)s/%(slug)s'
  
  def __unicode__(self):
    return unicode(self.get_menu()) + ' >> ' + self.__label__()

  def __label__(self):
    res = self.name
    if self.get_parentlink():
      return self.get_parentlink().__label__() + ' >> ' + res
    return res

  @classmethod
  def urltag(cls):
    return 'menuitem'

  @classmethod
  def get_by_url(cls, url):
    res = cls.get(link=url)
    logging.info("   res: %s" % res)
    return res

  @classmethod
  def category_admin(cls):
    return cls.category_model().admin_url()
  
  @classmethod
  def category_model(cls):
    return Menu

  def current(self, request):
    res = self.link == request.path
    if self.has_childs():
      for item in self.get_childs():
        res = (res or item.current(request)) and True
    return res

  def get_menu(self):
    return Menu.get(slug=self.menu)

  def get_parentlink(self):
    return MenuItem.get(uuid=self.parentlink)

  def get_childs(self):
    return MenuItem.filter('parentlink =', self.uuid).filter('active', True)

  def has_childs(self):
    return self.get_childs().count() > 0

  @classmethod
  def get_choices(cls, exclude=[]):
    items = [(item.uuid, item.__unicode__()) for item in cls.get_items(exclude)]
    items = sorted(items, key=itemgetter(1))
    return items

  @classmethod
  def get_items(cls, exclude=[]):
    return [item for item in cls.all() if item.uuid not in exclude]

class Action(BaseModel):
  appname = db.StringProperty(required=True)
  name = db.StringProperty(required=True)
  pattern = db.StringProperty()
  active = db.BooleanProperty(required=True, default=True)
  authorizable = db.BooleanProperty(required=True, default=True)

  key_template = '%(appname)s/%(name)s'
  
  @classmethod
  def register_action(cls, app):
    actions = util.get_attr_from('%s.urls.urlpatterns' % app)
    
    items_excluded = util.get_config_value(app, 'exclude_auth', [])

    # Get all actions from app
    actions_list_name = []
    for action in actions:
      if action.name:
        authorizable = action.name not in items_excluded and True
        action_ref = cls.get(appname=app, name=action.name)
        if not action_ref:
          action_ref = cls(appname=app,
                           name=action.name,
                           pattern=action.regex.pattern,
                           authorizable=authorizable)
        else:
          action_ref.authorizable = authorizable
        action_ref.put()
        actions_list_name.append(action.name)
        
    default_auth = util.get_config_value(app, 'default_auth', {'administrator':actions_list_name})

    # Create permissions
    for role, items in default_auth.iteritems():
      permission_ref = Permission.get_by_role(role)
      if items == '*':
        app_actions = [x for x in actions_list_name if x not in permission_ref.actions]
      else:
        app_actions = [x for x in items if x not in permission_ref.actions]
      permission_ref.actions += app_actions
      permission_ref.save()

class Permission(BaseModel):
  role = db.StringProperty(required=True)
  actions = db.StringListProperty(required=True, default=[])

  key_template = '%(role)s'

  @classmethod
  def get_by_role(cls, role):
    ref = cls.get(role=role)
    if ref is None:
      ref = Permission(role=role)
      ref.put()
    return ref

  @classmethod
  def can_access(cls, roles, action):
    logging.info(">> Permissions.can_access ")
    for role in roles:
      ref = cls.get(role=role)
      if ref is not None and action in ref.actions:
        logging.info(" True")
        return True
    logging.info(" False")
    return False

class Role(BaseModel):
  name = db.StringProperty(required=True)
  core = db.BooleanProperty(required=True, default=False)
  order = db.IntegerProperty(required=True, default=3)

  key_template = '%(name)s'

  def delete(self):
    if self.core:
      raise exception.UnableAction
    super(Role, self).delete()

  @classmethod
  def all(cls):
    return super(Role, cls).all().order('order')