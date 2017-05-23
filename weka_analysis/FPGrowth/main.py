
from csv_manager import CsvManager
from weka_manager import WekaManager
from weka_parser import WekaParser
import sys

def parse_commands(argv):
  from optparse import OptionParser
  parser = OptionParser('"')
  parser.add_option('-i', '--inputFile', dest='input_file')
  parser.add_option('-o', '--outputFile', dest='output_file')
  
  options, otherjunk = parser.parse_args(argv)
  return options

options = parse_commands(sys.argv[1:])

parser = None
weka_objects = None
with open(options.input_file, 'r') as weka_file:
  parser = WekaParser(weka_file)
  weka_objects = parser.parse()

weka_manager = WekaManager(weka_objects)
weka_manager.filter_objects()
# weka_manager.normalize()

analyze_result = weka_manager.analyze()
analyze_result = weka_manager.normalize_weights(analyze_result)

with open(options.output_file, 'w+') as csv_file:
  csv_manager = CsvManager(csv_file, ['Type', 'Source', 'Target', 'Weight'])
  for relationship, weight in analyze_result.items():
    csv_manager.write_row({
      'Type': 'Undirected',
      'Source': relationship[0],
      'Target': relationship[1],
      'Weight': weight,
    })