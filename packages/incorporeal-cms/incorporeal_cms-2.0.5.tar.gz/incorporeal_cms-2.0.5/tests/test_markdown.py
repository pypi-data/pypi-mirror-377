"""Test the conversion of Markdown pages.

SPDX-FileCopyrightText: © 2025 Brian S. Stephan <bss@incorporeal.org>
SPDX-License-Identifier: GPL-3.0-or-later
"""
import os
from unittest.mock import patch

import pytest

from incorporealcms import init_instance
from incorporealcms.markdown import (generate_parent_navs, handle_markdown_file_path,
                                     instance_resource_path_to_request_path, parse_md,
                                     request_path_to_breadcrumb_display)

HERE = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(HERE, 'instance')
PAGES_DIR = os.path.join(INSTANCE_DIR, 'pages/')

# initialize in order to configure debug logging
init_instance(INSTANCE_DIR)


def test_generate_page_navs_index():
    """Test that the index page has navs to the root (itself)."""
    assert generate_parent_navs('index.md', PAGES_DIR) == [('example.org', '/')]


def test_generate_page_navs_subdir_index():
    """Test that dir pages have navs to the root and themselves."""
    assert generate_parent_navs('subdir/index.md', PAGES_DIR) == [('example.org', '/'), ('subdir', '/subdir/')]


def test_generate_page_navs_subdir_real_page():
    """Test that real pages have navs to the root, their parent, and themselves."""
    assert generate_parent_navs('subdir/page.md', PAGES_DIR) == [('example.org', '/'), ('subdir', '/subdir/'),
                                                                 ('Page', '/subdir/page')]


def test_generate_page_navs_subdir_with_title_parsing_real_page():
    """Test that title metadata is used in the nav text."""
    assert generate_parent_navs('subdir-with-title/page.md', PAGES_DIR) == [
        ('example.org', '/'),
        ('SUB!', '/subdir-with-title/'),
        ('page', '/subdir-with-title/page')
    ]


def test_generate_page_navs_subdir_with_no_index():
    """Test that breadcrumbs still generate even if a subdir doesn't have an index.md."""
    assert generate_parent_navs('no-index-dir/page.md', PAGES_DIR) == [
        ('example.org', '/'),
        ('/no-index-dir/', '/no-index-dir/'),
        ('page', '/no-index-dir/page')
    ]


def test_page_includes_themes_with_default():
    """Test that a request contains the configured themes and sets the default as appropriate."""
    assert '<link rel="stylesheet" type="text/css" title="light" href="/static/css/light.css">'\
        in handle_markdown_file_path('index.md', PAGES_DIR)
    assert '<link rel="alternate stylesheet" type="text/css" title="dark" href="/static/css/dark.css">'\
        in handle_markdown_file_path('index.md', PAGES_DIR)
    assert '<a href="" onclick="setStyle(\'light\'); return false;">[light]</a>'\
        in handle_markdown_file_path('index.md', PAGES_DIR)
    assert '<a href="" onclick="setStyle(\'dark\'); return false;">[dark]</a>'\
        in handle_markdown_file_path('index.md', PAGES_DIR)


def test_render_with_style_overrides():
    """Test that the default can be changed."""
    with patch('incorporealcms.Config.DEFAULT_PAGE_STYLE', 'dark'):
        assert '<link rel="stylesheet" type="text/css" title="dark" href="/static/css/dark.css">'\
            in handle_markdown_file_path('index.md', PAGES_DIR)
        assert '<link rel="alternate stylesheet" type="text/css" title="light" href="/static/css/light.css">'\
            in handle_markdown_file_path('index.md', PAGES_DIR)
    assert '<a href="" onclick="setStyle(\'light\'); return false;">[light]</a>'\
        in handle_markdown_file_path('index.md', PAGES_DIR)
    assert '<a href="" onclick="setStyle(\'dark\'); return false;">[dark]</a>'\
        in handle_markdown_file_path('index.md', PAGES_DIR)


def test_render_with_default_style_override():
    """Test that theme overrides work, and if a requested theme doesn't exist, the default is loaded."""
    with patch('incorporealcms.Config.PAGE_STYLES', {'cool': '/static/css/cool.css',
                                                     'warm': '/static/css/warm.css'}):
        with patch('incorporealcms.Config.DEFAULT_PAGE_STYLE', 'warm'):
            assert '<link rel="stylesheet" type="text/css" title="warm" href="/static/css/warm.css">'\
                in handle_markdown_file_path('index.md', PAGES_DIR)
            assert '<link rel="alternate stylesheet" type="text/css" title="cool" href="/static/css/cool.css">'\
                in handle_markdown_file_path('index.md', PAGES_DIR)
            assert '<link rel="alternate stylesheet" type="text/css" title="light" href="/static/css/light.css">'\
                not in handle_markdown_file_path('index.md', PAGES_DIR)
            assert '<a href="" onclick="setStyle(\'warm\'); return false;">[warm]</a>'\
                in handle_markdown_file_path('index.md', PAGES_DIR)
            assert '<a href="" onclick="setStyle(\'cool\'); return false;">[cool]</a>'\
                in handle_markdown_file_path('index.md', PAGES_DIR)


