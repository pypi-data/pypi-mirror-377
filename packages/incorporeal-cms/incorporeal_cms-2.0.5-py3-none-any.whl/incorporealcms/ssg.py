"""Build an instance as a static site suitable for serving via e.g. Nginx.

SPDX-FileCopyrightText: © 2025 Brian S. Stephan <bss@incorporeal.org>
SPDX-License-Identifier: GPL-3.0-or-later
"""
import argparse
import logging
import os
import shutil
import stat
import tempfile

from termcolor import cprint

from incorporealcms import __version__, init_instance
from incorporealcms.error_pages import generate_error_pages
from incorporealcms.feed import generate_feed
from incorporealcms.markdown import handle_markdown_file_path

logger = logging.getLogger(__name__)


class StaticSiteGenerator(object):
    """Generate static site output based on the instance's content."""

    def __init__(self, instance_dir: str, output_dir: str, extra_config=None):
        """Create the object to run various operations to generate the static site.

        Args:
            instance_dir: the directory from which to read an instance format set of content
            output_dir: the directory to write the generated static site to
        """
        self.instance_dir = os.path.abspath(instance_dir)
        self.output_dir = os.path.abspath(output_dir)

        # initialize configuration with the path to the instance
        init_instance(self.instance_dir, extra_config)

    def build(self):
        """Build the whole static site."""
        # putting the temporary directory next to the desired output so we can safely rename it later
        tmp_output_dir = tempfile.mkdtemp(dir=os.path.dirname(self.output_dir))
        cprint(f"creating temporary directory '{tmp_output_dir}' for writing", 'green')

        # copy core content
        pages_dir = os.path.join(self.instance_dir, 'pages')
        self.build_in_destination(pages_dir, tmp_output_dir)

        # copy the program's static dir
        program_static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        static_output_dir = os.path.join(tmp_output_dir, 'static')
        try:
            os.mkdir(static_output_dir)
        except FileExistsError:
            # already exists
            pass
        self.build_in_destination(program_static_dir, static_output_dir, convert_markdown=False)

        # generate the feeds
        cprint("generating feeds", 'green')
        generate_feed('atom', self.instance_dir, tmp_output_dir)
        generate_feed('rss', self.instance_dir, tmp_output_dir)

        # generate the error pages
        cprint("generating error pages", 'green')
        generate_error_pages(tmp_output_dir)

        # move temporary dir to the destination
        old_output_dir = f'{self.output_dir}-old-{os.path.basename(tmp_output_dir)}'
        if os.path.exists(self.output_dir):
            cprint(f"renaming '{self.output_dir}' to '{old_output_dir}'", 'green')
            os.rename(self.output_dir, old_output_dir)
        cprint(f"renaming '{tmp_output_dir}' to '{self.output_dir}'", 'green')
        os.rename(tmp_output_dir, self.output_dir)
        os.chmod(self.output_dir,
                 stat.S_IWUSR | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        # TODO: unlink old dir above? arg flag?

    def build_in_destination(self, source_dir: str, dest_dir: str, convert_markdown: bool = True) -> None:
        """Walk the source directory and copy and/or convert its contents into the destination.

        Args:
            source_dir: the directory to copy into the destination
            dest_dir: the directory to place copied/converted files into
            convert_markdown: whether or not to convert Markdown files (or simply copy them)
        """
        cprint(f"copying files from '{source_dir}' to '{dest_dir}'", 'green')
        for base_dir, subdirs, files in os.walk(source_dir):
            logger.debug("starting to build against %s || %s || %s", base_dir, subdirs, files)
            # remove the absolute path of the directory from the base_dir
            relpath = os.path.relpath(base_dir, source_dir)
            base_dir = relpath if relpath != '.' else ''
            # create subdirs seen here for subsequent depth
            for subdir in subdirs:
                self.build_subdir_in_destination(source_dir, base_dir, subdir, dest_dir)

            # process and copy files
            for file_ in files:
                if file_[0] == '.':
                    cprint(f"skipping {file_}", 'yellow')
                    continue
                self.build_file_in_destination(source_dir, base_dir, file_, dest_dir, convert_markdown)

    def build_subdir_in_destination(self, source_dir: str, base_dir: str, subdir: str, dest_dir: str) -> None:
        """Create a subdir (which might actually be a symlink) in the output dir.

        Args:
            source_dir: the absolute path of the location in the instance, contains subdir
            base_dir: the relative path of the location in the instance, contains subdir
            subdir: the subdir in the instance to replicate in the output
            dest_dir: the output directory to place the subdir in
        """
        dst = os.path.join(dest_dir, base_dir, subdir)
        absolute_dir = os.path.join(source_dir, base_dir, subdir)
        logger.debug("checking if %s is a symlink or not", absolute_dir)
        if os.path.islink(absolute_dir):
            logger.debug("symlink; raw destination is %s", os.path.realpath(absolute_dir))
            # keep the link relative to the output directory
            src = self.symlink_to_relative_dest(source_dir, absolute_dir)
            print(f"creating directory symlink '{dst}' -> '{src}'")
            os.symlink(src, dst, target_is_directory=True)
        else:
            print(f"creating directory '{dst}'")
            try:
                os.mkdir(dst)
            except FileExistsError:
                # already exists
                pass

    def build_file_in_destination(self, source_dir: str, base_dir: str, file_: str, dest_dir: str,
                                  convert_markdown=False) -> None:
        """Create a file (which might actually be a symlink) in the output dir.

        Args:
            source_dir: the absolute path of the location in the instance, contains subdir
            base_dir: the relative path of the location in the instance, contains subdir
            file_: the file in the instance to replicate in the output
            dest_dir: the output directory to place the subdir in
        """
        dst = os.path.join(dest_dir, base_dir, file_)
        absolute_file = os.path.join(source_dir, base_dir, file_)
        logger.debug("checking if %s is a symlink or not", absolute_file)
        if os.path.islink(absolute_file):
            logger.debug("symlink; raw destination is %s", os.path.realpath(absolute_file))
            # keep the link relative to the output directory
            src = self.symlink_to_relative_dest(source_dir, absolute_file)
            print(f"creating symlink '{dst}' -> '{src}'")
            os.symlink(src, dst, target_is_directory=False)
            if src.endswith('.md') and convert_markdown:
                # we also need to make a .html symlink so that web server configs
                # pick up the "redirect"
                second_src = src.removesuffix('.md') + '.html'
                second_dst = dst.removesuffix('.md') + '.html'
                print(f"creating symlink '{second_dst}' -> '{second_src}'")
                os.symlink(second_src, second_dst, target_is_directory=False)

        else:
            src = os.path.join(source_dir, base_dir, file_)
            print(f"copying file '{src}' -> '{dst}'")
            shutil.copy2(src, dst)

            # render markdown as HTML
            if src.endswith('.md') and convert_markdown:
                rendered_file = dst.removesuffix('.md') + '.html'
                print(f"rendering file '{src}' -> '{rendered_file}'")
                try:
                    content = handle_markdown_file_path(src, source_dir)
                except UnicodeDecodeError:
                    # perhaps this isn't a markdown file at all for some reason; we
                    # copied it above so stick with tha
                    cprint(f"{src} has invalid bytes! skipping", 'yellow')
                else:
                    with open(rendered_file, 'w') as dst_file:
                        dst_file.write(content)

    def symlink_to_relative_dest(self, base_dir: str, source: str) -> str:
        """Given a symlink, make sure it points to something inside the instance and provide its real destination.

        This is made to be relative to the location of the symlink in all
        circumstances, in order to avoid breaking out of the instance or output
        dirs.

        Args:
            base_dir: the full absolute path of the instance's pages dir, which the symlink destination must be in.
            source: the symlink to check
        Returns:
            what the symlink points at
        """
        if not os.path.realpath(source).startswith(base_dir):
            raise ValueError(f"symlink destination {os.path.realpath(source)} is outside the instance!")
        # this symlink points to realpath inside base_dir, so relative to the source, the symlink dest is...
        return os.path.relpath(os.path.realpath(source), os.path.dirname(source))


def build():
    """Build the static site generated against an instance directory."""
    parser = argparse.ArgumentParser(
        description="Build the static site generated against an instance directory.",
    )
    parser.add_argument(
        'instance_dir', help="path to instance directory root (NOTE: the program will go into pages/)"
    )
    parser.add_argument(
        'output_dir', help="path to directory to output to (NOTE: the program must be able to write into its parent!)"
    )
    args = parser.parse_args()

    cprint(f"incorporealcms-build v{__version__} Copyright (C) 2025 Brian S. Stephan <bss@incorporeal.org>", 'green')
    # check output path before doing work
    if not os.path.isdir(args.output_dir):
        # if it doesn't exist, great, we'll just move the temporary dir later;
        # if it exists and is a dir, that's fine, but if it's a file, we should error
        if os.path.exists(args.output_dir):
            raise ValueError(f"specified output path '{args.output_dir}' exists as a file!")

    site_gen = StaticSiteGenerator(args.instance_dir, args.output_dir)
    site_gen.build()
