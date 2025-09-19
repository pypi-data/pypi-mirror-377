"""Create generic figures with captions.

SPDX-FileCopyrightText: © 2022 Brian S. Stephan <bss@incorporeal.org>
SPDX-License-Identifier: GPL-3.0-or-later
"""
import re
from xml.etree.ElementTree import SubElement  # nosec B405

import markdown


class FigureExtension(markdown.Extension):
    """Wrap the markdown prepcoressor."""

    def extendMarkdown(self, md):
        """Add FigureBlockProcessor to the Markdown instance."""
        md.parser.blockprocessors.register(FigureBlockProcessor(md.parser), 'figure', 100)


class FigureBlockProcessor(markdown.blockprocessors.BlockProcessor):
    """Process figures."""

    # |> thing to put in the figure
    # |: optional caption for the figure
    # optional whatever else, like maybe an attr_list
    figure_regex = re.compile(r'^[ ]{0,3}\|>[ ]{0,3}(?P<content>[^\n]*)')
    caption_regex = re.compile(r'^[ ]{0,3}\|:[ ]{0,3}(?P<caption>[^\n]*)')

    def test(self, parent, block):
        """Determine if we should process this block."""
        lines = block.split('\n')
        return bool(self.figure_regex.search(lines[0]))

    def run(self, parent, blocks):
        """Replace the top block with HTML."""
        block = blocks.pop(0)
        lines = block.split('\n')

        # consume line and create a figure
        figure_match = self.figure_regex.search(lines[0])
        lines.pop(0)
        content = figure_match.group('content')
        figure = SubElement(parent, 'figure')
        figure.text = content
        if lines:
            if caption_match := self.caption_regex.search(lines[0]):
                # consume line and add the caption as a child of the figure
                lines.pop(0)
                caption = caption_match.group('caption')
                figcaption = SubElement(figure, 'figcaption')
                figcaption.text = caption
        if lines:
            # other lines are mysteries, might be attr_list, so re-append
            # make sure there's a child to hang the rest (which is maybe an attr_list?) off of
            # this is probably a bad hack
            if not len(list(figure)):
                SubElement(figure, 'span')
            rest = '\n'.join(lines)
            figure[-1].tail = f'\n{rest}'


def makeExtension(*args, **kwargs):
    """Provide the extension to the markdown extension loader."""
    return FigureExtension(*args, **kwargs)
