import tokenize
import re
import sys
import pymysql

max_score = sys.argv[1]
disease_name = sys.argv[2]
filename = disease_name+"_"+max_score+".arff"
f_2 = open(filename,'w')

conn = pymysql.connect(host='localhost', user='root', password='',db='mesh', charset='utf8')
 
curs = conn.cursor()
query = "SELECT  DISTINCT SYMBOL FROM "+disease_name+"_GENES WHERE MAX_SCORE > " + max_score
curs.execute(query)
symbols = curs.fetchall()
query = "SELECT  DISTINCT PM_ID FROM "+disease_name+"_GENES"
curs.execute(query)
pm_ids = curs.fetchall()
relation_name = "@relation "+disease_name+".symbolic\n\n"
f_2.write(relation_name)
for sym in symbols:
	f_2.write('@attribute '+sym[0]+' {0,1}\n')
f_2.write('@data\n')

thesis = []
for pm_id in pm_ids:
	del thesis[:] 
	query = "SELECT  SYMBOL FROM "+disease_name+"_GENES WHERE  IS_FAMILY = 0 AND PM_ID="+str(pm_id[0])+" AND MAX_SCORE > " + max_score 
	curs.execute(query)
	match = curs.fetchall()
	#print match
	for sym in symbols:
		if sym in match:
			#print sym
			#print match
			thesis.append('1')
		else:
			thesis.append('?')
	outstr = ', '.join(thesis)
	#print outstr
	f_2.write(outstr+'\n')
conn.close()	


