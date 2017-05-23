
class WekaManager():

  def __init__(self, weka_objects):
    self.weka_objects = weka_objects
  
  # Remove weka object that have lift value less than 1.
  def filter_objects(self):
    self.weka_objects = list(filter(lambda weka: weka.lift > 1, self.weka_objects))

  # (x - min(x)) / (max(x) - min(x))
  def normalize(self):
    conf_values = [weka.conf for weka in self.weka_objects]
    lift_values = [weka.lift for weka in self.weka_objects]
    lev_values = [weka.lift for weka in self.weka_objects]
    conv_values = [weka.conv for weka in self.weka_objects]
    unknown_values = [weka.unknown for weka in self.weka_objects]

    conf_min = min(conf_values)
    conf_max = max(conf_values)
    lift_min = min(lift_values)
    lift_max = max(lift_values)
    lev_min = min(lev_values)
    lev_max = max(lev_values)
    conv_min = min(conv_values)
    conv_max = max(conv_values)
    unknown_min = min(unknown_values)
    unknown_max = max(unknown_values)
    
    for weka in self.weka_objects:
      # Normalize conf
      weka.conf = (weka.conf - conf_min) / (conf_max - conf_min) if conf_max != conf_min else 1
      # Normalize lift
      weka.lift = (weka.lift - lift_min) / (lift_max - lift_min) if lift_max != lift_min else 1
      # Normalize lev
      weka.lev = (weka.lev - lev_min) / (lev_max - lev_min) if lev_max != lev_min else 1
      # Normalize conv
      weka.conv = (weka.conv - conv_min) / (conv_max - conv_min) if conv_max != conv_min else 1
      # Normalize unknown
      weka.unknown = (weka.unknown - unknown_min) / (unknown_max - unknown_min) if unknown_max != unknown_min else 1
    
  def analyze(self):
    results = dict()

    for weka in self.weka_objects:
      score = weka.lift / (len(weka.first_genes) * len(weka.second_genes))
      for first_gene in weka.first_genes:
        for second_gene in weka.second_genes:
          relationship = (first_gene, second_gene)
          reverse_relationship = (second_gene, first_gene)
          if relationship in results:
            results[relationship] += score
          elif reverse_relationship in results:
            results[reverse_relationship] += score
          else:
            results[relationship] = score

    return results
        
        
