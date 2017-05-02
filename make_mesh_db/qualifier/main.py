
import xml.etree.ElementTree as et
import pymysql
import time

get_current_millis = lambda: int(round(time.time() * 1000))
def get_elapsed_seconds(current_time, elapsed_millis):
  return (current_time - elapsed_millis) / 1000.0

db = pymysql.connect(host='localhost', user='root', password='', db='mesh', charset='utf8')

elapsed_millis = get_current_millis()
root = et.parse('../input/qual2017.xml').getroot()
print('Parse xml time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))

elapsed_millis = get_current_millis()
records = root.findall('QualifierRecord')
print('Find all records time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))

rows = []
for record in records:
  uid = record.findtext('QualifierUI')
  name = record.find('QualifierName').findtext('String')
  tree_numbers = []
  for tree_number_record in record.findall('TreeNumberList'):
    tree_numbers.append(tree_number_record.findtext('TreeNumber'))
  
  print('INSERT INTO MESH_QUALIFIER (UID, NAME, TREE_NUMBERS) VALUES (%s, %s, %s)' % (
    uid, name, str(tree_numbers)))
  
  rows.append([uid, name, str(tree_numbers)])

elapsed_millis = get_current_millis()
# Send a query to insert MESH_QUALIFIER.
with db.cursor(pymysql.cursors.DictCursor) as cursor:
  cursor.executemany(
    'INSERT INTO MESH_QUALIFIER (UID, NAME, TREE_NUMBERS) VALUES (%s, %s, %s)',
    rows
  )
db.commit()
print('Insert mesh db time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
