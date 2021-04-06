#
# Copyright (c) 2014-2021 National Technology and Engineering
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

import argparse
import csv
import logging
import os
import pprint
import re
import shutil
import subprocess
import sys
import tempfile

# NOTE TO SELF: we should also remove DLLs found in C:\Windows

# Libraries in these lists should not be bundled into the wheel,
# either because they are part of Windows itself or have other
# redistribution restrictions.
EXCLUSIONS = {
    'windows': [
        r'kernel32\.dll',
        r'api-ms-win-.*\.dll',
        r'bcrypt.dll',
        r'advapi32.dll',
        r'ws2_32.dll',
        r'secur32.dll'
        ],
    'msvc_runtime': [
        r'msvcp\d{3}\.dll',
        r'vcruntime.*\.dll',
        r'concrt\d{3}\.dll'
        ],
    'libpython': [
        r'^python\d{2}\.dll'
        ],
    'directories': [
        r'c:\\windows',
        r'microsoft visual studio'
        ]
}

def _my_run(arg_list, timeout=None, **kwargs):
    """Internal function: Simulate subprocess.run()

    When we call subprocess.run(), we want to use
    `capture_output=True` for debugging.  Python 3.5 appears to
    lack this option.  This function fakes it.

    All keyword arguments will be passed unmodified to
    `subprocess.Popen()`.

    Arguments:
        arg_list {list of str}: Command to run and arguments

    Returns:
        Dict with 'returncode' set to the process's return code (-1
            if it was killed), 'stdout' set to the process's standard
            output and 'stderr' set to its standard error

    Note:
        Do not supply the `stdout` or `stderr` keyword arguments
        with this function.  We use those ourselves.

    Note:
        If you supply a timeout keyword argument, the process
            will be killed if it doesn't exit before then.
    """

    if 'stdout' in kwargs or 'stderr' in kwargs:
        raise KeyError('stdout and stderr are used internally by _my_run; do not override')

    process = subprocess.Popen(
        arg_list,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **kwargs
        )
    try:
        (stdout, stderr) = process.communicate(timeout=timeout)
        return { 'returncode': process.returncode,
                 'stdout': stdout,
                 'stderr': stderr }
    except subprocess.TimeoutExpired:
        process.kill()
        (stdout, stderr) = process.communicate()
        return { 'returncode': -1,
                 'stdout': stdout,
                 'stderr': stderr }



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
    dumpbin_result = _my_run(['dumpbin.exe', '/dependents', filename])

    # This will raise CalledProcessError if the return code is non-zero.
    if dumpbin_result['returncode'] != 0:
        raise subprocess.CalledProcessError((
            'Result code from dumpbin was {}.').format(dumpbin_result['returncode']))
    lines = dumpbin_result['stdout'].split(b'\r\n')
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
                logging.getLogger(__name__).debug('DLL {} is excluded: matches pattern {} from category {}'.format(filename, regex, category))
                return True
    assert('api-ms-win' not in filename)
    assert('vcruntime' not in filename)
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

def build_file_db(search_directories, extensions=None):
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

#    logger.debug('Found {} files in {} search directories with extension filter {}: {}'.format(
#        len(file_dict), len(unique_directories), extensions, file_dict))

    logger.debug('Found {} files in {} search directories with extension filter {}'.format(
        len(file_dict), len(unique_directories), extensions))

    if len(file_dict) < 15:
        pprint.pprint(file_dict)

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

# -----------------------------------------------------------

def files_in_subtree(root_dir, extensions=None):
    """Find files in a directory tree with desired extensions

    Arguments:
        root_dir {path-like}: Root of directory tree to search

    Keyword arguments:
        extensions {list of str}: Extensions to use as filters.
            Defaults to None, meaning 'include all files'.

    Returns:
        List of files with full paths
    """

    dirlist = directories_in_subtree(root_dir)
    db = build_file_db(dirlist, extensions=extensions)
    return list(db.values())

# ------------------------------------------------------------

