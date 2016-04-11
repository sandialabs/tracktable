# Declare all source and object files here.

SRC = TwoPortals.cpp ParseCommandLine.cpp Portal.cpp Initial.cpp KmlOut.cpp
#CXX = gfilt

OBJ = $(SRC:.cpp=.o)

PROG = two_portal

CXXFLAGS = -Wall -O2 -I/home/mdrinto/local/include

LIBDIRS = -L/home/mdrinto/local/lib
LIBS = -lm -lboost_program_options -lboost_date_time -lboost_timer -lTracktableCore -lTracktableDomain

$(PROG): $(OBJ)
	$(CXX) $(CXXFLAGS) -o $(PROG) $(OBJ) $(LIBDIRS) $(LIBS)

$(OBJ)	:

clean:
	/bin/rm -f $(PROG) $(OBJ) core

veryclean:
	/bin/rm -rf $(PROG) $(OBJ) core
