from tracktable.examples.example_point_reader_redone import *

def test_point_reader():
  print("Testing the point reader for terrestrial points.")
  print("Configuring parameters")
  infile = open("data/SampleASDI.csv", 'r')
  args = dict()
  args['domain'] = "terrestrial"
  args['delimiter'] = ','
  args['comment_character'] = '#'
  args['object_id'] = 0
  args['timestamp'] = 1
  args['coordinate0'] = 2
  args['coordinate1'] = 3
  args['coordinate2'] = None
  print("Creating the reader.")
  reader = configure_point_reader(infile, **args)
  print("Outputting points to confirm they were read correctly.")
  for x in reader:
    print(x)
  print("Test complete.")
  infile.close()
  
# Will add Jupyter test after to compare