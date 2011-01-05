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

import datetime
import logging
import re

from django.forms import widgets
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe

class SelectMultiple(widgets.SelectMultiple):
    def value_from_datadict(self, data, files, name):
      logging.info(">> common.widgets.SelectMultiple.value_from_datadict")
      res = super(SelectMultiple, self).value_from_datadict(data, files, name)
      if res:
        return ', '.join(res)
      return '[]'

__all__ = ('SelectDateTimeWidget',)

RE_DATETIME = re.compile(r'(\d{4})-(\d\d?)-(\d\d?) (\d\d):(\d\d).*$')

def _generate_time_choices(size):
  _choices = []
  for i in range(size):
    out = (str(i), '0%s'%i)[i < 10]
    _choices.append((i, out))
  return _choices

class SelectDateTimeWidget(widgets.Widget):
    """
    A Widget that splits datetime input into three <select> boxes for date and
    two <select> for time.

    This also serves as an example of a Widget that has more than one HTML
    element and hence implements value_from_datadict.
    """
    month_field = '%s_month'
    day_field = '%s_day'
    year_field = '%s_year'

    hour_field = '%s_hour'
    minute_field = '%s_minute'

    def __init__(self, attrs=None, years=None):
        # years is an optional list/tuple of years to use in the "year" select box.
        self.attrs = attrs or {}
        if years:
            self.years = years
        else:
            this_year = datetime.date.today().year
            self.years = range(this_year, this_year+10)

    def render(self, name, value, attrs=None):
        if value is None:
          value = datetime.datetime.now()
          
        try:
            year_val, month_val, day_val, hour_val, minute_val = \
            value.year, value.month, value.day, value.hour, value.minute
        except AttributeError:
            year_val = month_val = day_val = hour_val = minute_val = None
            if isinstance(value, basestring):
                match = RE_DATETIME.match(value)
                if match:
                    year_val, month_val, day_val, hour_val, minute_val = [int(v) for v in match.groups()]

        output = []

        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name

        month_choices = MONTHS.items()
        month_choices.sort()
        local_attrs = self.build_attrs(id=self.month_field % id_)
        select_html = widgets.Select(choices=month_choices).render(self.month_field % name, month_val, local_attrs)
        output.append(select_html)

        day_choices = [(i, i) for i in range(1, 32)]
        local_attrs['id'] = self.day_field % id_
        select_html = widgets.Select(choices=day_choices).render(self.day_field % name, day_val, local_attrs)
        output.append(select_html)

        year_choices = [(i, i) for i in self.years]
        local_attrs['id'] = self.year_field % id_
        select_html = widgets.Select(choices=year_choices).render(self.year_field % name, year_val, local_attrs)
        output.append(select_html)

        output.append('&nbsp;&nbsp;')

        hour_choices = _generate_time_choices(24)
          
        minute_choices = _generate_time_choices(60)
        
        local_attrs['id'] = self.hour_field % id_
        select_html = widgets.Select(choices=hour_choices).render(self.hour_field % name, hour_val, local_attrs)
        output.append(select_html)

        output.append(':')
        
        local_attrs['id'] = self.minute_field % id_
        select_html = widgets.Select(choices=minute_choices).render(self.minute_field % name, minute_val, local_attrs)
        output.append(select_html)

        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        return '%s_month' % id_
    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        y, m, d, h, mi = data.get(self.year_field % name), \
                         data.get(self.month_field % name), \
                         data.get(self.day_field % name), \
                         data.get(self.hour_field % name), \
                         data.get(self.minute_field % name)
        if y and m and d and h and mi:
            return '%s-%s-%s %s:%s' % (y, m, d, h, mi)
        return data.get(name, None)
