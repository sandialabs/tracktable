#
# Copyright (c) 2014-2020 National Technology and Engineering
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
# winlocate.py -- Find dependencies for binary artifacts in a wheel.
#     Windows-specific.
#
# This module will open up a wheel file, inspect it for binary
# artifacts (presumably compiled extension modules), and try to
# locate any library dependencies for those artifacts.  
#
# You must have dumpbin.exe on your PATH.  This is packaged with
# Microsoft Visual Studio.  If you use the Developer Tools Command
# Prompt shortcut that Visual Studio puts into the Start menu, you
# will have dumpbin available.
#

import csv
import logging
import os
import pprint
import re
import subprocess
import sys
import tempfile
import wheel

import pdb

# NOTE TO SELF: we should also remove DLLs found in C:\Windows

# Libraries in these lists should not be bundled into the wheel,
# either because they are part of Windows itself or have other
# redistribution restrictions.
EXCLUDED_FILENAMES = {
    'windows': [
        r'kernel32\.dll',
        r'api-ms-win-.*\.dll'
        r'bcrypt.dll'
        ],
    'msvc_runtime': [
        r'msvcp\d{3}\.dll',
        r'vcruntime.*\.dll',
        r'concrt\d{3}\.dll'
        ],
    'libpython': [
        r'python\d{2}\.dll'
    ]
}

EXCLUDE_REGEXES = {}

EXCLUDED_DIRECTORIES = [
    'c:\\windows',
    'microsoft visual studio'
]


def find_dll_dependencies(filename):
    """Use dumpbin.exe to find DLL dependencies for a file

    Arguments:
        filename {string}: Filename to interrogate

    Returns:
        List of DLL filenames returned by dumpbin.

    Raises:
        TypeError: file is not a DLL.
        IOError: file could not be opened.
    """

    # Dumpbin output looks like this:
    # Microsoft (R) COFF/PE Dumper Version 14.25.28612.0
    # Copyright (C) Microsoft Corporation.  All rights reserved.
    #
    #
    # Dump of file TracktableCore.dll
    #
    # File Type: DLL
    #
    #   Image has the following dependencies:
    #
    #     boost_date_time-vc142-mt-x64-1_71.dll
    #     boost_log-vc142-mt-x64-1_71.dll
    #     KERNEL32.dll
    #     MSVCP140.dll
    #     bcrypt.dll
    #     VCRUNTIME140.dll
    #     VCRUNTIME140_1.dll
    #     api-ms-win-crt-heap-l1-1-0.dll
    #     api-ms-win-crt-runtime-l1-1-0.dll
    #     api-ms-win-crt-locale-l1-1-0.dll
    #     api-ms-win-crt-string-l1-1-0.dll
    #
    #   Summary
    #
    #         3000 .data
    #         3000 .pdata
    #        14000 .rdata
    #         1000 .reloc
    #         1000 .rsrc
    #        28000 .text
    #
    # The lines we want are those that start with four spaces and
    # end with the string '.dll' or '.DLL'.
    print('DEBUG: Checking dependencies for {}'.format(filename))
    dumpbin_result = subprocess.run(
        ['dumpbin.exe', '/dependents', filename],
        capture_output=True
        )
    # This will raise CalledProcessError if the return code is non-zero.
    dumpbin_result.check_returncode()
    lines = dumpbin_result.stdout.split(b'\r\n')
    dll_line_regex = re.compile(b'^    (\S+\.(dll|DLL))$')
    matches = [dll_line_regex.match(line) for line in lines]
    dll_names = [m.group(1) for m in matches if m is not None]
    # Convert to strings so that we can do case-insensitive 
    # processing
    return [name.decode('utf-8').lower() for name in dll_names]

# ---------------------------------------------------------------

def remove_excluded_files(dll_list, exclusions):
    logger = logging.getLogger(__name__)

    def is_excluded(dll_name):
        #basename = os.path.basename(dll_name)
        for (category, regex_list) in exclusions.items():
            print('Checking file {} against category {}'.format(dll_name, category))
            for regex in regex_list:
                if regex.search(dll_name):
                    logger.warning('Excluding {}: it belongs to category "{}"'.format(
                        dll_name, category
                        ))
                    return True
        return False

    return [dll_name for dll_name in dll_list if not is_excluded(dll_name)]


