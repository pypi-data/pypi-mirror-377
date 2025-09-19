"""Test command line invocations.

SPDX-FileCopyrightText: © 2025 Brian S. Stephan <bss@incorporeal.org>
SPDX-License-Identifier: GPL-3.0-or-later
"""
import os
import tempfile
from subprocess import run

HERE = os.path.dirname(os.path.abspath(__file__))


def test_build():
    """Test some of the output of the core builder command."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run(['incorporealcms-build', os.path.join(HERE, 'instance'), tmpdir],
                     capture_output=True, encoding='utf8')
        assert "creating temporary directory" in result.stdout
        assert "copying file" in result.stdout
        assert "creating symlink" in result.stdout
        assert "creating directory" in result.stdout
        assert "renaming" in result.stdout


def test_build_error():
    """Test some of the output of the core builder command."""
    result = run(['incorporealcms-build', os.path.join(HERE, 'instance'), os.path.join(HERE, 'test_markdown.py')],
                 capture_output=True, encoding='utf8')
    assert "specified output path" in result.stderr
    assert "exists as a file!" in result.stderr
