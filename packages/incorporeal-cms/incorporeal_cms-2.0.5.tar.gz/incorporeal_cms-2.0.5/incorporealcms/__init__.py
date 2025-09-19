"""An application for running my Markdown-based sites.

SPDX-FileCopyrightText: © 2025 Brian S. Stephan <bss@incorporeal.org>
SPDX-License-Identifier: GPL-3.0-or-later
"""
import json
import logging
import os
from logging.config import dictConfig

from jinja2 import Environment, PackageLoader, select_autoescape
from termcolor import cprint

from incorporealcms.config import Config

jinja_env = Environment(
    loader=PackageLoader('incorporealcms'),
    autoescape=select_autoescape(),
)

# dynamically generate version number
try:
    # packaged/pip install -e . value
    from ._version import version as __version__
except ImportError:
    # local clone value
    from setuptools_scm import get_version
    __version__ = get_version(root='..', relative_to=__file__)


def init_instance(instance_path: str, extra_config: dict = None):
    """Create the instance context, with allowances for customizing path and test settings."""
    # load the instance config.json, if there is one
    instance_config = os.path.join(instance_path, 'config.json')
    try:
        with open(instance_config, 'r') as config:
            config_dict = json.load(config)
            cprint(f"splicing {config_dict} into the config", 'yellow')
            Config.update(config_dict)
    except OSError:
        raise ValueError("instance path does not seem to be a site instance!")

    if extra_config:
        cprint(f"splicing {extra_config} into the config", 'yellow')
        Config.update(extra_config)

    # stash some stuff
    Config.INSTANCE_DIR = os.path.abspath(instance_path)

    dictConfig(Config.LOGGING)
    logger = logging.getLogger(__name__)

    logger.debug("instance dir: %s", Config.INSTANCE_DIR)
