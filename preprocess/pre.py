import tokenize

import sys
f = open('lung_genetic_mesh.txt')
lines = f.readlines()
sys.stdout.writelines(lines[:20])