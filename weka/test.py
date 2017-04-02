import tokenize
import re
import sys
import pymysql

 f_2 = open('test.arff','w')

conn = pymysql.connect(host='localhost', user='root', password='',db='mesh', charset='utf8')
 
curs = conn.cursor()
query = "SELECT  DISTINCT SYMBOL FROM LUNG_GENES WHERE MAX_SCORE > 1.5 "
curs.execute(query)
symbols = curs.fetchall()
query = "SELECT  DISTINCT PM_ID FROM LUNG_GENES"
curs.execute(query)
pm_ids = curs.fetchall()
f_2.write('@relation LUNG_CANCER.symbolic'+'\n\n')
for sym in symbols:
	f_2.write('@attribute '+sym+' {0,1}\n')
for pm_id in pm_ids:
	for sym in symbols:
		query = "SELECT  * FROM LUNG_GENES WHERE  PM_ID="+pm_id+" AND SYMBOL = "+sym 
		curs.execute(query)
		match = curs.fetchall()
		print match
conn.close()	

