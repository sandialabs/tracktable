<!--

This template is for creating a Tracktable release that will go out to the world.

-->

# Public Tracktable release

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
- [ ] Bump Libtool version numbers in `version.txt`
    - Reference https://www.gnu.org/software/libtool/manual/html_node/Libtool-versioning.html on how to update the Libtool version
- [ ] Bump Tracktable version number in `version.txt`
- [ ] Wheels
    * [ ] Build Wheels
        - [ ] Linux
        - [ ] Windows
        - [ ] MacOS
    * [ ] Generate GPG signatures
    * [ ] Upload wheels to PyPI
    * [ ] Upload wheels to Cascade
- [ ] Anaconda Package (Do these steps in a fork of `conda-forge/tracktable-feedstock` after the code is released on github)
    * [ ] Create release branch
    * [ ] Update version number
    * [ ] (Optional) Update build number if subsequent build of the same version
    * [ ] Update sha256 value
        - Command is: curl -sL {tarball url} | openssl sha256
    * [ ] Push changes to branch
    * [ ] Open PR to merge into upstream master
- [ ] Release Notes
    * [ ] Compile from issues since previous version
    * [ ] Note known issues
    * [ ] Add release notes to RTD changelog (remember it's in reST format and title underlines *must* match)
    * [ ] Check into release branch
- [ ] Documentation
    * [ ] Build
    * [ ] `.tar.gz` file
    * [ ] `.zip` file
    * [ ] Upload to Cascade
    * [ ] Include links on Documentation page
- [ ] Example Notebooks
    * [ ] `.tar.gz` file
    * [ ] `.zip` file
    * [ ] Upload to Cascade
    * [ ] Include links on Documentation page
- [ ] Source Code
    * [ ] Check out clean copy
    * [ ] Delete `.git` directory
    * [ ] Make `.tar.gz` version
    * [ ] Make `.tar.bz2` version
    * [ ] Make `.zip` version
    * [ ] Upload to Cascade
- [ ] Web Site
    * [ ] Announcement on front page
    * [ ] Release Notes
    * [ ] Links to new documentation
    * [ ] Links to new example notebooks
    * [ ] Links to wheels
    * [ ] Links to Anaconda package
    * [ ] Links to source code
- [ ] Announcement
    * [ ] Send to tracktable-develop
- [ ] Finalize
    * [ ] Create and handle merge request for release branch
    * [ ] Publish updates on Cascade to `https://tracktable.sandia.gov`
    * [ ] Push source code to `sandialabs/tracktable` on Github
