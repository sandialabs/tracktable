======================
Sample Project Example
======================

.. note:: This example is specific to Linux. Windows and
   Mac projects will need to be modified accordingly to properly
   build and execute.

This example demonstrates a sample standalone C++ project
that uses Tracktable as a library. The sample project structure
and files can be found in the source code distribution in the
directory ``tracktable/Examples/Sample_Project``. To run the
commands below ensure that your current working directory is
``tracktable/Examples/Sample_Project``.

This mini-project is not part of the tracktable build system. Instead,
it is a template demonstrating how to create your own program using
Tracktable as one of your libraries. Below you will find the sample
project source code and the commands to build and execute it.

.. code-block:: c++
   :caption: Project Main
   :linenos:

    #include <tracktable/Core/PointCartesian.h>
    #include <tracktable/Domain/Cartesian2D.h>

    int main(int argc, char* argv[])
    {
        typedef tracktable::domain::cartesian2d::CartesianPoint2D MyPointType;

        MyPointType point1(10, 10);
        MyPointType point2(20, 20);
        MyPointType point3;

        point3 = tracktable::interpolate(point1, point2, 0.25);

        std::cout << "Awesome point 1: " << point1 << std::endl
                  << "Awesome point 2 above point 1: " << point2 << std::endl
                  << "Cool interpolated point at 0.25 from 1 to 2: " << point3 << std::endl;

        return 0;
    }

This script will run all of the following commands with contextual output:

.. code-block:: console

    $ sh run-test.sh

This will make a build directory with:

.. code-block:: console

    $ mkdir build

Change into the build directory:

.. code-block:: console

    $ cd build

Create the makefiles:

.. code-block:: console

    $ cmake ..

Build the program:

.. code-block:: console

    $ make

And run the program:

.. code-block:: console

    $ ./coolprogram

