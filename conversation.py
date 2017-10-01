# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os.path
import sys
import random
import json

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

CLIENT_ACCESS_TOKEN = 'a4c5990369cf4ce08b839abef0d2eac7'


class Conversation:

  _instance = None
  
  @classmethod
  def get_instance(cls):
    if not cls._instance:
      cls._instance = Conversation()
    return cls._instance

  def __init__(self):
    self._ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    self._session_id = str(int(random.random() * 1000000000000))

  def get_action(self, query, locale):
    request = self._ai.text_request()

    request.lang = locale 

    request.query = query

    response = request.getresponse()

    data = json.load(response)
    retval = {}
    retval["action"] = data["result"]["action"]
    retval["parameters"] = data["result"]["parameters"]
    retval["contexts"] = data["result"]["contexts"]
    retval["response"] = data["result"]["fulfillment"]["speech"]

    return retval
