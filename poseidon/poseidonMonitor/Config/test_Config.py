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
Test module for Config.py

Created on 28 June 2016
@author: dgrossman, lanhamt
"""
import falcon
import pytest
from Config import Config

application = falcon.API()
application.add_route('/v1/Config/{section}/{field}', Config())


# exposes the application for testing
@pytest.fixture
def app():
    return application


def test_pcap_resource_get(client):
    """
<<<<<<< HEAD:poseidon/poseidonMonitor/Config/test_Config.py
    Tests the Config class
=======
    Tests the PoseidonConfig class
>>>>>>> eb82051dbd7dca113f4b41cc8d0ca86000b05225:poseidon/poseidonRest/PoseidonConfig/test_PoseidonConfig.py
    """
    resp = client.get('/v1/Config/rest config test/key1')
    assert resp.status == falcon.HTTP_OK
    assert resp.body == "trident"

    resp = client.get('/v1/Config/rest config test/key2')
    assert resp.status == falcon.HTTP_OK
    assert resp.body == "theseus"

    resp = client.get('/v1/Config/rest config test/double key')
    assert resp.status == falcon.HTTP_OK
    assert resp.body == "atlas horses"
