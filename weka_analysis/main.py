
from csv_manager import CsvManager
from weka_manager import WekaManager
from weka_parser import WekaParser
import sys

if len(sys.argv) < 3:
  raise RuntimeError('Need to set input file and output file')

INPUT_FILE = sys.argv[1]
OUTPUT_FILE = sys.argv[2]

parser = None
weka_objects = None
with open(INPUT_FILE, 'r') as weka_file:
  parser = WekaParser(weka_file)
  weka_objects = parser.parse()

weka_manager = WekaManager(weka_objects)
weka_manager.filter_objects()
weka_manager.normalize()

analyze_result = weka_manager.analyze()

with open(OUTPUT_FILE, 'w+') as csv_file:
  csv_manager = CsvManager(csv_file, ['Type', 'Source', 'Target', 'Weight'])
  for relationship, weight in analyze_result.items():
    csv_manager.write_row({
      'Type': 'Undirected',
      'Source': relationship[0],
      'Target': relationship[1],
      'Weight': weight,
    })