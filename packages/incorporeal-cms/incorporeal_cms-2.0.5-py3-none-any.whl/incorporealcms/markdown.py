"""Process Markdown pages.

With the project now being a SSG, most files we just let the web server serve
as is, but .md files need to be processed with a Markdown parser, so a lot of this
is our tweaks and customizations for pages my way.

SPDX-FileCopyrightText: © 2025 Brian S. Stephan <bss@incorporeal.org>
SPDX-License-Identifier: GPL-3.0-or-later
"""
import datetime
import logging
import os
import re

import markdown
from markupsafe import Markup

from incorporealcms import jinja_env
from incorporealcms.config import Config

logger = logging.getLogger(__name__)


def get_meta_str(md, key):
    """Provide the page's (parsed in Markup obj md) metadata for the specified key, or '' if unset."""
    return " ".join(md.Meta.get(key)) if md.Meta.get(key) else ""


def init_md():
    """Initialize the Markdown parser.

    This used to done at the app level in __init__, but extensions like footnotes apparently
    assume the parser to only live for the length of parsing one document, and create double
    footnote ref links if the one parser sees the same document multiple times.
    """
    # initialize markdown parser from config, but include
    # extensions our app depends on, like the meta extension
    return markdown.Markdown(extensions=Config.MARKDOWN_EXTENSIONS + ['meta'],
                             extension_configs=Config.MARKDOWN_EXTENSION_CONFIGS)


def instance_resource_path_to_request_path(path):
    """Reverse a relative disk path to the path that would show up in a URL request."""
    return '/' + re.sub(r'.md$', '', re.sub(r'index.md$', '', path))


def parse_md(path: str, pages_root: str):
    """Given a file to parse, return file content and other derived data along with the md object.

    Args:
        path: the path to the file to render
        pages_root: the absolute path to the pages/ dir, which the path should be within. necessary for
                    proper resolution of resolving parent pages (which needs to know when to stop)
    """
    try:
        absolute_path = os.path.join(pages_root, path)
        logger.debug("opening path '%s'", absolute_path)
        with open(absolute_path, 'r') as input_file:
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(input_file.name), tz=datetime.timezone.utc)
            entry = input_file.read()

        logger.debug("path '%s' read", absolute_path)

        # remove .md extensions used for navigating in vim and replace them with
        # the pattern we use for HTML output here
        # foo/index.md -> foo/, foo/index.md#anchor -> foo/#anchor
        # ../index.md -> ../, ../index.md#anchor -> ../#anchor
        entry = re.sub(r'\[([^]]+)\]\(([^)]+)index.md(#[^)]*)?\)', r'[\1](\2\3)', entry)
        # index.md -> ., index.md#anchor -> .#anchor
        entry = re.sub(r'\[([^]]+)\]\(index.md(#[^)]*)?\)', r'[\1](.\2)', entry)
        # bar.md -> bar, foo/bar.md -> foo/bar, bar.md#anchor -> bar#anchor
        entry = re.sub(r'\[([^]]+)\]\(([^)]+).md(#[^)]*)?\)', r'[\1](\2\3)', entry)
        md = init_md()
        content = Markup(md.convert(entry))     # nosec B704
    except (OSError, FileNotFoundError):
        logger.exception("path '%s' could not be opened!", path)
        raise
    except ValueError:
        logger.exception("error parsing/rendering markdown!")
        raise

    logger.debug("file metadata: %s", md.Meta)

    rel_path = os.path.relpath(path, pages_root)
    page_name = get_meta_str(md, 'title') if md.Meta.get('title') else instance_resource_path_to_request_path(rel_path)
    page_title = f'{page_name} - {Config.TITLE_SUFFIX}' if page_name else Config.TITLE_SUFFIX
    logger.debug("title (potentially derived): %s", page_title)

    return content, md, page_name, page_title, mtime


def handle_markdown_file_path(path: str, pages_root: str) -> str:
    """Given a location on disk, attempt to open it and render the markdown within.

    Args:
        path: the path to the file to parse and produce metadata for
        pages_root: the absolute path to the pages/ dir, which the path should be within. necessary for
                    proper resolution of resolving parent pages (which needs to know when to stop)
    """
    content, md, page_name, page_title, mtime = parse_md(path, pages_root)
    relative_path = os.path.relpath(path, pages_root)
    parent_navs = generate_parent_navs(relative_path, pages_root)
    extra_footer = get_meta_str(md, 'footer') if md.Meta.get('footer') else None
    template_name = get_meta_str(md, 'template') if md.Meta.get('template') else 'base.html'

    # check if this has a HTTP redirect
    redirect_url = get_meta_str(md, 'redirect') if md.Meta.get('redirect') else None
    if redirect_url:
        raise NotImplementedError("redirects in markdown are unsupported!")

    template = jinja_env.get_template(template_name)
    return template.render(title=page_title,
                           config=Config,
                           description=get_meta_str(md, 'description'),
                           image=Config.BASE_HOST + get_meta_str(md, 'image'),
                           content=content,
                           base_url=Config.BASE_HOST + instance_resource_path_to_request_path(relative_path),
                           navs=parent_navs,
                           mtime=mtime.strftime('%Y-%m-%d %H:%M:%S %Z'),
                           extra_footer=extra_footer)


def generate_parent_navs(path, pages_root: str):
    """Create a series of paths/links to navigate up from the given resource path.

    Args:
        path: the path to parse and generate parent metadata nav links for
        pages_root: the absolute path to the pages/ dir, which the path should be within. path is relative,
                    but opening parents requires the full path
    """
    logger.debug("path to generate navs for: %s", path)
    if path == 'index.md':
        # bail and return the domain name as a terminal case
        return [(Config.DOMAIN_NAME, '/')]
    else:
        if path.endswith('index.md'):
            # index case: one dirname for foo/bar/index.md -> foo/bar, one for foo/bar -> foo
            parent_resource_dir = os.path.dirname(os.path.dirname(path))
        else:
            # usual case: foo/buh.md -> foo
            parent_resource_dir = os.path.dirname(path)

        # generate the request path (i.e. what the link will be) for this path, and
        # also the resource path of this parent (which is always a dir, so always index.md)
        request_path = instance_resource_path_to_request_path(path)
        parent_resource_path = os.path.join(parent_resource_dir, 'index.md')

        logger.debug("resource path: '%s'; request path: '%s'; parent resource path: '%s'", path,
                     request_path, parent_resource_path)

        # for issues regarding parser reuse (see lib.init_md) we reinitialize the parser here
        md = init_md()

        # read the resource
        try:
            with open(os.path.join(pages_root, path), 'r') as entry_file:
                entry = entry_file.read()
            _ = Markup(md.convert(entry))       # nosec B704
            page_name = (" ".join(md.Meta.get('title')) if md.Meta.get('title')
                         else request_path_to_breadcrumb_display(request_path))
            return generate_parent_navs(parent_resource_path, pages_root) + [(page_name, request_path)]
        except FileNotFoundError:
            return generate_parent_navs(parent_resource_path, pages_root) + [(request_path, request_path)]


def request_path_to_breadcrumb_display(path):
    """Given a request path, e.g. "/foo/bar/baz/", turn it into breadcrumby text "baz"."""
    undired = path.rstrip('/')
    leaf = undired[undired.rfind('/'):]
    return leaf.strip('/')
