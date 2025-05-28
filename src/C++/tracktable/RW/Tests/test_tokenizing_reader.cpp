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
#include <tracktable/RW/StringTokenizingReader.h>
#include <iostream>
#include <fstream>

int test_tokenizing_reader(const char* filename, bool output_tokens=false)
{
  std::ifstream infile;
  infile.open(filename);

  typedef tracktable::LineReader<> line_reader_type;
  typedef tracktable::StringTokenizingReader<line_reader_type::iterator> token_reader_type;

  line_reader_type line_reader(infile);
  token_reader_type token_reader;
  token_reader.set_input_range(line_reader.begin(), line_reader.end());
  token_reader.set_field_delimiter(",");

  std::vector<int> tokens_per_line;
  for (token_reader_type::iterator token_range_iter = token_reader.begin();
       token_range_iter != token_reader.end();
       ++token_range_iter)
    {
    int num_tokens = 0;
    int num_empty_tokens = 0;
    for (token_reader_type::iterator::iterator token_iter = (*token_range_iter).first;
         token_iter != (*token_range_iter).second;
         ++token_iter)
      {
      if (output_tokens)
        {
        if (num_tokens > 0) std::cout << " || ";
        std::cout << *token_iter;
        }
      if ((*token_iter).size() == 0)
        {
        ++num_empty_tokens;
        }
      ++num_tokens;
      }
    if (output_tokens)
      {
      std::cout << "\n";
      std::cout << "This line had "
                << num_tokens << " tokens total with "<< num_empty_tokens << " empty\n";
      }
    tokens_per_line.push_back(num_tokens);
    }

  if (output_tokens)
    {
    std::cout << "Tokens per line (final results):\n";
    for (size_t i = 0; i < tokens_per_line.size(); ++i)
      {
      std::cout << "Line " << i << ": " << tokens_per_line[i] << " tokens\n";
      }
    }
  std::cout << tokens_per_line.size()  << " lines total read from file\n";
  return 0;
}

int main(int argc, char* argv[])
{
  int num_errors = 0;

  if (argc != 2)
    {
    std::cerr << "usage: "
              << argv[0] << " file_to_read.txt\n";
    return 1;
    }

  char* filename = argv[1];

  num_errors += test_tokenizing_reader(filename);
  return num_errors;
}
