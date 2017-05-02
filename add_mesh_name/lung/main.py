#!/usr/bin/python

from http_wrapper import HttpWrapper
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
# Get all preprocessed MeSH terms in DB.
all_processed = None
with db.cursor(pymysql.cursors.DictCursor) as cursor:
  query = 'SELECT * FROM LUNG_PROCESSED ORDER BY S_ID' if START_S_ID is None \
    else 'SELECT * FROM LUNG_PROCESSED WHERE S_ID > %s ORDER BY S_ID' % (START_S_ID)
  cursor.execute(query)
  all_processed = cursor.fetchall()
print('Find all processed time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))

hgnc_http = HttpWrapper('http://rest.genenames.org')

def get_max_score_doc(result_docs):
  return max(result_docs, key = lambda doc: doc['score'])

# Search using P_NAME from processed rows.
for processed in all_processed:
  # Workaround: Except for % character
  if '%' in processed['P_NAME']:
    continue
  
  elapsed_millis = get_current_millis()
  original = None
  with db.cursor(pymysql.cursors.DictCursor) as cursor:
    cursor.execute('SELECT * FROM LUNG_GENES where S_ID = %s', (processed['S_ID'],))
    original = cursor.fetchone()
  print('Get lung genes time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
  if not original:
    continue

  elapsed_millis = get_current_millis()
  response = None
  while True:
    try:
      # Hgnc response
      response = hgnc_http.request(
        '/search/' + quote(processed['P_NAME']), 'GET', '', ''
      )['response']
    except:
      print('HGNC request failed, so retry after 5 seconds')
      time.sleep(5)
      continue
    else:
      print('HGNC response time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
      break

  # Ignore empty docs, not equal to response's max score.
  if not response['docs'] or \
    (original and not math.isclose(original['MAX_SCORE'], response['maxScore'], abs_tol=0.01)):
    continue
  
  max_doc = get_max_score_doc(response['docs'])
  
  elapsed_millis = get_current_millis()
  gene_family_info = None
  with db.cursor(pymysql.cursors.DictCursor) as cursor:
    cursor.execute('SELECT * FROM GENES_FAMILY where APPROVED_SYMBOL=%s', (max_doc['symbol'],))
    gene_family_info = cursor.fetchone()
  print('Find gene family time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))

  if not gene_family_info:
    continue

  # Get a name similarity score between MeSH query and HGNC family name.
  name_score = difflib.SequenceMatcher(None, processed['P_NAME'].lower(), gene_family_info['GENE_FAMILY_NAME'].lower()).ratio()

  print('UPDATE LUNG_GENES SET MESH_NAME="%s", HGNC_FAMILY_NAME="%s", NAME_SCORE=%s WHERE S_ID=%s' % (
    processed['P_NAME'], gene_family_info['GENE_FAMILY_NAME'], name_score, processed['S_ID']))

  elapsed_millis = get_current_millis()
  # Send a query to update LUNG_GENES.
  with db.cursor(pymysql.cursors.DictCursor) as cursor:
    cursor.execute(
      'UPDATE LUNG_GENES SET MESH_NAME="%s", HGNC_FAMILY_NAME="%s", NAME_SCORE=%s WHERE S_ID=%s',
      (processed['P_NAME'], gene_family_info['GENE_FAMILY_NAME'], name_score, processed['S_ID'])
    )
  db.commit()
  print('Update gene time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))

