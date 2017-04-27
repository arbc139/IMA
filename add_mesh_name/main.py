#!/usr/bin/python

from http_wrapper import HttpWrapper
from urllib.parse import quote
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
  query = 'SELECT * FROM LUNG_PROCESSED ORDER BY S_ID' if START_S_ID is None else
    'SELECT * FROM LUNG_PROCESSED WHERE S_ID > %s ORDER BY S_ID' % (START_S_ID)
  cursor.execute(query)
  all_processed = cursor.fetchall()
print(all_processed)

# Search using P_NAME from processed rows.
"""
hgnc_http = HttpWrapper('http://rest.genenames.org')

for processed in all_processed:
  # Workaround: Except for % character
  if '%' in processed['P_NAME']:
    continue
  
  original = None
  with db.cursor(pymysql.cursors.DictCursor) as cursor:
    cursor.execute('SELECT * FROM LUNG_GENES where S_ID = %d', (processed['S_ID'],))
    original = cursor.fetchone()

  # Hgnc response
  response = hgnc_http.request(
    '/search/' + quote(processed['P_NAME']), 'GET', '', ''
  )['response']

  # Ignore empty docs, not equal to response's max score.
  if not response['docs'] or \
    not math.isclose(original['MAX_SCORE'], response['maxScore'], abs_tol=0.0000001):
    continue
  
  with db.cursor(pymysql.cursors.DictCursor) as cursor:
    cursor.execute('UPDATE LUNG_GENES SET MESH_NAME=%s', (processed['P_NAME'],))
  db.commit()
"""