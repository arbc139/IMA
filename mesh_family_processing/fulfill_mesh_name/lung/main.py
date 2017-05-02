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
# Get all genes which does not have MESH_NAME.
all_genes = None
with db.cursor(pymysql.cursors.DictCursor) as cursor:
  query = 'SELECT * FROM LUNG_GENES WHERE MESH_NAME IS NULL ORDER BY S_ID' if START_S_ID is None \
    else 'SELECT * FROM LUNG_GENES WHERE S_ID > %s AND MESH_NAME IS NULL ORDER BY S_ID' % (START_S_ID)
  cursor.execute(query)
  all_genes = cursor.fetchall()
print('Find all genes time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))

hgnc_http = HttpWrapper('http://rest.genenames.org')

def get_max_score_doc(result_docs):
  return max(result_docs, key = lambda doc: doc['score'])

# Fulfill gene's MESH_NAME.
for gene in all_genes:
  elapsed_millis = get_current_millis()
  processeds = None
  with db.cursor(pymysql.cursors.DictCursor) as cursor:
    cursor.execute('SELECT * FROM LUNG_PROCESSED where S_ID = %s', (gene['S_ID'],))
    processeds = cursor.fetchall()
  print('Get processed time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
  
  # Get MeSH query
  mesh_name = None
  max_doc = None
  if len(processeds) == 1:
    mesh_name = processeds[0]['P_NAME']
  else:
    for processed in processeds:
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
      if not response['docs']:
        continue
      if not max_doc or max_doc['score'] < response['maxScore']:
        print('Found max doc')
        max_doc = get_max_score_doc(response['docs'])
        mesh_name = processed['P_NAME']
  
  if max_doc:
    print('It has max doc')
    # Get gene family info
    elapsed_millis = get_current_millis()
    gene_family_info = None
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
      cursor.execute('SELECT * FROM GENES_FAMILY where APPROVED_SYMBOL=%s', (gene['SYMBOL'],))
      gene_family_info = cursor.fetchone()
    print('Find gene family time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
    
    if not mesh_name and not gene_family_info:
      continue
    
    if not gene_family_info:
      elapsed_millis = get_current_millis()
      # Send a query to update LUNG_GENES.
      with db.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(
          'UPDATE LUNG_GENES SET HGNC_ID="%s", SYMBOL="%s", MAX_SCORE=%s, MESH_NAME="%s" WHERE S_ID=%s',
          (max_doc['hgnc_id'], max_doc['symbol'], max_doc['score'], mesh_name, gene['S_ID'])
        )
      db.commit()
      print('Update gene time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
      continue
    
    # Get a name similarity score between MeSH query and HGNC family name.
    name_score = difflib.SequenceMatcher(None, mesh_name.lower(), gene_family_info['GENE_FAMILY_NAME'].lower()).ratio()

    print('UPDATE LUNG_GENES SET HGNC_ID="%s", SYMBOL="%s", MAX_SCORE=%s, MESH_NAME="%s", HGNC_FAMILY_NAME="%s", NAME_SCORE=%s WHERE S_ID=%s' % (
      max_doc['hgnc_id'], max_doc['symbol'], max_doc['score'], mesh_name, gene_family_info['GENE_FAMILY_NAME'], name_score, gene['S_ID']))

    elapsed_millis = get_current_millis()
    # Send a query to update LUNG_GENES.
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
      cursor.execute(
        'UPDATE LUNG_GENES SET HGNC_ID="%s", SYMBOL="%s", MAX_SCORE=%s, MESH_NAME="%s", HGNC_FAMILY_NAME="%s", NAME_SCORE=%s WHERE S_ID=%s',
        (max_doc['hgnc_id'], max_doc['symbol'], max_doc['score'], mesh_name, gene_family_info['GENE_FAMILY_NAME'], name_score, gene['S_ID'])
      )
    db.commit()
    print('Update gene time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
    continue
  
  # Get gene family info
  elapsed_millis = get_current_millis()
  gene_family_info = None
  with db.cursor(pymysql.cursors.DictCursor) as cursor:
    cursor.execute('SELECT * FROM GENES_FAMILY where APPROVED_SYMBOL=%s', (gene['SYMBOL'],))
    gene_family_info = cursor.fetchone()
  print('Find gene family time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))

  if not mesh_name and not gene_family_info:
    continue

  if not gene_family_info:
    elapsed_millis = get_current_millis()
    # Send a query to update LUNG_GENES.
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
      cursor.execute(
        'UPDATE LUNG_GENES SET MESH_NAME="%s" WHERE S_ID=%s',
        (mesh_name, gene['S_ID'])
      )
    db.commit()
    print('Update gene time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
    continue

  if not mesh_name:
    elapsed_millis = get_current_millis()
    # Send a query to update LUNG_GENES.
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
      cursor.execute(
        'UPDATE LUNG_GENES SET HGNC_FAMILY_NAME="%s" WHERE S_ID=%s',
        (gene_family_info['GENE_FAMILY_NAME'], gene['S_ID'])
      )
    db.commit()
    print('Update gene time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
    continue
  
  # Get a name similarity score between MeSH query and HGNC family name.
  name_score = difflib.SequenceMatcher(None, mesh_name.lower(), gene_family_info['GENE_FAMILY_NAME'].lower()).ratio()

  print('UPDATE LUNG_GENES SET MESH_NAME="%s", HGNC_FAMILY_NAME="%s", NAME_SCORE=%s WHERE S_ID=%s' % (
    mesh_name, gene_family_info['GENE_FAMILY_NAME'], name_score, gene['S_ID']))

  elapsed_millis = get_current_millis()
  # Send a query to update LUNG_GENES.
  with db.cursor(pymysql.cursors.DictCursor) as cursor:
    cursor.execute(
      'UPDATE LUNG_GENES SET MESH_NAME="%s", HGNC_FAMILY_NAME="%s", NAME_SCORE=%s WHERE S_ID=%s',
      (mesh_name, gene_family_info['GENE_FAMILY_NAME'], name_score, gene['S_ID'])
    )
  db.commit()
  print('Update gene time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
