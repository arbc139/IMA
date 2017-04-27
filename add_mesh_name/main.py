#!/usr/bin/python

from http_wrapper import HttpWrapper
from urllib.parse import quote
import difflib
import math
import pymysql
import sys

START_S_ID = None
if len(sys.argv) > 1:
  START_S_ID = sys.argv[1]

db = pymysql.connect(host='localhost', user='root', password='', db='mesh', charset='utf8')

# Get all preprocessed MeSH terms in DB.
all_processed = None
with db.cursor(pymysql.cursors.DictCursor) as cursor:
  query = 'SELECT * FROM LUNG_PROCESSED ORDER BY S_ID' if START_S_ID is None \
    else 'SELECT * FROM LUNG_PROCESSED WHERE S_ID > %s ORDER BY S_ID' % (START_S_ID)
  cursor.execute(query)
  all_processed = cursor.fetchall()

hgnc_http = HttpWrapper('http://rest.genenames.org')

def get_max_score_doc(result_docs):
  return max(result_docs, key = lambda doc: doc['score'])

# Search using P_NAME from processed rows.
for processed in all_processed:
  # Workaround: Except for % character
  if '%' in processed['P_NAME']:
    continue
  
  print('S_ID:', processed['S_ID'], 'P_NAME:', processed['P_NAME'])
  
  original = None
  with db.cursor(pymysql.cursors.DictCursor) as cursor:
    cursor.execute('SELECT * FROM LUNG_GENES where S_ID = %s', (processed['S_ID'],))
    original = cursor.fetchone()

  # Hgnc response
  response = hgnc_http.request(
    '/search/' + quote(processed['P_NAME']), 'GET', '', ''
  )['response']

  print('Response received')

  # Ignore empty docs, not equal to response's max score.
  if not response['docs'] or \
    not math.isclose(original['MAX_SCORE'], response['maxScore'], abs_tol=0.01):
    continue
  
  max_doc = get_max_score_doc(response['docs'])
  
  print('SYMBOL:', max_doc['symbol'])
  gene_family_info = None
  with db.cursor(pymysql.cursors.DictCursor) as cursor:
    cursor.execute('SELECT * FROM GENES_FAMILY where APPROVED_SYMBOL=%s', (max_doc['symbol'],))
    gene_family_info = cursor.fetchone()

  if not gene_family_info:
    continue

  print('P_NAME:', processed['P_NAME'], 'FAMILY_NAME:', gene_family_info['GENE_FAMILY_INFO'])
  # Get a name similarity score between MeSH query and HGNC family name.
  name_score = difflib.SequenceMatcher(None, processed['P_NAME'].lower(), gene_family_info['GENE_FAMILY_NAME'].lower()).ratio()

  print('UPDATE LUNG_GENES SET MESH_NAME="%s", HGNC_FAMILY_NAME="%s", NAME_SCORE=%s WHERE S_ID=%s' % (
    processed['P_NAME'], gene_family_info['GENE_FAMILY_NAME'], name_score, processed['S_ID']))

  # Send a query to update LUNG_GENES.
  with db.cursor(pymysql.cursors.DictCursor) as cursor:
    cursor.execute(
      'UPDATE LUNG_GENES SET MESH_NAME="%s", HGNC_FAMILY_NAME="%s", NAME_SCORE=%s WHERE S_ID=%s',
      (processed['P_NAME'], gene_family_info['GENE_FAMILY_NAME'], name_score, processed['S_ID'])
    )
  db.commit()

