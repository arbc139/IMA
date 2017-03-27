import tokenize
import re
import sys

name_reg = re.compile('(?<=\">)[^<]*(?=\<\/nameofsubstance)')
pmid_reg = re.compile('(?<=\">)[^<]*(?=\<\/pmid)')
f = open('lung_genetic_mesh.txt')
lines = f.readlines()
for line in lines[:50]:
	name = name_reg.findall(line)
	pmid = pmid_reg.findall(line)
	
	name_list = name[0].split(", ")
	print name


		#'Receptors, Antigen, T-Cell, gamma-delta'

