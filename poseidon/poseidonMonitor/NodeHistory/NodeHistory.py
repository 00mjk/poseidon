#!/usr/bin/env python
#
#   Copyright (c) 2016 In-Q-Tel, Inc, All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""
Created on 17 May 2016
@author: dgrossman, lanhamt
"""

from poseidon.baseClasses.Monitor_Action_Base import Monitor_Action_Base
from poseidon.baseClasses.Monitor_Helper_Base import Monitor_Helper_Base


class NodeHistory(Monitor_Action_Base):

    def __init__(self):
        super(NodeHistory, self).__init__()
        self.mod_name = self.__class__.__name__
        self.owner = None
        self.configured = False
        self.actions = dict()

    def add_endpoint(self, name, handler):
        a = handler()
        a.owner = self
        self.actions[name] = a

    def del_endpoint(self, name):
        if name in self.actions:
            self.actions.pop(name)

    def get_endpoint(self, name):
        if name in self.actions:
            return self.actions.get(name)
        else:
            return None
        self.config_section_name = self.mod_name

    def configure(self):
        self.mod_name, 'configure'
        if self.owner:
            conf = self.owner.Config.get_endpoint('Handle_SectionConfig')
            self.config = conf.direct_get(self.mod_name)
            self.configured = True

    def configure_endpoints(self):
        # print self.mod_name, 'configure_endpoints'
        if self.owner and self.configured:
            for k, v in self.actions.iteritems():
                # print 'about to configure %s\n' % (k)
                v.configure()


class Handle_Default(Monitor_Helper_Base):

    def __init__(self):
        super(Handle_Default, self).__init__()
        self.mod_name = self.__class__.__name__
        self.owner = None
        self.config = None
        self.configured = False

    def on_get(self, req, resp, resource):
        resp.content_type = 'text/text'
        try:
            resp.body = self.mod_name + ' found: %s' % (resource)
        except:  # pragma: no cover
            resp.body = 'failed'

    def configure(self):
        if not self.owner:
            return

        if not self.owner.owner:
            return

        conf = self.owner.owner.Config.get_endpoint('Handle_SectionConfig')
        name = self.owner.mod_name + ':' + self.mod_name

        self.config = conf.direct_get(name)
        self.configured = True


nodehistory_interface = NodeHistory()
nodehistory_interface.add_endpoint('Handle_Default', Handle_Default)
