"""Test the feed methods.

SPDX-FileCopyrightText: © 2023 Brian S. Stephan <bss@incorporeal.org>
SPDX-License-Identifier: GPL-3.0-or-later
"""
import os
import tempfile

from incorporealcms import init_instance
from incorporealcms.feed import generate_feed

HERE = os.path.dirname(os.path.abspath(__file__))

init_instance(instance_path=os.path.join(HERE, 'instance'))


def test_atom_type_generated():
    """Test that an ATOM feed can be generated."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(HERE, 'instance')
        generate_feed('atom', src_dir, tmpdir)

        with open(os.path.join(tmpdir, 'feed', 'atom'), 'r') as feed_output:
            data = feed_output.read()
            assert '<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n<feed xmlns="http://www.w3.org/2005/Atom">' in data
            assert '<id>https://example.org/</id>' in data
            assert '<email>admin@example.org</email>' in data
            assert '<name>Test Name</name>' in data

            # forced-no-title.md
            assert '<title>example.org</title>' in data
            assert '<link href="https://example.org/forced-no-title"/>' in data
            assert '<id>tag:example.org,2023-12-01:/forced-no-title</id>' in data
            assert '<content type="html">&lt;p&gt;some words are here&lt;/p&gt;</content>' in data

            # more-metadata.md
            assert '<title>title for the page - example.org</title>' in data
            assert '<link href="https://example.org/more-metadata"/>' in data
            assert '<id>tag:example.org,2025-03-16:/more-metadata</id>' in data
            assert '<content type="html">&lt;p&gt;hello&lt;/p&gt;</content>' in data


def test_rss_type_generated():
    """Test that an RSS feed can be generated."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(HERE, 'instance')
        generate_feed('rss', src_dir, tmpdir)

        with open(os.path.join(tmpdir, 'feed', 'rss'), 'r') as feed_output:
            data = feed_output.read()
            assert '<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n<rss xmlns:atom="http://www.w3.org/2005/Atom"' in data
            assert 'xmlns:content="http://purl.org/rss/1.0/modules/content/" version="2.0">' in data
            assert '<link>https://example.org</link>' in data

            # forced-no-title.md
            assert '<title>example.org</title>' in data
            assert '<link>https://example.org/forced-no-title</link>' in data
            assert '<guid isPermaLink="false">tag:example.org,2023-12-01:/forced-no-title</guid>' in data
            assert '<description>&lt;p&gt;some words are here&lt;/p&gt;</description>' in data
            assert '<author>admin@example.org (Test Name)</author>' in data

            # more-metadata.md
            assert '<title>title for the page - example.org</title>' in data
            assert '<link>https://example.org/more-metadata</link>' in data
            assert '<guid isPermaLink="false">tag:example.org,2025-03-16:/more-metadata</guid>' in data
            assert '<description>&lt;p&gt;hello&lt;/p&gt;</description>' in data
            assert '<author>admin@example.org (Test Name)</author>' in data


def test_multiple_runs_without_error():
    """Test that we can run the RSS and Atom feed generators in any order."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(HERE, 'instance')
        generate_feed('atom', src_dir, tmpdir)
        generate_feed('rss', src_dir, tmpdir)
        generate_feed('atom', src_dir, tmpdir)
        generate_feed('rss', src_dir, tmpdir)
