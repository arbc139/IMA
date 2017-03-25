import tokenize
import re
import sys

p = re.compile('>*<')
f = open('lung_genetic_mesh.txt')
lines = f.readlines()
for line in lines[:5]:
	m = p.match(line)
	print m
#sys.stdout.writelines(lines[:20])