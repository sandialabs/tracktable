# CHANGE LOG

This file contains a list of the merge requests (each with one-line summary)
that went into each release of Tracktable starting with 1.7.0.

Each entry is formatted as follows:

#<MERGE REQUEST NUMBER>: Short description of issue

Entries are ordered newest-to-oldest based on merge date.  Contact
tracktable-questions at sandia dot gov if you have questions about
any given one.

### TRACKTABLE 1.7.2

- 339: Prefer offline Folium packages when available
- 340: Python docs target must depende on extension libraries
- 338: Fix miscellaneous build warnings
- 332: solid colored trajectories weren't animating correctly.
- 320: added anim_loop parameter and passed to timestampedgeojson
- 334: Resolve "Magic call in Cartopy backend causes errors"
- 333: Update build scripts for Python 3.12, 3.13
- 335: Rename tutorial notebooks to match names in tracktable-docs
- 331: Fix deprecated iterator usage
- 330: Bump C++ version to 20
- 329: Update CI environemnts for new Boost packages, VS 2022
- 325: Add dev and CI YML files for new Python versions
- 326: Clean C add_test macro
- 324: Update tracktable-data version to 1.7.3
- 317: Add shared libraries to Python install
- 313: Migrate wheel-building process away from invoking setup.py
- 315: Fix unary_function warnings
- 312: Fix compile error in catch2.hpp

### TRACKTABLE 1.7.1

- 313: Resolve "Migrate wheel-building process away from invoking setup.py"
- 315: Resolve "Fix unary_function warnings"
- 314: Resolve "Fix compile error in catch2.hpp"
- 311: Resolve "Add Python 3.11 to Linux packaging"
- 310: Make desired manylinux tag a parameter to BuildWheel
- 312: Update manylinux tag to 2014
- 309: Resolve "Great Fit Circle - wrong?"
- 308: Resolve "Unbound variable error in build_osx_wheels"
- 307: Change all OSX references to MacOS
- 300: Hotfix: propagate CI changes to MacOS packaging script
- 306: Add missing items to release checklist
- 304: Fix wheel installation by fixing version number in __init__.py
- 303: Resolve "Add boost-cpp to MacOS conda environment"
- 302: Resolve 'Add missing comma in setup-generic'

### TRACKTABLE 1.7.1

- 313: Resolve "Migrate wheel-building process away from invoking setup.py" 
- 315: Resolve "Fix unary_function warnings"
- 314: Resolve "Fix compile error in catch2.hpp"
- 311: Resolve "Add Python 3.11 to Linux packaging"
- 310: Make desired manylinux tag a parameter to BuildWheel
- 312: Update manylinux tag to 2014
- 309: Resolve "Great Fit Circle - wrong?"
- 308: Resolve "Unbound variable error in build_osx_wheels"
- 307: Change all OSX references to MacOS
- 300: Hotfix: propagate CI changes to MacOS packaging script
- 306: Add missing items to release checklist
- 304: Fix wheel installation by fixing version number in __init__.py
- 303: Resolve "Add boost-cpp to MacOS conda environment"
- 302: Resolve 'Add missing comma in setup-generic'

### HOTFIXES TO TRACKTABLE 1.7.0

- 302: Syntax error in dependencies in setup-generic.py

### TRACKTABLE 1.7.0

- 298: Update ReadTheDocs config to use libmamba
- 296: Conda YML per OS and Python version
- 293: Add brand new CHANGELOG for 1.7.0 and future releases
- 294: Update PyPI tags for Python 3.11
- 295: Fix nbconvert validation error on documentation notebooks
- 285: Potential crash when reading point data containing Unicode
- 291: Fix scale-bar rendering in Mapmaker tests
- 290: Fixed C_GREAT_CIRCLE_FIT (Failed) and C_PointGenerator (Failed)
- 289: Build wheels for Python 3.11
- 288: Restore local Linux wheel-building ability
- 287: Resolve "Add animate to render_trajectories"
- 283: Resolve "Move examples.data_generators to data_generators module"
- 286: Update docs for distance() to indicate that you can do point<->trajectory and trajectory<->trajectory distance
- 282: Resolve "Update Existing Traj Loading Code To Leverage General Loader"
- 280: Resolve "Update Or Remove Example Python Scripts"
- 281: Resolve "Update Tutorial And Analytic Demo Filenames"
- 276: Resolve "Add coastal data access to Tracktable"
- 279: Resolve "Setting a property to None should fail gracefully or not at all"
- 236: Resolve "Add Ability To Render Movies Directly From Render Module"
- 278: Resolve "Add Project Badges To Repo"
- 277: DeprecatedDeclaration.h left out of CMakeLists file
- 275: Resolve "Nightly Documentation Builds"
- 274: Resolve "Increase Parallel Job Threads in Linux CI/CD"
- 272: Resolve "Automated Python Code Coverage"
- 273: Resolve "Update Linux CI/CD Docker Container"
- 271: Resolve "Add setup.py, CMake infrastructure to create development wheels"
- 270: Resolve "Create a singular location of tracktable's version"
- 269: Resolve "Static Code Analysis"
- 268: Resolve "Automated Coverage Reporting"
- 263: Resolve "Automated Nightly Builds of Tracktable Develop and Main"
- 68: better str(), repr() for BasePoint
- 264: Resolve "Create data packages with sample data"
- 265: Resolve "Improved RTD Build Capabilities / New Docs Repo"
- 267: Resolve "Folium Heatmap Creation Missing Params"
- 260: Resolve "Feature: render airports and/or maritime ports"
- 266: Resolve "Upgrade CI/CD infrastructure with Python linter and additional tests"
- 262: Resolve "Update copyright to 2022"
- 256: Resolve "Feature: Add maritime ports to Tracktable"
- 257: Resolve "General Method for load"
- 254: Resolve "Update setup-generic.py"
- 259: Resolve "Tutorial05B.ipynb is too large"
- 261: Resolve "Complete rebuild of Ubuntu 20.04 Docker image"
- 256: Resolve "Remove contents of master branch"
- 242: Resolve "Verify documentation on RTD prior to 1.6 release"
- 253: Update RTD Conf


