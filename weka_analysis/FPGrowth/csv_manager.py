
import csv

class CsvManager():

  def __init__(self, csvfile, fieldnames):
    self.writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
    self.writer.writeheader()
  
  def write_row(self, row):
    self.writer.writerow(row)