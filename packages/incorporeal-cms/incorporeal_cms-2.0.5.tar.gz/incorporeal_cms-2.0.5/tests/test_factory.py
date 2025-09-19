"""Test basic configuration stuff.

SPDX-FileCopyrightText: © 2020 Brian S. Stephan <bss@incorporeal.org>
SPDX-License-Identifier: GPL-3.0-or-later
"""
import os

import pytest

from incorporealcms import init_instance
from incorporealcms.config import Config

HERE = os.path.dirname(os.path.abspath(__file__))


def test_config():
    """Test that the app initialization sets values not normally present in the config."""
    # this may have gotten here from other imports in other tests
    try:
        delattr(Config, 'INSTANCE_VALUE')
    except AttributeError:
        pass

    assert not getattr(Config, 'INSTANCE_VALUE', None)
    assert not getattr(Config, 'EXTRA_VALUE', None)

    instance_path = os.path.join(HERE, 'instance')
    init_instance(instance_path=instance_path, extra_config={"EXTRA_VALUE": "hello"})

    assert getattr(Config, 'INSTANCE_VALUE', None) == "hi"
    assert getattr(Config, 'EXTRA_VALUE', None) == "hello"


def test_broken_config():
    """Test that the app initialization errors when not given an instance-looking thing."""
    with pytest.raises(ValueError):
        instance_path = os.path.join(HERE, 'blah')
        init_instance(instance_path=instance_path)
