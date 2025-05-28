"""Find the tag (cp313-cp313) that matches a Python version (3.13)"""

import argparse
import re
import sys

def main():
    parser = argparse.ArgumentParser(
        usage=("Find tags for interpreters for Python versions.  You must specify at least "
               "one.  This program will look in /opt/python/cp* to find interpreters "
               "whose version tags are in the list of desired versions, then return the names of "
               "the directories containing them.")
    )
    parser.add_argument("directories_with_tag_names",
                        help="All directories in /opt/python")
    parser.add_argument("desired_version_str",
                        help="All desired Python versions in a space-delimited string")
    args = parser.parse_args()

    # Convert all the versions into (major, minor, abi) tuples
    all_versions_split = []
    text_version_re = re.compile(r"(\d).(\d+)([a-z]*)")

    for full_version in args.desired_version_str.split():
        re_match = text_version_re.match(full_version)
        major = re_match.group(1)
        minor = re_match.group(2)
        abiflags = re_match.group(3)
        all_versions_split.append(("cp", major, minor, abiflags))

    # Remove duplicates
    desired_versions = set(all_versions_split)

    found_versions = []

    tag_version_re = re.compile(r"([a-z]+)(\d)(\d+)-([a-z]+)(\d)(\d+)([a-z]*)")
    directory_names = [
        dirname.strip() for dirname in args.directories_with_tag_names.split()
    ]

    for dirname in directory_names:
        re_match = tag_version_re.match(dirname)
        platform = re_match.group(1)
        major = re_match.group(2)
        minor = re_match.group(3)
        abiflags = re_match.group(7)
        detected_version = (platform, major, minor, abiflags)
        if detected_version in desired_versions:
            readable_version = "".join(detected_version)
            print(f"Found interpreter for {readable_version} in directory {dirname}", file=sys.stderr)
            found_versions.append(dirname)
        # else:
            # print(f"Version {detected_version} not on desired list", file=sys.stderr)

    print("\n".join(found_versions))
    return 0


if __name__ == '__main__':
    sys.exit(main())