def resolve_dependencies_transitive(filename,
                                    file_db,
                                    exclusions=None):
    """Find all dependent DLLs for the specified file

    This function will extract the list of DLLs that a given file
    depends upon and search the filesystem for each one.  It will
    repeat the process on each of those dependencies.  When the
    process terminates we will have a full list of all the DLLs
    needed to load the given file.

    The files to be returned will also be filtered to remove DLLs
    on the exclusion list / in system directories.

    Arguments:
        filename {str}: Filename whose dependencies you want
        file_db {dict}: Database of files to search for dependencies

    Keyword Arguments:
        exclusions {dict}: Dict of regular expressions to check
            to see if file should be excluded from further processing.
            This makes sure we don't try to chase down dependencies
            for system DLLs.
    Returns:
        List of filenames for all dependencies with full paths.
    """

    logger = logging.getLogger(__name__)
    dependency_queue = find_dll_dependencies(filename)
    resolved = set()
    while len(dependency_queue) != 0:
        dll_name = dependency_queue.pop(0)
        if not is_excluded(dll_name, exclusions):
            logger.debug('****** Resolving dependencies for {}'.format(dll_name))
        else:
            logger.debug('Skipping excluded DLL {}'.format(dll_name))
            continue

        if dll_name in resolved:
            continue
        else:
            if dll_name not in file_db:
                raise FileNotFoundError((
                    'Couldn\'t find DLL {} while resolving '
                    'dependencies of {}.').format(dll_name, filename))
            else:
                resolved.add(dll_name)
                full_name = file_db[dll_name]
                if not is_excluded(full_name, exclusions):
                    new_dependencies = find_dll_dependencies(full_name)
                    logging.debug('Adding {} new dependencies for file {}: {}.'.format(len(new_dependencies), dll_name, new_dependencies))
                    dependency_queue.extend(new_dependencies)

    return remove_excluded_files([
        file_db[dll_name] for dll_name in resolved
        ],
        exclusions)

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

def resolve_dependencies_for_wheel(wheel_path,
                                   search_paths=None,
                                   exclusions=None,
                                   extensions=None):
    """Find all the DLLs that need to be added to a wheel

    Arguments:
        wheel_path {str}: Full path to where the wheel has been
            unpacked

    Keyword arguments:
        search_paths {list of str}: Directories to search
            for dependencies.  Defaults to directories
            on the PATH environment variable plus
            C:\Windows.
        exclusions {dict of regexes}: Regular expressions
            indicating files and directories to be excluded
            from dependency lists
        extensions {list of str}: Extensions of binary files
            (defaults to '.dll', '.pyd')

    Returns: dict of {wheel_file: dependency_files}

    Note:
        Before you copy files into the wheel, make sure to
        remove anything that's already in the current directory
        of the file being examined.

    Note:
        Windows also searches the registry key
        HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\
        SessionManager\KnownDLLs.  We do not yet include those.

    """

    if extensions is None:
        extensions = [r'\.dll', r'\.pyd']

    if search_paths is None:
        search_paths = (
            split_path(os.getenv('PATH', '')) +
            directories_in_subtree('C:\\Windows')
        )

    if exclusions is None:
        exclusions = dict()

    logger = logging.getLogger(__name__)
    logger.info('resolve_dependencies_for_wheel has {} exclusion categories.'.format(len(exclusions)))
    logger.info('Building file DB.  This may take some time.')
    main_file_db = build_file_db(search_paths, extensions)
    logger.info('Locating binary artifacts in wheel.  Root directory is {}.'.format(wheel_path))
    files_to_check = files_in_subtree(wheel_path, extensions)

    directories_already_checked = set(search_paths)
    all_dependencies = {}

    full_file_db = dict(main_file_db)

    for filename in files_to_check:
        if is_excluded(filename, exclusions):
            continue

        logger.info('Resolving dependencies for {}.'.format(filename))
        this_directory = os.path.dirname(filename)
        if this_directory not in directories_already_checked:
            logger.info('Adding DLLs in directory containing {}.'.format(filename))
            file_db_this_directory = build_file_db([os.path.dirname(filename)], extensions)
            full_file_db.update(file_db_this_directory)
            directories_already_checked.add(this_directory)

        try:
            all_dependencies[filename] = resolve_dependencies_transitive(filename,
                                                                         file_db=full_file_db,
                                                                         exclusions=exclusions)
        except subprocess.CalledProcessError:
            logger.warning('File {} is not a DLL.  Maybe the extension filter is wrong.'.format(filename))
    return all_dependencies


