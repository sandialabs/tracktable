
<!--

This template is for creating a Tracktable release that will go out to the world.

-->

# Public Tracktable release

Documentation on this process is available on the wiki for the Tracktable GitLab repository.

### Version Number

<!--
    Example: 1.3.1
-->

### Major/Minor/Patch release?

<!--
    Example: Patch
-->

### Major features in this release

<!--
    Example: Interactive trajectory rendering using Folium
-->

### Major bug fixes in this release

<!--
    Example: Python interpreter crashes on import
-->

## The Process

### Resources

There is a page with details and notes on the release process on our internal wiki.  Go to Tracktable's home page, then Plan (from the sidebar), then Wiki.  It includes information about how to upload wheels to PyPI and how to update our conda-forge recipe so that new packages will be built there.

If those documents do not have what you need, ask Andy.


### Checklist

- [ ] Part 1: Prepare the Code
  * [ ] Create Gitlab issue for release (name it "Release Tracktable 1.x.y")
  * [ ] Create Gitlab merge request with source branch `develop`, target branch `main`
  * [ ] Bump version numbers
    - [ ] Top-level version.txt
      * [ ] Tracktable release
      * [ ] Libtool (`UNIX SO VERSION` - see [Libtool documentation](https://www.gnu.org/software/libtool/manual/html_node/Versioning.html))
    - [ ] `packaging/pyproject.toml`
    - [ ] `packaging/setup.cfg`
    - [ ] `src/Python/tracktable/__init__.py`
  * [ ] Release Notes
    - [ ] Include all merge requests since previous release in CHANGELOG.md
    - [ ] Write human-readable release notes in RELEASE_NOTES.md
      * [ ] Describe new features
      * [ ] Note known issues
    - [ ] Check into release branch
    - [ ] Update `tracktable-docs/Documentation/changelog.rst`
    - [ ] If new authors have come onboard, update `tracktable-docs/Documentation/authors.rst`
  * [ ] Update `documentation_build_environment.yml` with new versions for Tracktable, data packages


- [ ] Part 2: Initial `conda-forge` Deployment
  * [ ] Tag `tracktable` and `tracktable-docs` with `vX.Y.Z-rc1`, push to external Github
  * [ ] Also update `tracktable-data` if it has changed
  * [ ] Fork `git@github.com:conda-force/tracktable-feedstock` into your personal space
  * [ ] Follow instructions on internal Tracktable wiki to build new conda-forge packages for `vX.Y.Z-rc1`
  * [ ] Wait for all checks/builds on Github pull request to pass
  * [ ] Merge pull request
  * [ ] Have a drink or a snack - you've earned it

- [ ] Part 3: Update the Documentation
  * [ ] Make sure documentation builds locally (enable `BUILD_DOCUMENTATION` in CMake)
  * [ ] Test Read the Docs build locally
    - [ ] Create new Conda environment from `documentation_build_environment.yml`
    - [ ] Check out clean source tree
    - [ ] Set environment variable `READTHEDOCS=1`
    - [ ] `cd tracktable-docs/Documentation`
    - [ ] Build with `sphinx-build -b html . ../../../doc-build_test`
  * [ ] Once that works, test Read the Docs build remotely.  There are instructions on the wiki page for running a Tracktable release.

- [ ] Part 4: Wheels
  * [ ] Build `tracktable-data` wheel
  * [ ] Build `tracktable` wheels
    - [ ] Windows: Python 3.10 - 3.13
      * [ ] Test all wheels to make sure they import correctly
    - [ ] Linux: Python 3.9 - 3.13
      * [ ] Test all wheels to make sure they import correctly
    - [ ] MacOS: Python 3.9 - 3.13
      * [ ] Intel build (use Andy's Mac Pro)
      * [ ] Apple Silicon build (use a laptop or `tracktable-build` Mac Mini)
      * [ ] Test all wheels to make sure they import correctly
  * [ ] Upload all wheels to PyPI using `twine` (instructions on wiki)

- [ ] Part 5: GitHub Releases
  * [ ] Assets
    * [ ] Create tarball of pre-rendered notebooks from `tracktable-docs`
    * [ ] Create tarball of all documentation from `tracktable-docs`
  * [ ] Tags
    * [ ] Tag `tracktable` and `tracktable-docs` with `vX.Y.Z`
    * [ ] Push `tracktable` tag to Github
    * [ ] Push `tracktable-docs` tag to Github
    * [ ] Repeat for `tracktable-data` if new version is being released
  * [ ] Release `tracktable-docs`
    * [ ] Go to [https://github.com/sandialabs/tracktable-docs/releases/new]
    * [ ] Select tag `vX.Y.Z`
    * [ ] Write short description of updates
    * [ ] Upload tarballs of pre-rendered notebooks, documentation
    * [ ] Click the big green button to finalize the release
  * [ ] Release `tracktable`
    * [ ] Go to [https://github.com/sandialabs/tracktable/releases/new]
    * [ ] Select tag `vX.Y.Z`
    * [ ] Write short description of updates (latest section from release notes)
    * [ ] Upload tarballs of pre-rendered notebooks, documentation (both repositories get this)
    * [ ] Optional: upload wheels
    * [ ] Click the big green button to finalize the release

- [ ] Part 6: Update Tracktable Home Page
    * [ ] Announcement on front page
    * [ ] Release Notes
    * [ ] Links to new documentation
    * [ ] Links to new example notebooks
    * [ ] Links to wheels at PyPI
    * [ ] Links to source code at Github
- [ ] Announcement
    * [ ] Send to tracktable-develop
