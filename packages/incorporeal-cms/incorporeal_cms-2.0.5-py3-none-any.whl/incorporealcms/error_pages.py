"""Process the error page templates.

SPDX-FileCopyrightText: © 2025 Brian S. Stephan <bss@incorporeal.org>
SPDX-License-Identifier: GPL-3.0-or-later
"""
import os

from incorporealcms import jinja_env
from incorporealcms.config import Config


def generate_error_pages(dest_dir: str) -> None:
    """Process the error pages and place them in the output dir.

    Args:
        dest_dir: the directory to place the error pages in, for a web server to serve
    """
    for template_name in ['400.html', '404.html', '500.html']:
        template = jinja_env.get_template(template_name)
        with open(os.path.join(dest_dir, template_name), 'w') as error_page:
            error_page.write(template.render(config=Config))
