# Copyright (c) 2014-2025, National Technology & Engineering Solutions of
# Sandia, LLC (NTESS). All rights reserved.
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

"""Exceptions used in Tracktable"""

# TODO: Bring BoostPythonException in here

__all__ = [
    "MissingColumnError",
    "NoSuchDomainError"
]

class MissingColumnError(Exception):
    """Code asked for a column not present in the input"""
    def __init__(self, column_name: str):
        super().__init__((
            f"You requested a column '{column_name}' that is not "
            "present in the input source."
        ))
        self.column_name = column_name


class NoSuchDomainError(Exception):
    """Code asked for a point domain that does not exist."""
    def __init__(self, domain_name: str):
        super().__init__((
            f"You requested a point domain '{domain_name}' that is not "
            "supported in this version of Tracktable."
        ))
        self.domain_name = domain_name


class WrongCoordinatesError(Exception):
    def __init__(self, domain: str, expected_num: int, actual_num: int):
        super().__init__((
            f"Point domain {domain} requires {expected_num} coordinates. "
            f"Code supplied {actual_num} instead."
        ))
        self.domain = domain
        self.expected_num = expected_num
        self.actual_num = actual_num