#!/usr/bin/python

from http_wrapper import HttpWrapper

hgnc_search_uri = 'http://rest.genenames.org'
db_uri = 'http://e3cb0988.ngrok.io'

# Get all preprocessed MeSH terms in DB.
db_http = HttpWrapper(db_uri)
all_processed = db_http.request(
  '/sql',
  'GET',
  { 'query': 'SELECT * FROM LUNG_PROCESSED ORDER BY S_ID' },
  '',
)

# Search using P_NAME from processed rows.

# S_ID and HGNC Map.
# Key: S_ID
# Value: HGNC doc max score
sid_hgnc_map = dict()

hgnc_http = HttpWrapper(hgnc_search_uri)

def get_max_score_doc(result_docs):
  return max(result_docs, key = lambda doc: doc['score'])

for processed in all_processed:
  if not test:
    break
  # Hgnc response
  response = hgnc_http.request(
    '/search/' + processed['P_NAME'], 'GET', '', ''
  )['response']

  # Ignore empty docs, score less than max score.
  if not response['docs'] or \
    (processed['S_ID'] in sid_hgnc_map.keys() and \
    sid_hgnc_map[processed['S_ID']] >= response['maxScore']):
    continue

  print('docs:', response['docs'])
  sid_hgnc_map[processed['S_ID']] = response['maxScore']
  max_doc = get_max_score_doc(response['docs'])
  print('INSERT INTO LUNG_GENES (S_ID, PM_ID, HGNC_ID, SYMBOL, MAX_SCORE) VALUES (%s, %s, "%s", "%s", %s) ON DUPLICATE KEY UPDATE HGNC_ID="%s", SYMBOL="%s", MAX_SCORE=%s' % (
        processed['S_ID'], processed['PM_ID'], max_doc['hgnc_id'], max_doc['symbol'], max_doc['score'], max_doc['hgnc_id'], max_doc['symbol'], max_doc['score']))
  db_http.request(
    '/sql',
    'GET',
    {
      'query': 'INSERT INTO LUNG_GENES (S_ID, PM_ID, HGNC_ID, SYMBOL, MAX_SCORE) VALUES (%s, %s, "%s", "%s", %s) ON DUPLICATE KEY UPDATE HGNC_ID="%s", SYMBOL="%s", MAX_SCORE=%s' % (
        processed['S_ID'], processed['PM_ID'], max_doc['hgnc_id'], max_doc['symbol'], max_doc['score'], max_doc['hgnc_id'], max_doc['symbol'], max_doc['score']),
    },
    '',
  )
