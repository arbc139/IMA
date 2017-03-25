import tokenize
import re
import sys

name_reg = re.compile('(?<=\">)[^<]*(?=\<\/nameofsubstance)')
pmid_reg = re.compile('(?<=\">)[^<]*(?=\<\/pmid)')
f = open('lung_genetic_mesh.txt')
lines = f.readlines()
for line in lines[:5]:
	print line
	name = name_reg.findall(line)
	pmid = pmid_reg.findall(line)
	print name
	print pmid
#sys.stdout.writelines(lines[:20])