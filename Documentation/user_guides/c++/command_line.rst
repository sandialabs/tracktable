.. _user-guide-cpp-command-line:

============
Command Line
============

.. attention:: Tracktable's C++ interface does currently have
   command line factories available however they have not been
   integrated into Tracktable's main components. This means,
   for example, that you will not be able to call Tracktable's
   C++ ``AssembleTrajectories`` function directly from the
   command line. However, these factories can be integrated into
   other programs utilizing Tracktable's C++ interface to enable
   a command line interface for that program

-------------------------------
Enabling Command Line Factories
-------------------------------

The C++ interface contains multiple command line factories that allow for easy integration
of command line parameters for a compiled program. All of the command line factories are
wrapped thinly wrapped ``boost::program_options``. The provided factories are as follows:

    * The :cpp:class:`CommandLineFactory` class generates the basic ``help`` CLI input that
      will output the provided help text for the given program. This factory also allows
      for user-generated options to be added to a program's CLI. This can include, for example,
      options such as ``input``, ``output`` and ``tolerance``.
    * The :cpp:class:`PointReaderFromCommandLine` is a derived class from :cpp:class:`CommandLineFactory`
      that inlcudes all of the various options that are specific for initializing and using
      ``tracktable::PointReader`` from the command line.
    * The :cpp:class:`AssemblerFromCommandLine` is a derived class from :cpp:class:`CommandLineFactory`
      that inlcudes all of the various options that are specific for initializing and using
      ``tracktable::AssembleTrajectories`` from the command line.

Adding command line factories with custom options and initializing exisitng
factories is as simple as:

.. code-block:: c++
   :linenos:

   #include <tracktable/CommandLineFactories/AssemblerFromCommandLine.h>
   #include <tracktable/CommandLineFactories/PointReaderFromCommandLine.h>

   boost::program_options::options_description commandLineOptions;
   commandLineOptions.add_options()("help", "Print help");

   // Create command line factories
   tracktable::PointReaderFromCommandLine<PointT> readerFactory;
   tracktable::AssemblerFromCommandLine<TrajectoryT> assemblerFactory;
   // Add options from the factories
   readerFactory.addOptions(commandLineOptions);
   assemblerFactory.addOptions(commandLineOptions);

   // And a command line option for output
   commandLineOptions.add_options()("output", bpo::value<std::string>()->default_value("-"),
                                   "file to write to (use '-' for stdout), overridden by 'separate-kmls'");

   /** Boost program options using a variable map to tie everything together.
    * one parse will have a single variable map. We need to let the factories know
    * about this variable map so they can pull information out of it */
   auto vm = std::make_shared<boost::program_options::variables_map>();
   readerFactory.setVariables(vm);
   assemblerFactory.setVariables(vm);

Once the factories are initialized and the custom options are added the command
line needs to be parsed

.. code-block:: c++
   :linenos:

   // Parse the command lines, don't forget the 'notify' after
   try {
     // We use this try/catch to automatically display help when an unknown option is used
     boost::program_options::store(
     boost::program_options::command_line_parser(_argc, _argv).options(commandLineOptions).run(), *vm);
     boost::program_options::notify(*vm);
   } catch (boost::program_options::error e) {
     std::cerr << e.what();
     std::cerr << helpmsg << "\n\n";
     std::cerr << commandLineOptions << std::endl;
     return 1;
   }
   /** Parsing will give an error of an incorrect option is used, but it won't
    * display the help unless we tell it too */
   if (vm->count("help") != 0) {
     std::cerr << helpmsg << "\n\n";
     std::cerr << commandLineOptions << std::endl;
     return 1;
   }

After the inputs are parsed then the program can perform any necessary operations
on the data or values being passed into the program.

Once the program is compiled into an executable it can be run
identically to other command line programs.

.. code-block:: console

   $ ./assemble --input=/data/flights.tsv --output=/data/flights.trj

.. note:: This command is specific to Linux and Mac. Windows
   machines will have a different command line call.