# ---------------------------------------------------------------

    
def compile_exclusion_regexes(exclusion_lists):
    """Build regexes for exclusions.

    The global exclusion list is a dict where each
    category of exclusions has an entry.  The keys
    are the names of the categories ('windows_system',
    'msvc_runtime') and the values are lists of regular
    expressions that identify libraries to exclude.

    Since we will be using these lists a bunch of times,
    it's polite to compile them to regular expression 
    objects.

    Arguments:
        exclusion_lists {dict}: Dictionary of exclusion
            regexes

    Returns:
        Dictionary of lists of compiled regular expressions
    """

    result = {}
    for (category_name, regex_strings) in exclusion_lists.items():
        compiled_regexes = [re.compile(regex, re.IGNORECASE) for regex in regex_strings]
        result[category_name] = compiled_regexes

    return result


# ---------------------------------------------------------------


def files_in_directory(dirname):
    """Return names of all files in a directory

    Unlike os.walk(), which will recur into subdirectories,
    this function gets just the files in the specified directory.
    Moreover, it filters out directories.

    Arguments:
        dirname {str or bytes}: Directory to search

    Returns:
        List of filenames with paths.  If dirname is of type str,
        the filenames will be strings.  If it is of type
        bytes, the filenames will be bytes.
    
    Raises:
        PermissionError: Couldn't open the directory
    """

    return [direntry.path for direntry in os.scandir(dirname)
            if direntry.is_file()]


# ---------------------------------------------------------------


def split_path(path_env):
    """Parse the Windows PATH environment variable

    Windows uses the semicolon to separate entries in the
    PATH environment variable.  Unfortunately, it is also
    legal to use the semicolon in filenames.  Anyone who
    does that deliberately should be given a stern talking-to.

    Arguments:
        path_env {str}: Raw PATH environment variable

    Returns:
        List of components of PATH
    """
    lines = list(csv.reader([path_env], delimiter=';'))
    return lines[0]


def file_has_desired_extension(filename, extensions):
    return any([filename.endswith(ext) for ext in extensions])

def file_in_excluded_directory(filename, exclusions):
    for exclusion in exclusions:
        if exclusion in filename:
            return True
    return False

# ---------------------------------------------------------------

def file_db_for_directories(search_directories, extensions=None):
    logger = logging.getLogger(__name__)
    unique_directories = set(sd.lower() for sd in search_directories)
    print('DEBUG: {} directories on path, {} unique'.format(
        len(search_directories), len(unique_directories)))

    all_files = []
    for dirname in unique_directories:
        try:
            files_this_dir = files_in_directory(dirname)
            all_files.extend(files_this_dir)
        except FileNotFoundError as e:
            logger.debug('Couldn\'t open directory {}.  Skipping.'.format(dirname))
        except PermissionError as e:
            logger.debug('Permission denied while trying to open directory {}.  Skipping.'.format(dirname))

    if extensions is not None:
        lc_extensions = [ext.lower() for ext in extensions]
    else:
        lc_extensions = []

    file_dict = {}
    for filename in all_files:
        base_filename = os.path.basename(filename).lower()
        if not file_has_desired_extension(base_filename, lc_extensions):
            continue
        # This is the doorway to DLL Hell.
        #
        # The same DLL can be present in many different places on the 
        # filesystem.  We have no way of knowing which one is correct.  
        if base_filename not in file_dict:
            file_dict[base_filename] = filename.lower()

    print('DEBUG: Found {} files in {} search directories with extension filter {}'.format(
        len(file_dict), len(unique_directories), extensions))

    return file_dict


# ---------------------------------------------------------------

def find_file_on_path(filename, file_dict):
    """Check for a given file in a big list

    Suppose that we have a list of all the files on the
    user's PATH including their full pathnames.  We want 
    to know if a particular file is in there.  

    This function will traverse the whole smash and look to see
    if it's there.  

    Arguments:
        filename {str}: Filename to search for
        file_dict {dict}: Dictionary where keys are lowercase
            filenames and values are the full filename + path.
            Get this from file_db_for_directories().

    Returns:
        Filename (with complete path) of desired file if found.
        None otherwise.
    """

    filename_lc = filename.lower()
    return file_dict.get(filename_lc, None)

# ---------------------------------------------------------------

def remove_excluded_directories(filenames, excluded_directories):
    """Remove files whose paths contain excluded directories

    We want to avoid bundling DLLs from places like 
    the Windows system directory (C:\Windows\SYSTEM32).  To do that,
    just filter the list of filenames (which must include paths!)
    against a list of exclusions.

    Arguments:
        filenames {list of str}: Filenames to check
        excluded_directories {list of str}: Directories to exclude

    Returns:
        Filenames that are not in any of the excluded directories

    NOTE:
        Directory names are treated as fragments.  If you include
        'system32', for example, it will exclude all directories
        with 'system32' in their path no matter where on the
        filesystem they are.  Be as specific as you need to in 
        order to avoid this.
    """

    lc_dirnames = [dirname.lower() for dirname in excluded_directories]
    result = []
    for filename in filenames:
        pathname = os.path.dirname(filename).lower()
        file_is_ok = True
        for excluded_dirname in lc_dirnames:
            if excluded_dirname in pathname:
                file_is_ok = False
                break
        if file_is_ok:
            result.append(filename)
    return result


