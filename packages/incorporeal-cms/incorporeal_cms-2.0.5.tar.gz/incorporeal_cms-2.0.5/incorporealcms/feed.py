"""Generate Atom and RSS feeds based on content in a blog-ish location.

This parses a special root directory, feed/, for YYYYMMDD-foo.md files,
and combines them into an Atom or RSS feed. These files *should* be symlinks
to the real pages, which may mirror the same YYYYMMDD-foo.md file naming scheme
under pages/ (which may make sense for a blog) if they want, but could just
as well be pages/foo content.

SPDX-FileCopyrightText: © 2023 Brian S. Stephan <bss@incorporeal.org>
SPDX-License-Identifier: GPL-3.0-or-later
"""
import logging
import os
import re

from feedgen.feed import FeedGenerator

from incorporealcms.config import Config
from incorporealcms.markdown import instance_resource_path_to_request_path, parse_md

logger = logging.getLogger(__name__)


def generate_feed(feed_type: str, instance_dir: str, dest_dir: str) -> None:
    """Generate the Atom or RSS feed as requested.

    Feed entries should be symlinks to .md files in the pages/ directory, so that they
    are also linkable and can be browsed outside of the feed.

    Args:
        feed_type: 'atom' or 'rss' feed
        instance_dir: the directory for the instance, containing both the feed dir and pages
        dest_dir: the directory to place the feed subdir and requested feed
    """
    fg = FeedGenerator()
    fg.id(f'https://{Config.DOMAIN_NAME}/')
    fg.title(f'{Config.TITLE_SUFFIX}')
    fg.author(Config.AUTHOR)
    fg.link(href=f'https://{Config.DOMAIN_NAME}/feed/{feed_type}', rel='self')
    fg.link(href=f'https://{Config.DOMAIN_NAME}', rel='alternate')
    fg.subtitle(f"Blog posts and other interesting materials from {Config.TITLE_SUFFIX}")

    # feed symlinks should all be within the core content subdirectory
    pages_dir = os.path.join(instance_dir, 'pages')

    # get recent feeds
    feed_path = os.path.join(instance_dir, 'feed')
    feed_entry_paths = [os.path.join(dirpath, filename) for dirpath, _, filenames in os.walk(feed_path)
                        for filename in filenames if os.path.islink(os.path.join(dirpath, filename))]
    for feed_entry_path in sorted(feed_entry_paths):
        # get the actual file to parse it
        resolved_path = os.path.relpath(os.path.realpath(feed_entry_path), pages_dir)
        try:
            content, md, page_name, page_title, mtime = parse_md(os.path.join(pages_dir, resolved_path), pages_dir)
            link = f'https://{Config.DOMAIN_NAME}{instance_resource_path_to_request_path(resolved_path)}'
        except (OSError, ValueError, TypeError):
            logger.exception("error loading/rendering markdown!")
            raise

        fe = fg.add_entry()
        fe.id(_generate_feed_id(feed_entry_path, instance_resource_path_to_request_path(resolved_path)))
        fe.title(page_title)
        fe.author(Config.AUTHOR)
        fe.link(href=link)
        fe.content(content, type='html')

    if feed_type == 'rss':
        try:
            os.mkdir(os.path.join(dest_dir, 'feed'))
        except FileExistsError:
            pass
        with open(os.path.join(dest_dir, 'feed', 'rss'), 'wb') as feed_file:
            feed_file.write(fg.rss_str(pretty=True))
    else:
        try:
            os.mkdir(os.path.join(dest_dir, 'feed'))
        except FileExistsError:
            pass
        with open(os.path.join(dest_dir, 'feed', 'atom'), 'wb') as feed_file:
            feed_file.write(fg.atom_str(pretty=True))


def _generate_feed_id(feed_entry_path, request_path):
    """For a relative file path, generate the Atom/RSS feed ID for it."""
    date = re.sub(r'.*(\d{4})(\d{2})(\d{2}).*', r'\1-\2-\3', feed_entry_path)
    cleaned = request_path.replace('#', '/')
    return f'tag:{Config.DOMAIN_NAME},{date}:{cleaned}'
