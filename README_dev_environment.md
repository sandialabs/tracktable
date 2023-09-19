# Setting up a Tracktable development environment

If you're running Anaconda, you can find YML files for development
environments in tracktable/conda_dev_environments/<platform>/*.yml.  
Each one specifies a specific Python version.  MacOS and Linux variants
also include the utilities you'll need to build redistributable wheels
(binary Python install packages).

Even if you're not using Anaconda, the contents of these files are a
guide to what you'll need to install in order to build Tracktable
from source.

The file `tracktable_dev_environment.md` in this directory is a 
platform-agnostic, Python-version-agnostic version that will work if
all you want to do is play with Tracktable's source code.  

