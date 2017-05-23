
class WekaResult():

  def __init__(self, weka_result):
    self.first_genes = weka_result['first_genes']
    self.second_genes = weka_result['second_genes']
    self.first_count = weka_result['first_count']
    self.second_count = weka_result['second_count']
    self.conf = weka_result['conf']
    self.lift = weka_result['lift']
    self.lev = weka_result['lev']
    self.conv = weka_result['conv']
    self.unknown = weka_result['unknown']
  
  def __repr__(self):
    return str({
      'first_genes': self.first_genes,
      'second_genes': self.second_genes,
      'first_count': self.first_count,
      'second_count': self.second_count,
      'conf': self.conf,
      'lift': self.lift,
      'lev': self.lev,
      'conv': self.conv,
      'unknown': self.unknown,
    })
