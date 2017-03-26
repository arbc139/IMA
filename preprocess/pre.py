import tokenize
import re
import sys
import pymysql
 
conn = pymysql.connect(host='localhost', user='root', password='',db='thwhd2017', charset='utf8')
 
curs = conn.cursor()
pmid = 1234
name = "abc"
query = "INSERT INTO LUNG_SUBSTANCE (PM_ID, S_NAME) VALUES ('"+pmid+"', '"+name+"');"
curs.execute(sql)
name_reg = re.compile('(?<=\">)[^<]*(?=\<\/nameofsubstance)')
pmid_reg = re.compile('(?<=\">)[^<]*(?=\<\/pmid)')
f = open('lung_genetic_mesh.txt')
lines = f.readlines()
for line in lines:
	name = name_reg.findall(line)
	pmid = pmid_reg.findall(line)
	#query = "INSERT INTO LUNG_SUBSTANCE (PM_ID, S_NAME) VALUES ('"+pmid+"', '"+name+"');"
	"""name_list = name[0].split(", ")
	if(name_list[0] == "Antibodies" or name_list[0]=="Antigens"):
		print name
	if(name_list[0] != "Antibodies" and name_list[0]!="Antigens"):
		if len(name_list) == 3:
			print name"""

		
#sys.stdout.writelines(lines[:20])