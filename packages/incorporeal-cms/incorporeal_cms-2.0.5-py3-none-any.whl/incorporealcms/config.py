"""Default configuration.

SPDX-FileCopyrightText: © 2020 Brian S. Stephan <bss@incorporeal.org>
SPDX-License-Identifier: GPL-3.0-or-later
"""


class Config(object):
    """Represent the default configuration.

    Reminder: this should be overwritten in the instance config.py, not here!
    """

    DEBUG = False
    TESTING = False

    LOGGING = {
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s %(levelname)-7s %(name)s] %(message)s',
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'default',
            },
        },
        'loggers': {
            '': {
                'level': 'INFO',
                'handlers': ['console'],
            },
        },
    }

    MARKDOWN_EXTENSIONS = ['extra', 'incorporealcms.mdx.figures', 'sane_lists', 'smarty', 'toc']
    MARKDOWN_EXTENSION_CONFIGS = {
        'extra': {
            'footnotes': {
                'UNIQUE_IDS': True,
            },
        },
        'smarty': {
            'smart_dashes': True,
            'smart_quotes': False,
            'smart_angled_quotes': False,
            'smart_ellipses': True,
        },
    }

    # customizations
    PAGE_STYLES = {
        'dark': '/static/css/dark.css',
        'light': '/static/css/light.css',
        'plain': '/static/css/plain.css',
    }

    DEFAULT_PAGE_STYLE = 'light'
    DOMAIN_NAME = 'example.org'
    TITLE_SUFFIX = DOMAIN_NAME
    BASE_HOST = 'http://' + DOMAIN_NAME
    CONTACT_EMAIL = 'admin@example.org'

    # feed settings
    AUTHOR = {'name': 'Test Name', 'email': 'admin@example.org'}

    FAVICON = '/static/img/favicon.png'

    @classmethod
    def update(cls, config: dict):
        """Update this configuration with a dictionary of values from elsewhere."""
        for key, value in config.items():
            setattr(cls, key, value)
