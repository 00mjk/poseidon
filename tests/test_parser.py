# -*- coding: utf-8 -*-
"""
Test module for faucet parser.
@author: Charlie Lewis
"""
import os
import shutil
import tempfile
from poseidon.controllers.faucet.faucet import FaucetProxy
from poseidon.controllers.faucet.helpers import get_config_file
from poseidon.controllers.faucet.helpers import parse_rules
from poseidon.controllers.faucet.helpers import represent_none
from poseidon.controllers.faucet.parser import Parser
from poseidon.helpers.config import Config
from poseidon.helpers.endpoint import endpoint_factory

SAMPLE_CONFIG = 'tests/sample_faucet_config.yaml'


def test_ignore_events():
    parser = Parser(ignore_vlans=[999], ignore_ports={'switch99': 11})
    for message_type in ('L2_LEARN', 'L2_EXPIRE', 'PORT_CHANGE'):
        assert parser.ignore_event(
            {'dp_name': 'switch123', message_type: {'vid': 999, 'port_no': 123}})
        assert not parser.ignore_event(
            {'dp_name': 'switch123', message_type: {'vid': 333, 'port_no': 123}})
        assert parser.ignore_event(
            {'dp_name': 'switch99', message_type: {'vid': 333, 'port_no': 11}})
        assert not parser.ignore_event(
            {'dp_name': 'switch99', message_type: {'vid': 333, 'port_no': 99}})
        assert parser.ignore_event(
            {'dp_name': 'switch99', message_type: {'vid': 333, 'port_no': 99, 'stack_descr': 'something'}})
    assert parser.ignore_event(
        {'dp_name': 'switch123', 'UNKNOWN': {'vid': 123, 'port_no': 123}})



def test_parse_rules():
    with tempfile.TemporaryDirectory() as tmpdir:
        shutil.copy(SAMPLE_CONFIG, tmpdir)
        parse_rules(os.path.join(tmpdir, os.path.basename(SAMPLE_CONFIG)))


def test_clear_mirrors():
    with tempfile.TemporaryDirectory() as tmpdir:
        shutil.copy(SAMPLE_CONFIG, tmpdir)
        parser = Parser(ignore_vlans=[999], ignore_ports={'switch99': 11})
        parser.clear_mirrors(os.path.join(tmpdir, os.path.basename(SAMPLE_CONFIG)))


def test_represent_none():
    class MockDumper:
        def represent_scalar(self, foo, bar): return True

    foo = MockDumper()
    represent_none(foo, '')


def test_get_config_file():
    config = get_config_file(None)
    assert config == '/etc/faucet/faucet.yaml'


def test_Parser():
    """
    Tests Parser
    """
    def check_config(obj, path, endpoints):
        obj.config(path, 'mirror', 1, 't1-1')
        obj.config(path, 'mirror', 2, 0x1)
        obj.config(path, 'mirror', 2, 't1-1')
        obj.config(path, 'mirror', 5, 't2-1')
        obj.config(path, 'mirror', 6, 'bad')
        obj.config(path, 'unmirror', None, None)
        obj.config(path, 'unmirror', 1, 't1-1')
        obj.config(path, 'shutdown', None, None)
        obj.config(path, 'apply_acls', None, None)
        obj.config(path, 'apply_acls', 1, 't1-1', endpoints=endpoints,
                   rules_file=os.path.join(os.getcwd(),
                                           'rules.yaml'))
        obj.config(path, 'unknown', None, None)
        obj.log(os.path.join(log_dir, 'faucet.log'))

    config_dir = '/etc/faucet'
    log_dir = '/var/log/faucet'
    if not os.path.exists(config_dir):
        config_dir = os.path.join(os.getcwd(), 'faucet')
    if not os.path.exists(log_dir):
        log_dir = os.path.join(os.getcwd(), 'faucet')

    endpoint = endpoint_factory('foo')
    endpoint.endpoint_data = {
        'tenant': 'foo', 'mac': '00:00:00:00:00:00', 'segment': 't1-1', 'port': '1', 'ipv4': '0.0.0.0', 'ipv6': '1212::1'}
    endpoint.metadata = {'mac_addresses': {'00:00:00:00:00:00': {'1551805502.0': {'labels': ['developer workstation'], 'behavior': 'normal'}}}, 'ipv4_addresses': {
        '0.0.0.0': {'os': 'windows'}}, 'ipv6_addresses': {'1212::1': {'os': 'windows'}}}
    endpoints = [endpoint]

    parser = Parser(mirror_ports={'t1-1': 2})
    parser2 = Parser()
    controller = Config().get_config()
    proxy = FaucetProxy(controller)
    check_config(parser, os.path.join(config_dir, 'faucet.yaml'), endpoints)
    check_config(parser2, os.path.join(config_dir, 'faucet.yaml'), endpoints)
    check_config(proxy, os.path.join(config_dir, 'faucet.yaml'), endpoints)
    with tempfile.TemporaryDirectory() as tmpdir:
        shutil.copy(SAMPLE_CONFIG, tmpdir)
        check_config(parser, os.path.join(tmpdir, os.path.basename(SAMPLE_CONFIG)), endpoints)
        check_config(parser2, os.path.join(tmpdir, os.path.basename(SAMPLE_CONFIG)), endpoints)
        check_config(proxy, os.path.join(tmpdir, os.path.basename(SAMPLE_CONFIG)), endpoints)
