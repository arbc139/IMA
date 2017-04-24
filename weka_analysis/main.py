
from csv_manager import CsvManager
from weka_manager import WekaManager
from weka_parser import WekaParser

parser = None
weka_objects = None
with open('input/lung_gene_result.txt', 'r') as weka_file:
  parser = WekaParser(weka_file)
  weka_objects = parser.parse()

weka_manager = WekaManager(weka_objects)
weka_manager.normalize()

analyze_result = weka_manager.analyze()

with open('output/lung_gene_relationship.csv', 'w') as csv_file:
  csv_manager = CsvManager(csv_file, ['First', 'Second', 'Score'])
  for relationship, score in analyze_result.items():
    csv_manager.write_row({
      'First': relationship[0],
      'Second': relationship[1],
      'Score': score,
    })