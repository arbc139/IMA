#!/usr/bin/python

from http_wrapper import HttpWrapper
from urllib.parse import quote
import pymysql
import re
import sys
import time

db = pymysql.connect(host='localhost', user='root', password='', db='mesh', charset='utf8')

get_current_millis = lambda: int(round(time.time() * 1000))
def get_elapsed_seconds(current_time, elapsed_millis):
  return (current_time - elapsed_millis) / 1000.0

def parse_commands(argv):
  from optparse import OptionParser
  parser = OptionParser('"')
  parser.add_option('-s', '--substanceTable', dest='substance_table', help='Database substance table name')
  parser.add_option('-p', '--processedTable', dest='processed_table', help='Database processed table name')
  parser.add_option('-g', '--geneTable', dest='gene_table', help='Database gene table name')
  parser.add_option('--startSId', dest='start_s_id')
  
  options, otherjunk = parser.parse_args(argv)
  return options

options = parse_commands(sys.argv[1:])

hgnc_search_uri = 'http://rest.genenames.org'

# Get all substance MeSH terms in DB.
elapsed_millis = get_current_millis()
all_substances = None
with db.cursor(pymysql.cursors.DictCursor) as cursor:
  query = 'SELECT * FROM %s ORDER BY S_ID' % (options.substance_table)
  cursor.execute(query)
  all_substances = cursor.fetchall()
print('Find all substance mesh terms time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))

def find_substance(sid, all_substances):
  return next(substance for substance in all_substances if substance['S_ID'] == sid)

# Get all preprocessed MeSH terms in DB.
elapsed_millis = get_current_millis()
all_processeds = None
with db.cursor(pymysql.cursors.DictCursor) as cursor:
  query = 'SELECT * FROM %s ORDER BY S_ID' % (options.processed_table)
  if options.start_s_id:
    query = 'SELECT * FROM %s WHERE S_ID > %s ORDER BY S_ID' % (options.processed_table, options.start_s_id)
  cursor.execute(query)
  all_processeds = cursor.fetchall()
print('Find all processd mesh terms time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))

def find_processeds(sid, all_processeds):
  return [processed for processed in all_processeds if processed['S_ID'] == sid]

elapsed_millis = get_current_millis()
all_qualifiers = None
with db.cursor(pymysql.cursors.DictCursor) as cursor:
  cursor.execute('SELECT * FROM MESH_QUALIFIER')
  all_qualifiers = cursor.fetchall()
all_descriptors = None
with db.cursor(pymysql.cursors.DictCursor) as cursor:
  cursor.execute('SELECT * FROM MESH_DESCRIPTOR')
  all_descriptors = cursor.fetchall()
all_supplementals = None
with db.cursor(pymysql.cursors.DictCursor) as cursor:
  cursor.execute('SELECT * FROM MESH_SUPPLEMENTAL')
  all_supplementals = cursor.fetchall()
print('Find all mesh terms time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))

hgnc_http = HttpWrapper(hgnc_search_uri)

def get_max_score_doc(result_docs):
  return max(result_docs, key = lambda doc: doc['score'])

def check_is_family(mesh_term):
  qualifiers = list(filter(lambda qualifier: qualifier['NAME'] == mesh_term, all_qualifiers))
  descriptors = list(filter(lambda descriptor: descriptor['NAME'] == mesh_term, all_descriptors))
  supplementals = list(filter(lambda supplemental: supplemental['NAME'] == mesh_term, all_supplementals))
  
  tree_numbers = None
  if len(qualifiers) == 1:
    tree_numbers = eval(qualifiers[0]['TREE_NUMBERS'])
  elif len(descriptors) == 1:
    tree_numbers = eval(descriptors[0]['TREE_NUMBERS'])
  elif len(supplementals) == 1:
    return False
  else:
    print('There is no mesh term for qualifier and descriptor')
    return None
  
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
      return True
  return False

def save_gene(sid, pmid, hgncid, symbol, max_score, search_query, mesh_term, is_family):
  query = 'INSERT INTO %s ' % (options.gene_table) \
    + '(S_ID, PM_ID, HGNC_ID, SYMBOL, MAX_SCORE, SEARCH_QUERY, MESH_TERM, IS_FAMILY) ' \
    + 'VALUES ' \
    + '(%s, %s, "%s", "%s", %s, "%s", "%s", %d) ' % (
      sid, pmid, hgncid, symbol, max_score, re.escape(search_query), mesh_term, 1 if is_family else 0) \
    + 'ON DUPLICATE KEY UPDATE ' \
    + 'HGNC_ID="%s", SYMBOL="%s", MAX_SCORE=%s, SEARCH_QUERY="%s", MESH_TERM="%s", IS_FAMILY=%d' % (
      hgncid, symbol, max_score, re.escape(search_query), mesh_term, 1 if is_family else 0)
  print(query)

  elapsed_millis = get_current_millis()
  with db.cursor(pymysql.cursors.DictCursor) as cursor:
    cursor.execute(query)
  db.commit()
  print('GENE DB insert time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))


# MeSH Term and result information map.
# Key: MeSH Term
# Value: {
#   hgnc_id,
#   symbol,
#   max_score,
#   search_query,
#   is_family,
# }
mesh_result_map = dict()
sids = list(set([processed['S_ID'] for processed in all_processeds]))

for sid in sids:
  substance = find_substance(sid, all_substances)
  processeds = find_processeds(sid, all_processeds)

  pmid = substance['PM_ID']

  if not substance or not processeds:
    continue
  
  # 1. Case, MeSH result is cached.
  mesh = substance['S_NAME']
  if mesh in mesh_result_map:
    result = mesh_result_map[mesh]
    save_gene(
      sid, pmid, result['hgnc_id'], result['symbol'], result['max_score'], result['search_query'],
      mesh, result['is_family'])
    continue
  
  is_family = check_is_family(mesh)
  if is_family is None:
    continue

  # 2. Search to hgnc.
  max_score = 0
  max_doc = None
  max_search_query = None
  for processed in processeds:
    search_query = processed['P_NAME']

    # Except for % character.
    if '%' in search_query:
      continue

    # Tuning, Add "" to both side on query.
    search_query = '"%s"' % search_query
    print('search_query:', search_query)
    
    # Hgnc response
    elapsed_millis = get_current_millis()
    response = hgnc_http.request(
      '/search/' + quote(search_query), 'GET', '', ''
    )['response']
    print('HGNC request time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))

    # Ignore empty docs, score less than max score.
    if not response['docs'] or max_score >= response['maxScore']:
      continue
    
    max_score = response['maxScore']
    max_doc = get_max_score_doc(response['docs'])
    max_search_query = search_query
  
  if max_doc is None or max_search_query is None:
    continue
  
  # Save gene result information to DB.
  save_gene(
    sid, pmid, max_doc['hgnc_id'], max_doc['symbol'], max_doc['score'], max_search_query, mesh,
    is_family)
  
  # Cache gene result information.
  mesh_result_map[mesh] = {
    'hgnc_id': max_doc['hgnc_id'],
    'symbol': max_doc['symbol'],
    'max_score': max_doc['score'],
    'search_query': max_search_query,
    'is_family': is_family,
  }

print('Done.')