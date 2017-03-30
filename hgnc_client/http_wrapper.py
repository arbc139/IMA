
import json
import httplib2 as http
# For Python 3
from urllib.parse import urlparse, urlencode

class HttpWrapper():
  
  def __init__(self, uri):
    self.uri = uri
  
  def request(self, path, method, query, body):
    response, content = http.Http().request(
      urlparse(self.uri + path + '?' + urlencode(query)).geturl(), # URL
      method,
      body,
      { 'Accept': 'application/json' } # Header
    )

    if response['status'] != '200':
      raise RuntimeError('Request failed:', response['status'])
      
    return json.loads(content)
    