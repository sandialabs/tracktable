# Declare all source and object files here.

SRC = test_curv_interpolation.cpp curv_interpolation.cpp

#CXX = gfilt
CXX = colorgcc

OBJ = $(SRC:.cpp=.o)

PROG = example

CXXFLAGS =  -Wall -DBOOST_ALL_DYN_LINK -std=c++11 -Wno-unknown-pragmas -O2 -I/home/mdrinto/local/include

LIBDIRS = -L/home/mdrinto/local/lib

#LIBDIRS = -Wl,-rpath,/ascldap/users/mdrinto/src/tracktable/Build/lib:/ascldap/users/mdrinto/local/lib /home/mdrinto/local/lib/libTracktableDomain.so.1.2.0 /home/mdrinto/local/lib/libTracktableCore.so.1.2.0
LIBS = -lm -lboost_program_options -lboost_date_time -lboost_timer -lboost_regex -lboost_log -lboost_system -lTracktableCore -lTracktableDomain -lpthread

$(PROG): $(OBJ)
	$(CXX) $(CXXFLAGS) -o $(PROG) $(OBJ) $(LIBDIRS) $(LIBS)

$(OBJ)	:

clean:
	/bin/rm -f $(PROG) $(OBJ) core

veryclean:
	/bin/rm -rf $(PROG) $(OBJ) core