# --------------------------------------------------------------

def add_dependencies_to_wheel(dependency_results,
                              wheel_path):
    """Add dependency results to an unpacked wheel

    Given the dict that comes from
    resolve_dependencies_for_wheel, copy any missing
    files into appropriate locations in the unpacked
    wheel.

    This function will add dependencies alongside the
    library that loads them so that they will be found
    first in the DLL search process.  It will not
    overwrite files that are already there.

    Arguments:
        dependency_results {dict}: Result of calling
            resolve_dependencies_for_wheel()
        wheel_path {path or str}: Root directory of
            files for unpacked wheel

    Returns:
        List of files added

    Note:
        There are multiple subdirectories in a wheel.
        Make sure to get the right one.
    """

    logger = logging.getLogger(__name__)
    num_files_copied = 0

    files_added_by_directory = dict()
    for (original_file, dependencies) in dependency_results.items():
        logger.debug('Copying dependencies for {}'.format(original_file))
        original_file_path = os.path.dirname(original_file).lower()
        if original_file_path not in files_added_by_directory:
            files_added_by_directory[original_file_path] = set()
        
        if len(files_added_by_directory) > 0:
            logger.debug('Files already in directory: {}'.format(pprint.pformat(files_added_by_directory[original_file_path])))


        for dependency in dependencies:
            dependency_basename = os.path.basename(dependency).lower()
            dependency_path = os.path.dirname(dependency).lower()
            logger.debug('--- Considering dependent library: {}'.format(dependency_basename))
            # We don't need to add files that are already in that
            # directory -- the current directory is always on the
            # DLL search path.
            if dependency_path == original_file_path:
                logger.debug('    Same directory.  Recursive search not needed.')
                continue
            # Don't add files that we've already added
            if dependency_basename in files_added_by_directory[original_file_path]:
                logger.debug('File {} is already in directory {}'.format(dependency_basename, original_file_path))
                continue
            else:
                # OK, add this one!
                logger.debug('Adding file {} to {} for {}'.format(
                    dependency_basename, original_file_path, os.path.basename(original_file)))
                shutil.copy(
                    dependency,
                    os.path.join(original_file_path, os.path.basename(dependency))
                    )
                files_added_by_directory[original_file_path].add(dependency_basename.lower())
                num_files_copied += 1

    logger.info('Copied {} files to resolve dependencies for wheel.'.format(num_files_copied))

# --------------------------------------------------------------

def unpack_wheel(wheel_filename, root_dir):
    """Unpack wheel into desired directory

    Arguments:
        wheel_filename {str or bytes}: Filename of wheel to
            unpack with any necessary path
        root_dir {str, bytes, or Path}: Directory into which
            wheel should be unpacked

    Returns:
        Path to code directory in wheel.  This directory does
        not end with '.data' or '.dist-info'.

    Raises:
        FileNotFoundError: 'wheel' is not on your path
        subprocess.CalledProcessError: Something went wrong with
            the unpacking

    NOTE: The Python wheel module does not expose any documented
          module interface.  We would much rather call it within
          Python than as a subprocess, but that's not currently
          a viable option.
    """

    result = _my_run([
            'wheel', 'unpack',
            '-d', root_dir,
            wheel_filename])

    if result['returncode'] != 0:
        raise subprocess.CalledProcessError((
            'Return code from "wheel unpack" was {}.').format(result['returncode']))
    # There should be only one item in the root directory -- the
    # directory containing the wheel.
    directories = []
    for direntry in os.scandir(root_dir):
        if direntry.is_dir():
            directories.append(direntry.path)
    if len(directories) != 1:
        logging.getLogger(__name__).warning(
            ('WARNING: After unpacking wheel, directory has '
             '{} entries.  We were expecting only one.').format(len(directories)))

    return directories[0]



