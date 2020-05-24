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
EXCLUSIONS = {
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
        ],
    'directories': [
        r'c:\\windows',
        r'microsoft visual studio'
        ]
}


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
    """Filter a DLL list to remove excluded files

    We maintain a dictionary of regular expressions for filenames
    and directory names that indicate DLLs that should not be
    redistributed.  This function filters a list of DLLs to remove
    any entry that matches one of those regular expressions.

    Arguments:
        dll_list {list of str}: Filenames with full paths
        exclusions {dict}: category_name -> list of regexp mapping

    Returns:
        Elements of dll_list that do not match any of the exclusions
    """

    return [dll_name for dll_name in dll_list if not is_excluded(dll_name, exclusions)]


def is_excluded(filename, exclusions):
    """Test a filename (with path) against an exclusion list

    We maintain a dictionary of regular expressions for filenames
    and directory names that indicate DLLs that should not be
    redistributed.  This function filters a list of DLLs to remove
    any entry that matches one of those regular expressions.

    Arguments:
        filename {str}: Filename with path
        exclusions {dict}: category_name -> list of regexp mapping

    Returns:
        True if filename matches any exclusions, false otherwise
    """
    for (category, regex_list) in exclusions.items():
        for regex in regex_list:
            if regex.search(filename):
                return True
    return False


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


# ---------------------------------------------------------------

def file_db_for_directories(search_directories, extensions=None):
    """Compile a database of all files in a set of directories

    Since searching a filesystem is an expensive operation, we
    do it once and cache the results.  This function takes
    a list of directories (specified as full paths) and returns
    a dictionary containing all the files, structured as follows:

    {
        file_basename: filename_with_full_path
    }

    ...where the file base name is just the filename (no path),
    full_path_lowercase is the filename with path, all lowercase,
    and full_path_original is the filename with path and
    whatever case the filesystem reports.

    You can ask for certain types of files by supplying a list
    of extensions for the 'extensions' keyword argument.  Anything
    you supply will be compiled into a regular expression.  

    Arguments:
        search_directories {list of str}: Paths to search

    Keyword arguments:
        extensions {list of str}: Extensions of file types you
            want returned (default None, meaning include all types)
            Not case-sensitive.

    Returns:
        Dictionary mapping file base name -> file full path
    """

    # Assemble the list of extensions into a singular regular
    # expression
    if extensions is not None:
        alternatives =  '|'.join(extensions)
        extension_re_string = '({})$'.format(alternatives)
        extension_re = re.compile(extension_re_string, re.IGNORECASE)
    else:
        extension_re = None

    logger = logging.getLogger(__name__)
    
    unique_directories = set(sd.lower() for sd in search_directories)
    all_files = []
    for dirname in unique_directories:
        try:
            files_this_dir = files_in_directory(dirname)
            all_files.extend(files_this_dir)
        except FileNotFoundError as e:
            logger.debug('Couldn\'t open directory {}.  Skipping.'.format(dirname))
        except PermissionError as e:
            logger.debug('Permission denied while trying to open directory {}.  Skipping.'.format(dirname))

    file_dict = {}
    for filename in all_files:
        base_filename = os.path.basename(filename).lower()
        if extension_re is not None and extension_re.search(filename) is None:
            continue
        # This is the doorway to DLL Hell.
        #
        # The same DLL can be present in many different places on the 
        # filesystem.  We have no way of knowing which one is correct.  
        if base_filename not in file_dict:
            file_dict[base_filename] = filename

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


def resolve_dependencies_transitive(filename, 
                                    search_paths=None,
                                    include_file_location=True,
                                    exclusions=None):
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
        include_file_location {boolean}: If true, the search paths
            will be extended to include the directory that the file
            is in.  This reflects the fact that the DLL search 
            process starts in the file's current directory.
        exclusions {dict}: Dict of regular expressions to check
            to see if file should be excluded from further processing.
            This makes sure we don't try to chase down dependencies
            for system DLLs.
    Returns:
        List of filenames for all dependencies with full paths.
    """

    if search_paths is None:
        search_paths = (
            split_path(os.getenv('PATH', '')) +
            directories_in_subtree('C:\\Windows')
            )
    if include_file_location:
        search_paths.append(os.path.dirname(filename))

    file_db = file_db_for_directories(search_paths, extensions=['\.dll'])

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
                full_name = file_db[dll_name]
                if not is_excluded(full_name, exclusions):
                    new_dependencies = find_dll_dependencies(full_name)
                    dependency_queue.extend(new_dependencies)

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

    exclusions = compile_exclusion_regexes(EXCLUSIONS)

    try:
        
        transitive_dependencies = resolve_dependencies_transitive(filename_to_inspect, exclusions=exclusions)
        #print('Full dependency list with paths:')
        #pprint.pprint(transitive_dependencies)

        trimmed_deps = remove_excluded_files(transitive_dependencies, exclusions)
        trimmed_deps = transitive_dependencies    
        print('Dependency list after removing excluded DLLs:')
        pprint.pprint(trimmed_deps)
        return 0
    except subprocess.CalledProcessError:

        print('ERROR: The file {} is not a DLL or EXE.'.format(filename_to_inspect))
        return 1

if __name__ == '__main__':
    sys.exit(main())