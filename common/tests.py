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


from common.test.base import ViewTestCase
from common.models import MenuItem

from users.messages import messages 

__author__="Jose Maria Zambrana Arze <contact@josezambrana.com>"
__date__ ="$22-dic-2010 14:38:55$"

class MenusTest(ViewTestCase):
  def test_newhandler_get(self):
    logging.info("#### common.HandlerTest.test_new_handler")
    r = self.login_and_get('admin', MenuItem.new_url())
    self.failUnlessEqual(r.status_code, 200)