def test_redirects_error_unsupported():
    """Test that we throw a warning about the barely-used Markdown redirect tag, which we can't support via SSG."""
    with pytest.raises(NotImplementedError):
        handle_markdown_file_path('redirect.md', os.path.join(INSTANCE_DIR, 'broken'))


def test_instance_resource_path_to_request_path_on_index():
    """Test index.md -> /."""
    assert instance_resource_path_to_request_path('index.md') == '/'


def test_instance_resource_path_to_request_path_on_page():
    """Test no-title.md -> no-title."""
    assert instance_resource_path_to_request_path('no-title.md') == '/no-title'


def test_instance_resource_path_to_request_path_on_subdir():
    """Test subdir/index.md -> subdir/."""
    assert instance_resource_path_to_request_path('subdir/index.md') == '/subdir/'


def test_instance_resource_path_to_request_path_on_subdir_and_page():
    """Test subdir/page.md -> subdir/page."""
    assert instance_resource_path_to_request_path('subdir/page.md') == '/subdir/page'


def test_request_path_to_breadcrumb_display_patterns():
    """Test various conversions from request path to leaf nodes for display in the breadcrumbs."""
    assert request_path_to_breadcrumb_display('/foo') == 'foo'
    assert request_path_to_breadcrumb_display('/foo/') == 'foo'
    assert request_path_to_breadcrumb_display('/foo/bar') == 'bar'
    assert request_path_to_breadcrumb_display('/foo/bar/') == 'bar'
    assert request_path_to_breadcrumb_display('/') == ''


def test_parse_md_metadata():
    """Test the direct results of parsing a markdown file."""
    content, md, page_name, page_title, mtime = parse_md(os.path.join(PAGES_DIR, 'more-metadata.md'), PAGES_DIR)
    assert page_name == 'title for the page'
    assert page_title == 'title for the page - example.org'


def test_parse_md_metadata_forced_no_title():
    """Test the direct results of parsing a markdown file."""
    content, md, page_name, page_title, mtime = parse_md(os.path.join(PAGES_DIR, 'forced-no-title.md'), PAGES_DIR)
    assert page_name == ''
    assert page_title == 'example.org'


def test_parse_md_metadata_no_title_so_path():
    """Test the direct results of parsing a markdown file."""
    content, md, page_name, page_title, mtime = parse_md(os.path.join(PAGES_DIR, 'subdir/index.md'), PAGES_DIR)
    assert page_name == '/subdir/'
    assert page_title == '/subdir/ - example.org'


def test_parse_md_no_file():
    """Test the direct results of parsing a markdown file."""
    with pytest.raises(FileNotFoundError):
        content, md, page_name, page_title, mtime = parse_md(os.path.join(PAGES_DIR, 'nope.md'), PAGES_DIR)


def test_parse_md_bad_file():
    """Test the direct results of parsing a markdown file."""
    with pytest.raises(ValueError):
        content, md, page_name, page_title, mtime = parse_md(os.path.join(PAGES_DIR, 'actually-a-png.md'), PAGES_DIR)


def test_md_extension_in_source_link_is_stripped():
    """Test that if a foo.md file link is specified in the Markdown, it is foo in the HTML."""
    content, _, _, _, _ = parse_md(os.path.join(PAGES_DIR, 'file-with-md-link.md'), PAGES_DIR)
    assert '<a href="foo">Foo</a>' in content
    assert '<a href="foo#anchor">Anchored Foo</a>' in content
    assert '<a href="sub/foo">Sub Foo</a>' in content
    assert '<a href="sub/foo#anchor">Anchored Sub Foo</a>' in content


def test_index_in_source_link_is_stripped():
    """Test that if a index.md file link is specified in the Markdown, it is just the dir in the HTML."""
    content, _, _, _, _ = parse_md(os.path.join(PAGES_DIR, 'file-with-index.md-link.md'), PAGES_DIR)
    assert '<a href="cool/">Cool</a>' in content
    assert '<a href="cool/#anchor">Anchored Cool</a>' in content
    assert '<a href=".">This Index</a>' in content
    assert '<a href=".#anchor">Anchored This Index</a>' in content
    assert '<a href="../">Parent</a>' in content
    assert '<a href="../#anchor">Anchored Parent</a>' in content
