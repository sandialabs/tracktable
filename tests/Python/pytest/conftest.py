# Copyright (c) 2014-2025 National Technology and Engineering
# Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
# with National Technology and Engineering Solutions of Sandia, LLC,
# the U.S. Government retains certain rights in this software.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""PyTest fixtures for Tracktable tests"""

import os.path

import pytest

@pytest.fixture
def current_file_directory() -> str:
    return os.path.dirname(os.path.abspath(__file__))

@pytest.fixture
def repository_root(current_file_directory: str) -> str:
    # Go up until we find LICENSE.txt
    here = current_file_directory
    while not os.path.exists(os.path.join(here, "LICENSE.txt")):
        here = os.path.normpath(os.path.join(here, ".."))
    return here

@pytest.fixture
def tracktable_data_path(repository_root: str) -> str:
    return os.path.join(
        repository_root,
        "tracktable-data",
        "tracktable-data",
        "tracktable_data"
    )

@pytest.fixture
def some_other_path() -> str:
    return "/tmp"

@pytest.fixture
def ground_truth_path(tracktable_data_path: str) -> str:
    return os.path.join(
        tracktable_data_path,
        "internal_test_data"
    )
