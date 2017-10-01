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

"""
This file contains compatibility routines that let us use
Tracktable with Python 2 and Python 3.
"""

from __future__ import print_function, division, absolute_import

import sys

import codecs
import csv
import warnings

def open_backport(
        filename,
        mode='r',
        buffering=-1,
        encoding=None,
        errors=None,
        newline=None,
        closefd=True,
        opener=None
        ):

    if newline is not None:
        warnings.warn('tracktable.compatibility.open_backport: newline is not supported in Python 2')
    if not closefd:
        warnings.warn('tracktable.compatibility.open_backport: closefd is not supported in Python 2')
    if opener is not None:
        warnings.warn('tracktable.compatibility.open_backport: opener is not supported in Python 2')

    return codecs.open(
        filename=filename,
        mode=mode,
        encoding=encoding,
        errors=errors,
        buffering=buffering
        )



class UTF8Recoder:
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)
    def __iter__(self):
        return self
    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeCSVDictReader_py2:
    def __init__(
            self,
            f,
            dialect=csv.excel,
            encoding="utf-8-sig",
            reader_class=csv.DictReader,
            **kwds):

        f = UTF8Recoder(f, encoding)
        self.reader = reader_class(f, dialect=dialect, **kwds)
        self.encoding = encoding

    def next(self):
        '''next() -> unicode
        This function reads and returns the next line as a Unicode string.
        '''

        row = self.reader.next()

        if type(row) == dict:
            result = {}
            for (key, value) in row.items():
                result[unicode(key, self.encoding)] = unicode(value, self.encoding)

            else:
                pass
        else:
            result = [unicode(s, "utf-8") for s in row]

        return result

    def __iter__(self):
        return self

if sys.version_info[0] > 2:
    UnicodeCSVDictReader = csv.DictReader
else:
    UnicodeCSVDictReader = UnicodeCSVDictReader_py2