# --------------------------------------------------------------

def code_dir_inside_wheel(wheel_root):
    """Find the directory that probably contains code

    A wheel can contain several directories:

    foo
    foo.data
    foo.dist-info

    We want to return the one that is not .data and not
    .dist-info.

    Arguments:
        wheel_root {str or path}: Directory of wheel contents

    Returns:
        Path of code directory (we hope)
    """

    # Now we have to find the code directory in there.  Hopefully
    # this is correct...
    for direntry in os.scandir(wheel_root):
        if direntry.is_dir():
            if not (direntry.path.endswith('.data') or
                    direntry.path.endswith('.dist-info')):
                return direntry.path

# --------------------------------------------------------------

def repack_wheel(root_dir, destination_dir):
    """Re-pack wheel from specified directory into specified destination

    Arguments:
        root_dir {str or path}: Top-level directory of wheel.
            This is the directory for the wheel itself (e.g.
            mypackage-1.2), not the directory into which the
            wheel was unpacked.
        destination_dir {str or path}: Directory into which
            the new wheel should be placed

    Returns:
        No return value.

    Raises:
        FileNotFoundError: 'wheel' is not on your path
        subprocess.CalledProcessError: Something went wrong with repacking
        OSError: Destination directory exists but is not writable
    """

    if os.access(destination_dir, os.F_OK):
        if not os.access(destination_dir, os.W_OK):
            raise OSError('Destination directory {} is not writable.'.format(destination_dir))
    else:
        os.mkdir(destination_dir)

    result = _my_run([
        'wheel', 'pack',
        '-d', destination_dir,
        root_dir
        ])
    if result['returncode'] != 0:
        raise subprocess.CalledProcessError((
            'Return code from "wheel pack" was {}.').format(result['returncode']))

# --------------------------------------------------------------

def dumpbin_available():
    try:
        result = subprocess.run(['dumpbin.exe'])
        return True
    except FileNotFoundError:
        return False

# --------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description='Add binary dependencies to a wheel.'
        )
    parser.add_argument(
        '--destination-dir', '-d',
        help='Output directory for modified wheel',
        default='new_wheel'
        )
    parser.add_argument(
        'wheel_file',
        nargs=1,
        help='Wheel to process'
        )
    return parser.parse_args()

# --------------------------------------------------------------

def main():
    if not dumpbin_available():
        print(('ERROR: dumpbin.exe must be on the PATH. The easiest '
               'way to accomplish this is to run this program from '
               'a command prompt started with the Visual Studio '
               'Developer Prompt shortcut.'), file=sys.stderr)
        return 1

    args = parse_args()
    exclusions = compile_exclusion_regexes(EXCLUSIONS)

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logger = logging.getLogger(__name__)

    wheel_filename = args.wheel_file[0]
    with tempfile.TemporaryDirectory(prefix='winlocate') as tempdir:
        logger.debug('Unpacking wheel into {}'.format(tempdir))
        wheel_root = unpack_wheel(wheel_filename, tempdir)
        wheel_code_dir = code_dir_inside_wheel(wheel_root)
        logger.debug('Resolving dependencies')
        dependencies = resolve_dependencies_for_wheel(wheel_code_dir, exclusions=exclusions)
        logger.debug('Adding dependencies to unpacked wheel')
        add_dependencies_to_wheel(dependencies, wheel_root)
        logger.debug('Repacking wheel')
        repack_wheel(wheel_root, args.destination_dir)

    return 0

# YOU ARE HERE:
#
#
# Write a function that takes a DLL, calls resolve_dependencies_transitive, and then
# removes any files that are in the DLL's directory already.
#
# Write a function that copies the remaining DLLs into the directory of the file that
# was being examined.
#

if __name__ == '__main__':
    sys.exit(main())