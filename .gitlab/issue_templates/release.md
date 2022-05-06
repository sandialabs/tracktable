<!--

This template is for creating a Tracktable release that will go out to the world.

-->

# Public Tracktable release

### Version Number

<!--
    Example: 1.3.1
-->


### Checklist

- [ ] Create release branch and accompanying merge request from `develop`
- [ ] Bump Tracktable version number in `version.txt`
- [ ] Bump Libtool version numbers in `version.txt`
    - Reference https://www.gnu.org/software/libtool/manual/html_node/Libtool-versioning.html on how to update the Libtool version
- [ ] Release Notes
    - [ ] Compile from issues since previous version
    - [ ] Note known issues
    - [ ] Add release notes to RTD changelog (remember it's in `reST` format and title/section underlines *must* match)
    - [ ] Push to release branch
- [ ] Merge release branch
- [ ] Merge `develop` into main
- [ ] Create a release tag on `main`
- [ ] Push Tracktable `main` to `sandialabs/tracktable` on GitHub
- [ ] Push Tracktable-Data `main` to `sandialabs/tracktable-data` on GitHub
    - If Tracktable-Data was untouched or recently released then this step can be skipped 
- [ ] Push Tracktable-Docs `main` to `sandialabs/tracktable-docs` on GitHub
- [ ] Create GitHub release under `sandialabs/tracktable`
- [ ] Wheels
    - [ ] Build Wheels (Trigger release build pipeline in Gitlab CI/CD against `main` branch, build time: ~2 hours)
        - [ ] Linux
        - [ ] Windows
        - [ ] MacOS
    - [ ] Generate GPG signatures
    - [ ] Upload wheels to PyPI
    - [ ] Upload to GitHub release's assets
- [ ] Anaconda Package (Do these steps on a branch in a fork of `conda-forge/tracktable-feedstock` after the code is released on GitHub)
    - [ ] Create release branch
    - [ ] Update version number
    - [ ] (Optional) Update build number if subsequent build of the same version otherwise build number is `0`
    - [ ] Update sha256 value
        - Command for getting sha256 value is: `curl -sL {GitHub source code tarball url} | openssl sha256` i.e. `curl -sL https://GitHub.com/sandialabs/tracktable/archive/refs/tags/v<release tag version>.tar.gz | openssl sha256`
    - [ ] Push changes to branch
    - [ ] Open PR to merge into upstream master
- [ ] Documentation
    - [ ] Build
        - The documentation *should've* been built during the CI/CD Build 
    - [ ] `.tar.gz` file
    - [ ] `.zip` file
    - [ ] Upload to GitHub release's assets
    - [ ] Include links on Documentation page
- [ ] Example Notebooks
    - [ ] Clear notebooks of output 
    - [ ] `.tar.gz` file
    - [ ] `.zip` file
    - [ ] Upload to GitHub release's assets
    - [ ] Include links on Documentation page
- [ ] Web Site
    - [ ] Announcement on front page
    - [ ] Release Notes
    - [ ] Links to new documentation
    - [ ] Links to new example notebooks
    - [ ] Links to wheels
    - [ ] Links to Anaconda package
    - [ ] Links to source code
- [ ] Announcement
    - [ ] Send to tracktable-develop
- [ ] Finalize
    - [ ] Publish updates to `https://tracktable.sandia.gov`
