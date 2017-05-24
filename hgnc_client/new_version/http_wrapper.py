
import json
import httplib2 as http
import time
# For Python 3
from urllib.parse import urlparse, urlencode

class HttpWrapper():
  
  def __init__(self, uri):
    self.uri = uri
  
  def request(self, path, method, query, body):
    while True:
      response, content = http.Http().request(
        urlparse(self.uri + path + '?' + urlencode(query)).geturl(), # URL
        method,
        body,
        { 'Accept': 'application/json' } # Header
      )

      if response['status'] != '200':
        print('Request failed:', response['status'])
        # TODO(totoro): Find workaround better than this...
        time.sleep(5)
        print('After 5 seconds, try agian')
        continue
      else:
        return json.loads(content)
    