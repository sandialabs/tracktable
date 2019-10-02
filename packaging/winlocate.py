#
# Copyright (c) 2014-2017 National Technology and Engineering
# Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
# with National Technology and Engineering Solutions of Sandia, LLC,
# the U.S. Government retains certain rights in this software.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# winlocate.py -- find dependencies using dumpbin and windows path
#   locates first level dependencies beginning with "TrackTable"
#   and "boost" and ending with ".dll"
# Run in msbuildtools command line or dumpbin.exe must be on path.

import os
import subprocess
import re

def locate_file(file):
    
    output = []
    
    process = subprocess.Popen(['dumpbin', '/dependents', file], stdout=subprocess.PIPE)
    out, err = process.communicate()
    
    lines = str(out).split('\r\n')
    
    pattern = '((boost|[Tt]racktable)+([a-zA-Z0-9\s_\\.\-\(\):])+.dll)'

    library_depends = 'DEPENDS \n'
    for line in lines:
        matches = re.findall(pattern, line)
        
        if matches is not None:
            for match in matches:
                dll_name = match[0]
                output.append(dll_name)
    
    return output
    
def locate_dir(inputdir, extension):
    library_output = []
    
    for subdir, dirs, files in os.walk(inputdir):
         for file in files:
            ext = os.path.splitext(file)[-1].lower()[1:]
            if ext == extension:
                library_output = library_output + locate_file(inputdir + "\\" + file)
                
    return set(library_output)

if __name__ == "__main__":
    
    import argparse
    import glob
    
    parser = argparse.ArgumentParser(description='Returns a reasonable list of Boost and TrackTable dependencies')
    parser.add_argument('inputdir', help='input directory')
    parser.add_argument('extension', help='dll extension')
    args = parser.parse_args()
    
    dlls = locate_dir(args.inputdir, args.extension)
    
    support_libraries = []
    for file in dlls:
        for dir in os.environ['Path'].split(';'):
            found_depends = glob.glob(dir + "\\" + file)
            if len(found_depends) > 0:
                support_libraries.extend(found_depends)
                break
    
    print(support_libraries)
    