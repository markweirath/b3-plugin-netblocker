# -*- encoding: utf-8 -*-
import os
from textwrap import dedent
from tests import *


@pytest.mark.skipif(not os.path.exists(DEFAULT_PLUGIN_CONFIG_FILE), reason="Could not find default plugin config file %r" % DEFAULT_PLUGIN_CONFIG_FILE)
def test_default_conf(console):
    plugin = plugin_netb(console,  DEFAULT_PLUGIN_CONFIG_FILE)
    # [settings]
    assert "0.0.0.0" == plugin._blocks
    assert 1 == plugin._maxLevel


def test_empty_conf(console):
    plugin = plugin_netb_ini(console,  dedent(""""""))
    assert [] == plugin._blocks
    assert 1 == plugin._maxLevel


def test_1(console):
    plugin = plugin_netb_ini(console, dedent("""
        [settings]
        netblock: 0.0.0.0
        maxlevel: 0
        """))
    assert ["127.0.0.1", "192.168.0.3-192.168.0.4"] == plugin._l
    assert 0 == plugin._maxLevel

