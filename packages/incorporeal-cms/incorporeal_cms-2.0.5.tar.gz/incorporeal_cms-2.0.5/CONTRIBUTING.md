# How to Contribute

incorporeal-cms is a personal project seeking to implement a simpler, cleaner form of what would
commonly be called a "CMS". I appreciate any help in making it better.

incorporeal-cms is made available under the GNU General Public License version 3.

## Opening Issues

Issues should be posted to my Gitea instance at
<https://git.incorporeal.org/bss/incorporeal-cms/issues>. I'm not too picky about format, but I
recommend starting the title with "Improvement:", "Bug:", or similar, so I can do a high level of
prioritization.

## Contributions

### Sign Offs/Custody of Contributions

I do not request the copyright of contributions be assigned to me or to the project, and I require no provision that I
be allowed to relicense your contributions. My personal oath is to maintain inbound=outbound in my open source projects,
and the expectation is authors are responsible for their contributions.

I am following the [Developer Certificate of Origin (DCO)](https://developercertificate.org/), reproduced below. The DCO
is a way for contributors to certify that they wrote or otherwise have the right to license their code contributions to
the project. Contributors must sign-off that they adhere to these requirements by adding a `Signed-off-by` line to their
commit message, and/or, for frequent contributors, by signing off on their entry in `MAINTAINERS.md`.

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.


Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```

This process is followed by a number of open source projects, most notably the Linux kernel. Here's the gist of it:

```
[Your normal Git commit message here.]

Signed-off-by: Random J Developer <random@developer.example.org>
```

`git help commit` has more info on adding this:

```
-s, --signoff
    Add Signed-off-by line by the committer at the end of the commit log
    message. The meaning of a signoff depends on the project, but it typically
    certifies that committer has the rights to submit this work under the same
    license and agrees to a Developer Certificate of Origin (see
    http://developercertificate.org/ for more information).
```

### Submitting Contributions

I don't expect contributors to sign up for my personal Gitea in order to send contributions, but it
of course makes it easier. If you wish to go this route, please sign up at
<https://git.incorporeal.org/bss/incorporeal-cms> and fork the project. People planning on
contributing often are also welcome to request access to the project directly.

Otherwise, contact me via any means you know to reach me at, or <bss@incorporeal.org>, to discuss
your change and to tell me how to pull your changes.

### Guidelines for Patches, etc.

* Cloning
    * Clone the project. I would advise using a pull-based workflow where I have access to the hosted
      repository --- using my Gitea, cloning to a public GitHub, etc. --- rather than doing this over
      email, but that works too if we must.
    * Make your contributions in a new branch, generally off of `master`.
    * Send me a pull request when you're ready, and we'll go through a code review.
* Code:
    * Keep in mind that I strive for simplicity in the software. It serves files and renders
      Markdown, that's pretty much it. Features around that function are good; otherwise, I need
      convincing.
    * Follow the style precedent set in the code. Do **not** use Black, or otherwise reformat existing
      code. I like it the way it is and don't need a militant tool making bad decisions about what is
      readable.
    * `tox` should run cleanly, of course.
    * Almost any change should include unit tests, and also functional tests if they provide a feature
      to the CMS functionality. For defects, include unit tests that fail on the unfixed codebase, so I
      know exactly what's happening.
* Commits:
    * Squash tiny commits if you'd like. I prefer commits that make one atomic conceptual change
      that doesn't affect the rest of the code, assembling multiple of those commits into larger
      changes.
    * Follow something like [Chris Beams's post](https://chris.beams.io/posts/git-commit/) on
      formatting a good commit message.
    * Please make sure your Author contact information is stable, in case I need to reach you.
    * Consider cryptographically signing (`git commit -S`) your commits.
