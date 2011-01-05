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

from django import http, template
from django.shortcuts import render_to_response

from common.forms import CommentForm
from common import util

from django.utils.translation import ugettext_lazy as _

ENTRIES_PER_PAGE = 10

class HandlerBase(object):
  def __init__(self, request, extra_context={}, **kwargs):
    self.request = request
    self.extra_context = extra_context

  def handle(self, request, *args, **kwargs):
    raise NotImplementedError

  def get_response(self):
    raise NotImplementedError
  
  def get_context(self):
    return self.extra_context

  def update_context(self, context):
    self.extra_context.update(context)

class ViewHandler(HandlerBase):
  def __init__(self, request, **kwargs):
    super(ViewHandler, self).__init__(request, **kwargs)
    self.tpl = kwargs.pop('tpl', None)
    self.format = kwargs.pop('format', 'html')
    self.area = kwargs.pop('area', 'content')
    self.update_context({"request":self.request,
                         "area":self.area})

  def get_response(self):
    tpl = self.tpl
    if not self.tpl.endswith(('html', 'json', 'atom', 'rss', 'json')):
      tpl = '%s.%s' % (self.tpl, self.format)

    if self.format == 'atom':
      mimetype = 'application/atom+xml; charset=utf-8'
    elif self.format == 'rss':
      mimetype = 'application/rss+xml; charset=utf-8'
    elif self.format == 'json':
      mimetype = 'text/javascript; charset=utf-8'
    else:
      mimetype = None
    return render_to_response(tpl, self.get_context(), mimetype=mimetype)

  def get_context(self):
    return template.RequestContext(self.request, self.extra_context)
  
  def set_message(self, msg_key, type='success'):
    message = util.get_message(msg_key, 'success_content_new')
    util.add_msg(self.request, type, message)

class NewHandler(ViewHandler):
  def __init__(self, request, model=None, model_form=None, redirect_to=None, 
                              tpl="content_new.html", **kwargs):
    
    super(NewHandler, self).__init__(request, tpl=tpl, **kwargs)
    self.model = model
    self.model_form = model_form
    self.redirect_to = redirect_to
    self.update_context({"model":self.model, "model_form":model_form, 
                         "ckeditor":'.ckeditor textarea'})
    
  def handle(self):
    form = self.model_form()
    if self.request.method == 'POST':
      form = self.model_form(self.request.POST)
      if form.is_valid():
        item = form.save()
  
        msg_key = "success_%s_new" % self.model_form._meta.model.object_name()
        self.set_message(msg_key)
  
        if self.redirect_to is not None:
          if self.redirect_to == True:
            return http.HttpResponseRedirect(item.url())
          return http.HttpResponseRedirect(self.redirect_to)
        
    self.update_context({"form":form})
    return self.get_response()

class ContentViewHandler(ViewHandler):
  def __init__(self, request, id, **kwargs):
    tpl = kwargs.pop('tpl', 'content_show')
    super(ContentViewHandler, self).__init__(request, tpl=tpl, **kwargs)
    self.model = kwargs.pop('model')
    self.content = self.__get_content(id, self.model)
    self.update_context({"model":self.model,
                         "content":self.content})

  def handle(self):
    return self.get_response()

  @classmethod
  def __get_content(cls, id, model):
    content = model.get(uuid=id)
    if not content:
      content = model.get(slug=id)
      if not content:
        raise http.Http404(_("Content not found"))
    return content

class EditHandler(ContentViewHandler):
  def __init__(self, request, id, redirect_to=None, tpl="content_edit", **kwargs):
    super(EditHandler, self).__init__(request, id, tpl=tpl, **kwargs)
    self.model_form = kwargs.pop("model_form")
    self.redirect_to = redirect_to

  def handle(self):
    form = self.model_form(instance=self.content)
    if self.request.method == 'POST':
      form = self.model_form(self.request.POST, instance=self.content)
      if form.is_valid():
        item = form.save()

        msg_key = "success_%s_edit" % self.model_form._meta.model.object_name()
        self.set_message(msg_key)

        if self.redirect_to is not None:
          if self.redirect_to == True:
            return http.HttpResponseRedirect(item.url())
          return http.HttpResponseRedirect(self.redirect_to)

    self.update_context({"form":form})
    return self.get_response()

class DeleteHandler(ViewHandler):
  def __init__(self, request, id, model, redirect_to=None, **kwargs):
    super(DeleteHandler, self).__init__(request, **kwargs)
    self.model = model
    self.content = ContentViewHandler.__get_content(id, self.model)
    self.redirect_to = redirect_to or self.content.admin_url()

  def handle(self):
    self.content.delete()
    msg_key = "success_%s_delete" % self.model.object_name()
    self.set_message(msg_key)
    return http.HttpResponseRedirect(self.redirect_to)

class ContentListViewHandler(ViewHandler):
  def __init__(self, request, **kwargs):
    super(ContentListViewHandler, self).__init__(request, **kwargs)
    self.model = kwargs.pop('model')
    self.filters = kwargs.pop('filters', [])
    self.items = self.model.all()
    self.order = kwargs.pop('order', None)
    self.update_context({"model":self.model})

  def filter(self):
    if self.order is not None:
      self.items.order(self.order)

    for filter in self.filters:
      try:
        self.items = filter.filter(self.items)
      except AttributeError:
        self.items = [] # TODO(zero) change to an empty query result
        
    return self.items

  def handle(self):
    self.items = self.filter()
    self.items = util.paginate(self.request, self.items, ENTRIES_PER_PAGE)
    self.update_context({"items":self.items})
    return self.get_response()

class CommentableHandler(ContentViewHandler):
  def __init__(self, request, id, **kwargs):
    super(CommentableHandler, self).__init__(request, id, **kwargs)

  def handle(self):
    comment_form = CommentForm()
    if self.request.method == 'POST':
      params = {'author':self.request.user.username,
                'owner':self.content.owner,
                'content':self.content.uuid,
                'content_type':self.content.app_label}

      comment_form = CommentForm(self.request.POST, extra_params=params)

      if comment_form.is_valid():
        comment_ref = comment_form.save()
        message = util.get_message('success_comment_new')
        util.add_success(self.request, message)
        return http.HttpResponseRedirect(self.content.url())
    self.update_context({"comment_form":comment_form})

    return self.get_response()