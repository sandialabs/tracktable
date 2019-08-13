from tracktable.domain import all_domains as ALL_DOMAINS
import importlib
import itertools

def configure_point_reader(infile, **kwargs):
  domain = kwargs['domain']
  if domain.lower() not in ALL_DOMAINS:
    raise KeyError("Domain '{}' is not in list of installed domains ({}).".format(domain, ', '.join(ALL_DOMAINS)))
  else:
    domain_to_import = 'tracktable.domain.{}'.format(domain.lower())
    domain_module = importlib.import_module(domain_to_import)
  
  reader = domain_module.TrajectoryPointReader()
  reader.input = infile
  reader.comment_character = kwargs['comment_character']
  reader.field_delimiter = kwargs['delimiter']
  
  if kwargs['object_id'] is not None:
    reader.object_id_column = kwargs['object_id']
  if kwargs['timestamp'] is not None:
    reader.timestamp_column = kwargs['timestamp']
  if kwargs['coordinate0'] is not None:
    reader.coordinates[0] = int(kwargs['coordinate0'])
  if kwargs['coordinate1'] is not None:
    reader.coordinates[1] = int(kwargs['coordinate1'])
  if kwargs['coordinate2'] is not None:
    reader.coordinates[2] = int(kwargs['coordinate2'])
  return reader