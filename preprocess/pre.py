import tokenize
import re
import sys

p = re.compile('(?<=\">)[^<]*(?=\<\/nameofsubstance)')
f = open('lung_genetic_mesh.txt')
lines = f.readlines()
for line in lines[:5]:
	print line
	m = p.findall(line)
	print m
#sys.stdout.writelines(lines[:20])