def resolve_dependencies_transitive(filename, search_paths=None):
    """Find all dependent DLLs for the specified file

    This function will extract the list of DLLs that a given file
    depends upon and search the filesystem for each one.  It will
    repeat the process on each of those dependencies.  When the
    process terminates we will have a full list of all the DLLs
    needed to load the given file.

    This function does not make any attempt to filter
    out DLLs that are found in system directories.

    Arguments:
        filename {str}: Filename whose dependencies you want

    Keyword Arguments:
        search_paths {list of str}: Directories to search for
            dependent DLLs.  Defaults to PATH environment variable.

    Returns:
        List of filenames for all dependencies with full paths.
    """

    if search_paths is None:
        search_paths = (
            split_path(os.getenv('PATH', '')) +
            directories_in_subtree('C:\\Windows')
            )
    file_db = file_db_for_directories(search_paths, extensions=['.dll'])

    lc_excluded_directories = [dirname.lower() for dirname in EXCLUDED_DIRECTORIES]

    dependency_queue = find_dll_dependencies(filename)
    resolved = set()
    while len(dependency_queue) != 0:
        dll_name = dependency_queue.pop(0)
        if dll_name in resolved:
            continue
        else:
            if dll_name not in file_db:
                raise FileNotFoundError('Couldn\'t find DLL {}.'.format(dll_name))
            else:
                resolved.add(dll_name)
                if not file_in_excluded_directory(file_db[dll_name], lc_excluded_directories):
                    new_dependencies = find_dll_dependencies(file_db[dll_name])
                    dependency_queue.extend(new_dependencies)

    print('DEBUG: Found {} total dependencies'.format(len(resolved)))
    return [
        file_db[dll_name] for dll_name in resolved
    ]

# -------------------------------------------------------------

def directories_in_subtree(basedir):
    """List all the directories under a base path

    Arguments:
        basedir {str}: Base directory to search

    Returns:
        All directories under base, including base, as full paths
    """

    result = [basedir]
    for (dirpath, dirnames, filenames) in os.walk(basedir):
        for dirname in dirnames:
            result.append(os.path.join(dirpath, dirname))
    return result

# --------------------------------------------------------------

def main():
    if len(sys.argv) != 2:
        print('usage: {} filename.dll'.format(sys.argv[0]))
        return 1

    filename_to_inspect = sys.argv[1]

    pathline = split_path(os.getenv('PATH', ''))
    all_files = file_db_for_directories(
        split_path(os.getenv('PATH', '')),   
        extensions=['.dll'])

    exclusions = compile_exclusion_regexes(EXCLUDED_FILENAMES)

    # YOU ARE HERE
    # 
    # When you find files, keep the lowercased AND the regular-cased version.
    #

    try:
        direct_dependencies = find_dll_dependencies(filename_to_inspect)
        user_dll_names = remove_excluded_files(direct_dependencies, exclusions)
        
        dependencies_with_paths = []
        for dll_name in user_dll_names:
            print('Searching for {} on PATH.'.format(dll_name))
            maybe_match = find_file_on_path(dll_name, all_files)
            if maybe_match:
                print('\tFOUND: {}'.format(maybe_match))
                dependencies_with_paths.append(maybe_match)
            else:
                print('\tNOT FOUND')

        non_system_dlls = remove_excluded_directories(dependencies_with_paths, EXCLUDED_DIRECTORIES)
        #print('Non-system DLLs with paths:')
        #pprint.pprint(non_system_dlls)

        transitive_dependencies = resolve_dependencies_transitive(filename_to_inspect)
        #print('Full dependency list with paths:')
        #pprint.pprint(transitive_dependencies)

        print('Dependency list after removing Windows DLLs:')
        trimmed_deps = remove_excluded_directories(transitive_dependencies,
                                [d.lower() for d in EXCLUDED_DIRECTORIES]
                                )
      
        trimmed_deps = remove_excluded_files(trimmed_deps, exclusions)
        pprint.pprint(trimmed_deps)
        return 0
    except subprocess.CalledProcessError:
        print('ERROR: The file {} is not a DLL or EXE.'.format(filename_to_inspect))
        return 1

if __name__ == '__main__':
    sys.exit(main())