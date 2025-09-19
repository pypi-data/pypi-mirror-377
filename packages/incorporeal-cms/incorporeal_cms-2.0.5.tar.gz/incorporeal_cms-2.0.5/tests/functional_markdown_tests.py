"""Test graphviz functionality.

SPDX-FileCopyrightText: © 2021 Brian S. Stephan <bss@incorporeal.org>
SPDX-License-Identifier: GPL-3.0-or-later
"""
import os
import tempfile

import pytest

from incorporealcms import init_instance
from incorporealcms.ssg import StaticSiteGenerator

HERE = os.path.dirname(os.path.abspath(__file__))

init_instance(instance_path=os.path.join(HERE, 'instance'),
              extra_config={'MARKDOWN_EXTENSIONS': ['incorporealcms.mdx.pydot', 'incorporealcms.mdx.figures',
                                                    'attr_list']})


def test_graphviz_is_rendered():
    """Initialize the app with the graphviz extension and ensure it does something."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(HERE, 'instance')
        ssg = StaticSiteGenerator(src_dir, tmpdir)

        ssg.build_file_in_destination(os.path.join(HERE, 'instance', 'pages'), '', 'test-graphviz.md', tmpdir, True)
        with open(os.path.join(tmpdir, 'test-graphviz.html'), 'r') as graphviz_output:
            data = graphviz_output.read()
            assert 'data:image/png;base64' in data


def test_invalid_graphviz_is_not_rendered():
    """Check that invalid graphviz doesn't blow things up."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(HERE, 'instance')
        ssg = StaticSiteGenerator(src_dir, tmpdir)

        with pytest.raises(ValueError):
            ssg.build_file_in_destination(os.path.join(HERE, 'instance', 'broken'), '', 'test-invalid-graphviz.md',
                                          tmpdir, True)


def test_figures_are_rendered():
    """Test that a page with my figure syntax renders as expected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(HERE, 'instance')
        ssg = StaticSiteGenerator(src_dir, tmpdir)

        ssg.build_file_in_destination(os.path.join(HERE, 'instance', 'pages'), '', 'figures.md', tmpdir, True)
        with open(os.path.join(tmpdir, 'figures.html'), 'r') as graphviz_output:
            data = graphviz_output.read()
            assert ('<figure class="right"><img alt="fancy captioned logo" src="bss-square-no-bg.png" />'
                    '<figcaption>this is my cool logo!</figcaption></figure>') in data
            assert ('<figure><img alt="vanilla captioned logo" src="bss-square-no-bg.png" />'
                    '<figcaption>this is my cool logo without an attr!</figcaption>\n</figure>') in data
            assert ('<figure class="left"><img alt="fancy logo" src="bss-square-no-bg.png" />'
                    '<span></span></figure>') in data
            assert '<figure><img alt="just a logo" src="bss-square-no-bg.png" /></figure>' in data


def test_og_image():
    """Test that the og:image meta tag is present as expected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(HERE, 'instance')
        ssg = StaticSiteGenerator(src_dir, tmpdir)

        ssg.build_file_in_destination(os.path.join(HERE, 'instance', 'pages'), '', 'more-metadata.md', tmpdir, True)
        with open(os.path.join(tmpdir, 'more-metadata.html'), 'r') as markdown_output:
            data = markdown_output.read()
            assert ('<meta property="og:image" content="http://example.org/test.img">') in data


def test_og_url():
    """Test that the og:url meta tag is present as expected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(HERE, 'instance')
        ssg = StaticSiteGenerator(src_dir, tmpdir)

        # testing a whole build run because of bugs in how I handle pathing adding a "./" in
        # the generated URLs for content in the pages/ root
        ssg.build_in_destination(os.path.join(HERE, 'instance', 'pages'), tmpdir, True)
        with open(os.path.join(tmpdir, 'index.html'), 'r') as markdown_output:
            data = markdown_output.read()
            assert ('<meta property="og:url" content="http://example.org/">') in data
