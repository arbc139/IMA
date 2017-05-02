#!/usr/bin/python

from urllib.parse import quote
import difflib
import math
import pymysql
import re
import sys
import time

get_current_millis = lambda: int(round(time.time() * 1000))
def get_elapsed_seconds(current_time, elapsed_millis):
  return (current_time - elapsed_millis) / 1000.0

START_S_ID = None
if len(sys.argv) > 1:
  START_S_ID = sys.argv[1]

db = pymysql.connect(host='localhost', user='root', password='', db='mesh', charset='utf8')

elapsed_millis = get_current_millis()
# Get all genes in DB.
all_genes = None
with db.cursor(pymysql.cursors.DictCursor) as cursor:
  query = 'SELECT * FROM PROSTATE_GENES WHERE IS_FAMILY IS NULL ORDER BY S_ID' if START_S_ID is None \
    else 'SELECT * FROM PROSTATE_GENES WHERE IS_FAMILY IS NULL AND S_ID > %s ORDER BY S_ID' % (START_S_ID)
  cursor.execute(query)
  all_genes = cursor.fetchall()
print('Find all genes time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))

all_qualifiers = None
with db.cursor(pymysql.cursors.DictCursor) as cursor:
  cursor.execute('SELECT * FROM MESH_QUALIFIER')
  all_qualifiers = cursor.fetchall()
all_descriptors = None
with db.cursor(pymysql.cursors.DictCursor) as cursor:
  cursor.execute('SELECT * FROM MESH_DESCRIPTOR')
  all_descriptors = cursor.fetchall()

# Find with checking family
values = []
for gene in all_genes:
  elapsed_millis = get_current_millis()
  print('Mesh Term:', gene['MESH_TERM'])
  qualifiers = list(filter(lambda qualifier: qualifier['NAME'] == gene['MESH_TERM'], all_qualifiers))
  print('Find qualifier time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
  descriptors = list(filter(lambda descriptor: descriptor['NAME'] == gene['MESH_TERM'], all_descriptors))
  print('Find descriptor time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
  
  tree_numbers = None
  if len(qualifiers) == 1:
    tree_numbers = eval(qualifiers[0]['TREE_NUMBERS'])
  elif len(descriptors) == 1:
    tree_numbers = eval(descriptors[0]['TREE_NUMBERS'])
  else:
    print('There is no mesh term for qualifier and descriptor')
    continue
  
  print('Tree numbers:', tree_numbers)
  
  is_family = False
  for tree_number in tree_numbers:
    escaped_tree_number = re.escape(tree_number)
    qualifiers = list(filter(
      lambda qualifier: re.match('.*%s\\..*' % (escaped_tree_number), qualifier['TREE_NUMBERS']),
      all_qualifiers
    ))
    descriptors = list(filter(
      lambda descriptor: re.match('.*%s\\..*' % (escaped_tree_number), descriptor['TREE_NUMBERS']),
      all_descriptors
    ))
    if len(qualifiers) != 0 or len(descriptors) != 0:
      is_family = True
      break

  print('UPDATE PROSTATE_GENES SET IS_FAMILY=%d WHERE S_ID=%s' % (
    1 if is_family else 0, gene['S_ID']))
  values.append([1 if is_family else 0, gene['S_ID']])
"""
elapsed_millis = get_current_millis()
# Send a query to update PROSTATE_GENES.
with db.cursor(pymysql.cursors.DictCursor) as cursor:
  cursor.executemany(
    'UPDATE PROSTATE_GENES SET IS_FAMILY=%d WHERE S_ID=%s',
    values
  )
db.commit()
print('Update gene time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
"""