#!/usr/bin/python

from urllib.parse import quote
import difflib
import math
import pymysql
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
  supplemental = None
  with db.cursor(pymysql.cursors.DictCursor) as cursor:
    cursor.execute('SELECT * FROM MESH_SUPPLEMENTAL where NAME = %s', (gene['MESH_TERM'],))
    supplemental = cursor.fetchone()
  print('Supplemental:', supplemental)
  print('Find supplemental time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
  break
  """
  print('UPDATE LUNG_GENES SET MESH_TERM="%s" WHERE S_ID=%s' % (
    full_mesh_term, gene['S_ID']))

  elapsed_millis = get_current_millis()
  # Send a query to update LUNG_GENES.
  with db.cursor(pymysql.cursors.DictCursor) as cursor:
    cursor.execute(
      'UPDATE LUNG_GENES SET MESH_TERM="%s" WHERE S_ID=%s',
      (full_mesh_term, gene['S_ID'])
    )
  db.commit()
  print('Update gene time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
  """