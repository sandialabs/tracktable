/*
 * Copyright (c) 2014-2023 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include <tracktable/RW/LineReader.h>
#include <iostream>
#include <fstream>
#include <cstdlib>

int test_line_reader(int expected_num_lines, const char* filename)
{
  std::ifstream infile;
  infile.open(filename);
  int num_lines = 0;

  typedef tracktable::LineReader<> reader_type;

  reader_type reader(infile);


  for (reader_type::iterator iter = reader.begin();
       iter != reader.end();
       ++iter)
    {
    ++num_lines;
    }

  std::cout << "test_line_reader: Read "
            << num_lines
            << " lines from file "
            << filename << "\n";

  if (num_lines != expected_num_lines)
    {
    return 1;
    }
  else
    {
    return 0;
    }
}

int main(int argc, char* argv[])
{
  int num_errors = 0;

  if (argc != 3)
    {
    std::cerr << "usage: "
              << argv[0] << " expected_num_lines file_to_read.txt\n";
    return 1;
    }

  int expected_num_lines = atoi(argv[1]);
  char* filename = argv[2];

  num_errors += test_line_reader(expected_num_lines, filename);
  return num_errors;
}
