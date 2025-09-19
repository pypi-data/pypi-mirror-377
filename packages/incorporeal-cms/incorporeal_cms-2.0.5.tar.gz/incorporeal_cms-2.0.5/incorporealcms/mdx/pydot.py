"""Serve dot diagrams inline.

SPDX-FileCopyrightText: © 2021 Brian S. Stephan <bss@incorporeal.org>
SPDX-License-Identifier: GPL-3.0-or-later
"""
import base64
import logging
import re

import markdown
import pydot

logger = logging.getLogger(__name__)


class InlinePydot(markdown.Extension):
    """Wrap the markdown prepcoressor."""

    def extendMarkdown(self, md):
        """Add InlinePydotPreprocessor to the Markdown instance."""
        md.preprocessors.register(InlinePydotPreprocessor(md), 'dot_block', 100)


class InlinePydotPreprocessor(markdown.preprocessors.Preprocessor):
    """Identify dot codeblocks and run them through pydot."""

    BLOCK_RE = re.compile(r'~~~{\s+pydot:(?P<filename>[^\s]+)\s+}\n(?P<content>.*?)~~~', re.DOTALL)

    def run(self, lines):
        """Match and generate diagrams from dot code blocks."""
        text = '\n'.join(lines)
        out = text
        for block_match in self.BLOCK_RE.finditer(text):
            filename = block_match.group(1)
            dot_string = block_match.group(2)
            logger.debug("matched markdown block: %s", dot_string)
            logger.debug("match start/end: %s/%s", block_match.start(), block_match.end())

            # use pydot to turn the text into pydot
            graphs = pydot.graph_from_dot_data(dot_string)
            if not graphs:
                logger.debug("some kind of issue with parsed 'dot' %s", dot_string)
                raise ValueError("error parsing dot text!")

            # encode the image and provide as an inline image in markdown
            encoded_image = base64.b64encode(graphs[0].create_png()).decode('ascii')
            data_path = f'data:image/png;base64,{encoded_image}'
            inline_image = f'![{filename}]({data_path})'

            # replace the image in the output markdown
            out = out.replace(block_match.group(0), inline_image)

        return out.split('\n')


def makeExtension(*args, **kwargs):
    """Provide the extension to the markdown extension loader."""
    return InlinePydot(*args, **kwargs)
