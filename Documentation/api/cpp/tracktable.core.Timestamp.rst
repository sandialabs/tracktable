.. _cpp_timestamp_reference:

====================
Timestamp Module
====================


---------------
Module Contents
---------------

.. todo:: ``jan_1_1900``, ``time_from_string``, ``time_to_string``, ``no_such_timestamp``, ``is_timestamp_valid``, ``truncate_fractional_seconds``, ``round_to_nearest_second``,
          ``hours``, ``minutes``, ``seconds``, ``milliseconds``, ``microseconds``, ``days``, ``set_default_timestamp_output_format``,
          ``default_timestamp_output_format``, ``set_default_timestamp_input_format``, ``default_timestamp_input_format``
          throw errors when parsed by Breathe so documentation isn't generated for these functions.
          The reason being, Breathe doesn't easily support overloaded functions utilizing ``doxygenfunction::``, need to figure out
          how to handle the manually declared overloaded functions.

.. doxygentypedef:: Timestamp
.. doxygentypedef:: Duration
.. doxygentypedef:: Date
..
    doxygenfunction:: tracktable::jan_1_1900
.. doxygenfunction:: tracktable::BeginningOfTime
..
    doxygenfunction:: tracktable::time_from_string
..
    doxygenfunction:: tracktable::time_to_string
..
    doxygenfunction:: tracktable::no_such_timestamp
..
    doxygenfunction:: tracktable::is_timestamp_valid
..
    doxygenfunction:: tracktable::truncate_fractional_seconds
..
    doxygenfunction:: tracktable::round_to_nearest_second
..
    doxygenfunction:: tracktable::hours
..
    doxygenfunction:: tracktable::minutes
..
    doxygenfunction:: tracktable::seconds
..
    doxygenfunction:: tracktable::milliseconds
..
    doxygenfunction:: tracktable::microseconds
..
    doxygenfunction:: tracktable::days
.. doxygenfunction:: tracktable::imbue_stream_with_timestamp_output_format
..
    doxygenfunction:: tracktable::set_default_timestamp_output_format
..
    doxygenfunction:: tracktable::default_timestamp_output_format
..
    doxygenfunction:: tracktable::set_default_timestamp_input_format
..
    doxygenfunction:: tracktable::default_timestamp_input_format