#!/usr/bin/python

import httplib2 as http
import json

try:
  # For Python 2
  from urlparse import urlparse
except ImportError:
  # For Python 3
  from urllib.parse import urlparse

uri = 'http://rest.genenames.org'

# TODO(totoro): Need to implement search request using gene name.
path = '/fetch/hgnc_id/1097'

httpObject = http.Http()

response, content = httpObject.request(
  urlparse(uri + path).geturl(), # URL
  'GET', # Method
  '', # Body
  { 'Accept': 'application/json' } # Header
)

if response['status'] == '200':
  # Assume that content is a json reply
  # parse content with the json module 
  data = json.loads(content)
  print('Json response:', data)
else:
  print('Error detected:', response['status'])