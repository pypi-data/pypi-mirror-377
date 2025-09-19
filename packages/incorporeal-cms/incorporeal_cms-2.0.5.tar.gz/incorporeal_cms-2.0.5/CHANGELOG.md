# CHANGELOG

Included is a summary of changes to the project, by version. Details can be found in the commit history.

## v2.0.5

### Features

* The Markdown parser replaces links to e.g. `[Page](page.md)` with a href of `page`, rather than the Markdown source
  specifying a link of `page` explicitly. This allows for some improved site navigation when browsing the Markdown
  files, e.g. when going to files in Vim, or browsing a site in a Git web UI.

### Miscellaneous

* `tox.ini` also runs tests in a Python 3.13 environment now.
* Some trivial bumps to CI requirements.

## v2.0.4

### Bugfixes

* With some significant refactoring, files are now handled better with respect to relative paths, which fixes an issue
  with symlink pages only properly getting resolved to their target if the symlink was in the `pages/` root rather than
  a subdir.

## v2.0.3

### Bugfixes

* Symlinks for a `.md` file that are to be served by the web server also need a `.html` symlink pointed to the generated
  file, since the web server is looking for HTML files when serving paths.

### Miscellaneous

* The project now comes with the GPLv3 "or any later version" clause.

## v2.0.2

### Bugfixes

* Paths for files in the `pages/` root no longer have an extra `./` in them, which made URLs look ugly and also added an
  extra blank breadcrumb in the breadcrumbs.

### Improvements

* `custom-static` in the instance dir is now ignored and has no special handling --- put static files in `pages/static/`
  like all the other files that get copied. This also fixes a bug where the build errored if the directory didn't exist.
* Some README typos fixed.

## v2.0.1

### Improvements

* The `Image` tag in Markdown files no longer requires the full URL to be specified. Now `Config.BASE_HOST` is
  prepended to the tag value, which should be the full path to the image.
* `.files` are skipped when copying files to the SSG output directory.

## v2.0.0

### Features

* The project has been rewritten as a static site generator. This is of course a larger change than one line, so see the
  commit involved for the nitty gritty.
* Notably, this means I am now --- yes :( --- shipping some JavaScript, to handle the style switching, which is all
  client-side now.
* CHANGELOG.md added.
