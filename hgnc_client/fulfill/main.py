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
  parser.add_option('-f', '--fulfillFile', dest='fulfill_file')
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

def find_processed(pid, all_processeds):
  for processed in all_processeds:
    if processed['P_ID'] == pid:
      return processed

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

# Query and result information map.
# Key: Query
# Value: {
#   hgnc_id,
#   symbol,
#   max_score,
#   search_query,
#   is_family,
# }
query_result_map = dict()
pids = []
with open(options.fulfill_file, 'r') as pid_file:
  while True:
    line = pid_file.readline()
    if not line:
      break
    pids.append(int(line))

for pid in pids:
  processed = find_processed(pid, all_processeds)
  if not processed:
    continue
  sid = processed['S_ID']
  substance = find_substance(sid, all_substances)
  if not substance:
    continue

  pmid = substance['PM_ID']
  mesh = substance['S_NAME']
  is_family = check_is_family(mesh)
  if is_family is None:
    continue
  
  # Search to hgnc.
  search_query = processed['P_NAME']
  
  # Query result is cached.
  if search_query in query_result_map:
    result = query_result_map[search_query]
    if result['hgnc_id'] is None:
      continue
    gene = None
    with db.cursor(pymysql.cursors.DictCursor) as cursor:
      query = 'SELECT * FROM %s where S_ID=%d' % (options.gene_table, sid)
      cursor.execute(query)
      gene = cursor.fetchone()
    if gene and gene['MAX_SCORE'] > result['max_score']:
      continue
    save_gene(
      sid, pmid, result['hgnc_id'], result['symbol'], result['max_score'], result['search_query'],
      mesh, result['is_family'])
    continue
  
  is_family = check_is_family(mesh)
  if is_family is None:
    continue

  # Except for % character.
  if '%' in search_query:
    continue

  # Tuning, Add "" to both side on query.
  original_search_query = search_query
  search_query = '"%s"' % search_query
  print('search_query:', search_query)
  
  # Hgnc response
  elapsed_millis = get_current_millis()
  while True:
    try:
      response = hgnc_http.request(
        '/search/' + quote(search_query), 'GET', '', ''
      )['response']
    except:
      print('HGNC request failed, so retry after 5 seconds')
      time.sleep(5)
      continue
    else:
      print('HGNC request time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
      break
  
  # Ignore empty docs, score less than current saved gene.
  if not response['docs']:
    # Cache gene result information.
    query_result_map[original_search_query] = {
      'hgnc_id': None,
      'symbol': None,
      'max_score': None,
      'search_query': None,
      'is_family': None,
    }
    continue
  
  max_score = response['maxScore']
  max_doc = get_max_score_doc(response['docs'])

  # Cache gene result information.
  query_result_map[original_search_query] = {
    'hgnc_id': max_doc['hgnc_id'],
    'symbol': max_doc['symbol'],
    'max_score': max_doc['score'],
    'search_query': search_query,
    'is_family': is_family,
  }

  gene = None
  with db.cursor(pymysql.cursors.DictCursor) as cursor:
    query = 'SELECT * FROM %s where S_ID=%d' % (options.gene_table, sid)
    cursor.execute(query)
    gene = cursor.fetchone()

  if gene and gene['MAX_SCORE'] > response['maxScore']:
    continue
  
  # Save gene result information to DB.
  save_gene(
    sid, pmid, max_doc['hgnc_id'], max_doc['symbol'], max_doc['score'], search_query, mesh,
    is_family)

print('Done.')