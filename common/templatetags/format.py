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

import re

from django import template

from common.util import safe

register = template.Library()


core_plural_rules = [(r'(.*)(s)tatus$',r'\1\2tatuses'),
                     (r'(.*)(quiz)$',r'\1\2zes'),
                     (r'^(ox)$',r'\1en'),
                     (r'(.*)([m|l])ouse$',r'\1\2ice'),
                     (r'(.*)(matr|vert|ind)(ix|ex)$',r'\1\2\3ices'),
                     (r'(.*)(x|ch|ss|sh)$',r'\1\2es'),
                     (r'(.*)([^aeiouy]|qu)y$',r'\1\2ies'),
                     (r'(.*)(hive)$',r'\1\2s'),
                     (r'(.*)(?:([^f])fe|([lr])f)$',r'\1\2\3ves'),
                     (r'(.*)sis$',r'\1ses'),
                     (r'(.*)([ti])um$',r'\1\2a'),
                     (r'(.*)(p)erson$',r'\1\2eople'),
                     (r'(.*)(m)an$',r'\1\2en'),
                     (r'(.*)(c)hild$',r'\1\2hildren'),
                     (r'(.*)(buffal|tomat)o$',r'\1\2oes'),
                     (r'(.*)(alumn|bacill|cact|foc|fung|nucle|radi|stimul|syllab|termin|vir)us$',r'\1\2i'),
                     (r'(.*)us$',r'\1uses'),
                     (r'(.*)(alias)$',r'\1\2es'),
                     (r'(.*)(ax|cris|test)is$',r'\1\2es'),
                     (r'(.*)s$',r'\1s'),
                     (r'^$',r''),
                     (r'(.*)$',r'\1s')]

uninflected_plural = ['.*[nrlm]ese', 'buzz', 'chatter', '.*deer', '.*fish', '.*measles', '.*ois', '.*pox', '.*sheep', 'Amoyese',
			'bison', 'Borghese', 'bream', 'breeches', 'britches', 'buffalo', 'cantus', 'carp', 'chassis', 'clippers',
			'cod', 'coitus', 'Congoese', 'contretemps', 'corps', 'debris', 'diabetes', 'djinn', 'eland', 'elk',
			'equipment', 'Faroese', 'flounder', 'Foochowese', 'gallows', 'Genevese', 'Genoese', 'Gilbertese', 'graffiti',
			'headquarters', 'herpes', 'hijinks', 'Hottentotese', 'information', 'innings', 'jackanapes', 'Kiplingese',
			'Kongoese', 'Lucchese', 'mackerel', 'Maltese', 'media', 'mews', 'moose', 'mumps', 'Nankingese', 'news',
			'nexus', 'Niasese', 'Pekingese', 'People', 'Piedmontese', 'pincers', 'Pistoiese', 'pliers', 'Portuguese', 'proceedings',
			'rabies', 'rice', 'rhinoceros', 'salmon', 'Sarawakese', 'scissors', 'sea[- ]bass', 'series', 'Shavese', 'shears',
			'siemens', 'species', 'swine', 'testes', 'trousers', 'trout', 'tuna', 'Vermontese', 'Wenchowese',
			'whiting', 'wildebeest', 'Yengeese'];

irregular_plural = {
			'atlas':'atlases',
			'beef':'beefs',
			'brother':'brothers',
			'child':'children',
			'corpus':'corpuses',
			'cow':'cows',
			'ganglion':'ganglions',
			'genie':'genies',
			'genus':'genera',
			'graffito':'graffiti',
			'hoof':'hoofs',
			'loaf':'loaves',
			'man':'men',
			'money':'monies',
			'mongoose':'mongooses',
			'move':'moves',
			'mythos':'mythoi',
			'numen':'numina',
			'occiput':'occiputs',
			'octopus':'octopuses',
			'opus':'opuses',
			'ox':'oxen',
			'penis':'penises',
			'person':'people',
			'sex':'sexes',
			'soliloquy':'soliloquies',
			'testis':'testes',
			'trilby':'trilbys',
			'turf':'turfs',
			}


@register.filter(name="spacify")
@safe
def spacify(word, arg=None):
  return re.sub('((?=[A-Z][a-z])|(?<=[a-z])(?=[A-Z]))', ' ', word)


def _get_uninflected(word):
  for rule in uninflected_plural:
    if re.match(rule, word):
      return word
  return None

@register.filter(name="plural")
@safe
def plural(word, arg=None):
  res = _get_uninflected(word)
  if res is not None:
    return res
  for rule, replace in core_plural_rules:
    if re.match(rule, word, re.IGNORECASE):
	  return re.sub(rule, replace, word)
  return word