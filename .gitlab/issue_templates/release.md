
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

### Checklist

- [ ] Create release branch from `develop`
- [ ] Bump Libtool version numbers
- [ ] Bump version numbers
    * [ ] Top-level CMakeLists.txt
    * [ ] Documentation/conf.py
    * [ ] Documentation/conf.py.in
    * [ ] Documentation/readthedocs/Doxyfile-readthedocs
    * [ ] src/Python/tracktable/__init__.py
- [ ] Wheels
    * [ ] Build Tracktable Data Wheel
    * [ ] Build Tracktable Wheels
        - [ ] Linux
        - [ ] Windows
        - [ ] MacOS
    * [ ] Test all wheels to make sure they import correctly
    * [ ] Upload wheels to PyPI using `twine` (note: see wiki for instructions on generating API token)
- [ ] Release Notes
    * [ ] Include all merge requests since previous release in CHANGELOG.md
    * [ ] Write human-readable release notes in RELEASE_NOTES.md
      - [ ] Describe new features
      - [ ] Note known issues
    * [ ] Check into release branch
- [ ] Documentation
    * [ ] Build
    * [ ] `.tar.gz` file
    * [ ] `.tar.bz2` file
    * [ ] `.zip` file
    * [ ] Include links on Documentation page
- [ ] Example Notebooks
    * [ ] `.tar.gz` file
    * [ ] `.tar.bz2` file
    * [ ] `.zip` file
    * [ ] Include links on Documentation page
- [ ] Source Code
    * [ ] Check out clean copy
    * [ ] Delete `.git` directory
    * [ ] Make `.tar.gz` version
    * [ ] Make `.tar.bz2` version
    * [ ] Make `.zip` version
- [ ] GitHub Releases
    * [ ] tracktable-data
       - [ ] Upload release from Sandia to GitHub
         * [ ] Push tracktable-data main to personal repository on GitHub
         * [ ] Open pull request to merge into tracktable-data
         * [ ] Approve pull request
       - [ ] Create GitHub release - see wiki for instructions
    * [ ] tracktable-docs
       - [ ] Upload release from Sandia to GitHub
         * [ ] Push tracktable-data main to personal repository on GitHub
         * [ ] Open pull request to merge into tracktable-data
         * [ ] Approve pull request
       - [ ] Create GitHub release - see wiki for instructions
    * [ ] tracktable
       - [ ] Upload release from Sandia to GitHub
         * [ ] Push tracktable-data main to personal repository on GitHub
         * [ ] Open pull request to merge into tracktable-data
         * [ ] Approve pull request
       - [ ] Create GitHub release - see wiki for instructions
         * [ ] Add auxiliary files
           - [ ] Documentation
           - [ ] Source code (`tracktable` only)
           - [ ] Source code (everything included)
           - [ ] Wheels
- Anaconda Packages - see wiki for instructions; depends on GitHub releases
  * [ ] tracktable-data
    - [ ] Fork `github.com/conda-forge/tracktable-data-feedstock`
    - [ ] Create release branch
    - [ ] Update `meta.yaml`
    - [ ] Push to GitHub
    - [ ] Open pull request back into source repository
    - This list will be updated when we learn what happens after that
  * [ ] tracktable
    - [ ] Fork `github.com/conda-forge/tracktable-feedstock`
    - [ ] Create release branch
    - [ ] Update `meta.yaml`
    - [ ] Push to GitHub
    - [ ] Open pull request back into source repository
    - This list will be updated when we learn what happens after that
- [ ] Web Site
    * [ ] Announcement on front page
    * [ ] Release Notes
    * [ ] Links to new documentation
    * [ ] Links to new example notebooks
    * [ ] Links to wheels
    * [ ] Links to source code
- [ ] Announcement
    * [ ] Send to tracktable-develop
