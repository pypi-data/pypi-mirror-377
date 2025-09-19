# incorporeal-cms

A lightweight static site generator for Markdown-based sites.

## Installation and Usage

Something like the following should suffice:

```
% virtualenv --python=python3.9 env-py3.9
% source env-py3.9/bin/activate
% pip install -U pip
% pip install incorporeal-cms
% incorporealcms-build ./path/to/instance ./path/to/output/www/root
```

This will generate the directory suitable for serving by e.g. nginx.

## Creating a Site

Put content, notably Markdown content, inside `./your-instance/pages/` and when you are ready, run the build command
above. When you run `incorporealcms-build`, the following happens:

* Markdown files (ending in `.md`) are rendered via Python-Markdown as `.html` files and output to the static site
  directory. The `.md` files are also copied there, though this behavior may be toggleable in the future.
    * Directory paths (e.g. a request to `/dir/`) can be served via a `/dir/index.md` file, which will generate
      `/dir/index.html`, with the appropriate web server configuration to use `index.html` for directory listings.
* Symlinks to files are retained and mirrored into the output directory, and handled per the web server's configuration,
  whatever it is.
* All other files are copied directly, so images, text files, etc., can be referenced naturally as URLs.

## Configuration

The application is further configured within `./your-instance/config.json`. See `incorporealcms/config.py` for more
information about what you can tweak. Just adding stuff to `Config.py`/`config.json` yourself is trivial if all you need
to do is to refer to it in templates. I've tried to keep the software agnostic to my personal domains, logos, etc.

To do some basic personalization, there are some settings you are probably interested in tweaking, by specifying new
values in `incorporealcms-instance/config.json`:

* `TITLE_SUFFIX` is appended to the title of every page, separated from other title content by a dash.
* `CONTACT_EMAIL` is referred to in error templates.
* `FAVICON` supplies the image used in browser tabs and that kind of thing.

## Development and Contributing

Improvements, new plugins, and etc. are all welcome.

I'm reachable on the fediverse, over email, or on Discord, but if you're looking for an option I prefer, I maintain an
IRC channel, `#incorporeal-cms`, on [my IRC network, Randomus](https://randomus.net/) if you would like a place to hang
out and discuss issues and features and whatnot.

## Author and Licensing

Written by and copyright (C) 2025 Brian S. Stephan (bss@incorporeal.org).

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see
<https://www.gnu.org/licenses/>.

### Content Output

As per [the GPL FAQ entry](https://www.gnu.org/licenses/gpl-faq.en.html#CanIUseGPLToolsForNF), the generated output
(HTML, Atom/RSS feeds, etc.) of this program is *not* subject to the GPLv3 license, aside from cases where e.g.
JavaScript source code, CSS files, and the like are copied into the output directory verbatim, in which case their
license applies, naturally, to only those files.
