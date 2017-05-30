
from weka_result import WekaResult
import re
import tokenize

class WekaParser():

  def __init__(self, weka_file):
    self.weka_file = weka_file
  
  def parse(self):
    results = []

    # Ignore first part of weka file.
    while True:
      line = self.weka_file.readline()
      if 'FPGrowth found ' in line or not line: break

    while True:
      line = self.weka_file.readline()

      # Ignore last part of weka file.
      if '=== Evaluation ===' in line or not line: break
      
      parsed_line = self.parse_line(list(filter(lambda x: x and not re.match('[0-9]+\.', x), line.split(' '))))
      if not parsed_line: continue
      results.append(parsed_line)
    
    return results

  def parse_line(self, line_tokens):
    weka_result = dict()
    is_first_genes = True
    weka_result['first_genes'] = []
    weka_result['second_genes'] = []

    # print(line_tokens)

    if len(line_tokens) <= 1:
      return None

    for token in line_tokens:
      # Skip '\n' case.
      if token == '\n':
        continue

      # Toggle gene type:
      if token == '==>':
        is_first_genes = False
        continue

      # Gene type
      if re.search('=1', token):
        # print('gene:', token)
        if is_first_genes:
          weka_result['first_genes'].append(re.sub('[=1\[\]\:\,]', '', token))
        else:
          weka_result['second_genes'].append(re.sub('[=1\[\]\:\,]', '', token))
        continue
      
      # Gene counts
      if re.match('[0-9]+', token):
        # print('gene count:', token)
        if is_first_genes:
          weka_result['first_count'] = int(token)
        else:
          weka_result['second_count'] = int(token)
        continue
      
      # 'conf' type
      if re.match('\<conf\:\(\-?([0-9]+|[0-9]+\.[0-9]{1,2})\)\>', token):
        # print('conf:', token)
        weka_result['conf'] = float(re.sub('\)\>', '', re.sub('\<conf\:\(', '', token)))
        continue
      
      # 'lift' type
      if re.match('lift\:\(\-?([0-9]+|[0-9]+\.[0-9]{1,2})\)', token):
        # print('lift:', token)
        weka_result['lift'] = float(re.sub('\)', '', re.sub('lift\:\(', '', token)))
        continue

      # 'lev' type
      if re.match('lev\:\(\-?([0-9]+|[0-9]+\.[0-9]{1,2})\)', token):
        # print('lev:', token)
        weka_result['lev'] = float(re.sub('\)', '', re.sub('lev\:\(', '', token)))
        continue
      
      # 'conv' type
      if re.match('conv\:\(\-?([0-9]+|[0-9]+\.[0-9]{1,2})\)', token):
        # print('conv:', token)
        weka_result['conv'] = float(re.sub('\)', '', re.sub('conv\:\(', '', token)))
        continue

    weka_result['unknown'] = 0

    print(weka_result)
      
    return WekaResult(weka_result)