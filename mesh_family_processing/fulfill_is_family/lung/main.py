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
  query = 'SELECT * FROM LUNG_GENES WHERE IS_FAMILY IS NULL ORDER BY S_ID' if START_S_ID is None \
    else 'SELECT * FROM LUNG_GENES WHERE IS_FAMILY IS NULL AND S_ID > %s ORDER BY S_ID' % (START_S_ID)
  cursor.execute(query)
  all_genes = cursor.fetchall()
print('Find all genes time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))

# Find with checking family
values = []
for gene in all_genes:
  elapsed_millis = get_current_millis()
  print('Mesh Term:', gene['MESH_TERM'])
  qualifier = None
  with db.cursor(pymysql.cursors.DictCursor) as cursor:
    cursor.execute('SELECT * FROM MESH_QUALIFIER where NAME = %s', (gene['MESH_TERM'],))
    qualifier = cursor.fetchone()
  print('Qualifier:', qualifier)
  print('Find qualifier time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
  descriptor = None
  with db.cursor(pymysql.cursors.DictCursor) as cursor:
    cursor.execute('SELECT * FROM MESH_DESCRIPTOR where NAME = %s', (gene['MESH_TERM'],))
    descriptor = cursor.fetchone()
  print('Descriptor:', descriptor)
  print('Find descriptor time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
  
  tree_numbers = None
  if qualifier:
    tree_numbers = eval(qualifier['TREE_NUMBERS'])
  elif descriptor:
    tree_numbers = eval(descriptor['TREE_NUMBERS'])
  else:
    print('There is no mesh term for qualifier and descriptor')
    continue
  
  print('Tree numbers:', tree_numbers)
  
  is_family = False
  for tree_number in tree_numbers:
    escaped_tree_number = re.escape(tree_number)
    all_qualifiers = None
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
      print('SELECT * FROM MESH_QUALIFIER where TREE_NUMBERS REGEXP ".*%s\..*"' % (escaped_tree_number))
      cursor.execute('SELECT * FROM MESH_QUALIFIER where TREE_NUMBERS REGEXP ".*%s\..*"' % (escaped_tree_number))
      all_qualifiers = cursor.fetchall()
    all_descriptors = None
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
      print('SELECT * FROM MESH_DESCRIPTOR where TREE_NUMBERS REGEXP ".*%s\..*"' % (escaped_tree_number))
      cursor.execute('SELECT * FROM MESH_DESCRIPTOR where TREE_NUMBERS REGEXP ".*%s\..*"' % (escaped_tree_number))
      all_descriptors = cursor.fetchall()
    all_supplementals = None
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
      print('SELECT * FROM MESH_SUPPLEMENTAL where TREE_NUMBERS REGEXP ".*%s\..*"' % (escaped_tree_number))
      cursor.execute('SELECT * FROM MESH_SUPPLEMENTAL where TREE_NUMBERS REGEXP ".*%s\..*"' % (escaped_tree_number))
      all_supplementals = cursor.fetchall()
    if len(all_qualifiers) == 0 and len(all_descriptors) == 0 and len(all_supplementals) == 0:
      is_family = True
      break

  print('UPDATE LUNG_GENES SET IS_FAMILY=%d WHERE S_ID=%s' % (
    1 if is_family else 0, gene['S_ID']))
  values.append([1 if is_family else 0, gene['S_ID']])

"""
elapsed_millis = get_current_millis()
# Send a query to update LUNG_GENES.
with db.cursor(pymysql.cursors.DictCursor) as cursor:
  cursor.executemany(
    'UPDATE LUNG_GENES SET IS_FAMILY=%d WHERE S_ID=%s',
    values
  )
db.commit()
print('Update gene time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
"""