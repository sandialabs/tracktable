#
# Copyright (c) 2014-2023 National Technology and Engineering
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
# This test case exercises the trajectory point loader on data 
# containing non-ASCII characters.  Depending on how a file is
# opened in Python ("r" for text or "rb" for binary), read() will
# return either `str` or `bytes` objects.  The len() method on `bytes`
# returns the number of bytes in the string.  The len() method on `str`
# returns the number of code points (Unicode character equivalents).
# Depending on the glyph being encoded, each code point requires
# between 1 and 4 bytes.
#
# This is problematic when we come to the point of reading data
# into a buffer in C++ because we need to know exactly how many bytes
# we're getting.  Our solution is in 
# tracktable/PythonWrapping/PythonFileLikeObjectStreams.h.  
#



import logging
import sys

from tracktable.domain import terrestrial

logger = logging.getLogger(__name__)

def points_from_file(infile):
    reader = terrestrial.TrajectoryPointReader(infile)
    reader.comment_character = '#'  
    reader.field_delimiter = ','    
    reader.quote_character = '"'

    reader.object_id_column = 0         
    reader.coordinates[0] = 2           # longitude 
    reader.coordinates[1] = 3           # latitude
    reader.timestamp_column = 1        
    reader.set_real_field_column('altitude', 6) 
    reader.set_real_field_column('heading', 5) 
    reader.set_real_field_column('utf8_text', 18)

    return list(reader)
    
    
    
def test_loader_csv_bytes(filename):
    logger.info("Testing CSV loader with bytes object")
    with open(filename, "rb") as infile:
        points = points_from_file(infile)
        

def test_loader_csv_string(filename):
    logger.info("Testing CSV loader with str to force len() mismatch")
    with open(filename, "r", encoding="utf8") as infile:
        points = points_from_file(infile)


def main():
    test_loader_csv_bytes(sys.argv[1])
    test_loader_csv_string(sys.argv[1])
    

if __name__ == '__main__':
    sys.exit(main())
