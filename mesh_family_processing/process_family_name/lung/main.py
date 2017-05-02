#!/usr/bin/python

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
  query = 'SELECT * FROM LUNG_GENES ORDER BY S_ID' if START_S_ID is None \
    else 'SELECT * FROM LUNG_GENES WHERE S_ID > %s ORDER BY S_ID' % (START_S_ID)
  cursor.execute(query)
  all_genes = cursor.fetchall()
print('Find all genes time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))

for gene in all_genes:
  if not gene['HGNC_FAMILY_NAME'] or not '|' in gene['HGNC_FAMILY_NAME']:
    continue
  
  family_names = re.sub('\'', '', gene['HGNC_FAMILY_NAME']).split('|')
  print('gene:', gene)
  print('splitted:', family_names)
  
  max_name_score = 0
  for family_name in family_names:
    # Get a name similarity score between MeSH query and HGNC family name.
    name_score = difflib.SequenceMatcher(
      None,
      re.sub('\'', '', gene['MESH_NAME']).lower(),
      family_name.lower()
    ).ratio()
    if max_name_score < name_score:
      max_name_score = name_score
  
  elapsed_millis = get_current_millis()
  # Send a query to update LUNG_GENES.
  with db.cursor(pymysql.cursors.DictCursor) as cursor:
    cursor.execute(
      'UPDATE LUNG_GENES SET NAME_SCORE=%s WHERE S_ID=%s',
      (max_name_score, gene['S_ID'])
    )
  db.commit()
  print('Update gene time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
