# Declare all source and object files here.

SRC = Main.cpp ParseCommandLine.cpp KmlOut.cpp GetMappers.cpp ConvexHull.cpp AssignHeadings.cpp Mapping.cpp

#CXX = gfilt
CXX = colorgcc

OBJ = $(SRC:.cpp=.o)

PROG = tt_main

CXXFLAGS = -Wall -O2 -I/home/mdrinto/local/include -I/home/mdrinto/local/include/tracktable

LIBDIRS = -L/home/mdrinto/local/lib
LIBS = -lm -lboost_program_options -lboost_date_time -lboost_timer -lboost_regex -lTracktableCore -lTracktableDomain

$(PROG): $(OBJ)
	$(CXX) $(CXXFLAGS) -o $(PROG) $(OBJ) $(LIBDIRS) $(LIBS)

$(OBJ)	:

clean:
	/bin/rm -f $(PROG) $(OBJ) core

veryclean:
	/bin/rm -rf $(PROG) $(OBJ) core
