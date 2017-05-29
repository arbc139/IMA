import tokenize
import re
import pymysql
import sys

disease = sys.argv[1]

conn = pymysql.connect(host='localhost', user='root', password='',db='mesh', charset='utf8') 
curs = conn.cursor()
type_reg = re.compile('Type \w+|type \w+|subtype \w+|sub\-type \w+|Subtype \w+|Sub\-type \w+')
name_reg = re.compile('(?<=\">)[^<]*(?=\<\/nameofsubstance)')

longnon_reg_1 = re.compile('\w*long[ ]non-coding[ ]RNA\w*')
longnon_2 = re.compile('\w*long[ ]noncoding[ ]RNA\w*')
longnon_3 = re.compile('\w*long[ ]non coding[ ]RNA\w*')
longnon_4 = re.compile('\w*non[ ]coding[ ]RNA\w*')
longnon_5 = re.compile('\w*noncoding[ ]RNA\w*')
longnon_6 = re.compile('\w*non-coding[ ]RNA\w*')


spcae_reg = re.compile('[ ]\w+')
protein_reg = re.compile('\w*[ ]protein')
protein_reg_2 = re.compile('\w*[ ]protein$')
Protein_reg = re.compile('\w*[ ]Protein$')
micro_reg = re.compile('\w*[ ]microRNA\w*')



substance_replace = []

def micro_delete(name):
	gene_area = name[0].split(" ")
	substance_replace.append(gene_area[0])
def long_delete(name):
	gene_area = name[0].split(" ")
	gene = re.sub('long[ ]non-coding[ ]RNA', '', gene_area[0])
	gene = re.sub('long[ ]noncoding[ ]RNA', '', gene)
	gene = re.sub('long[ ]non[ ]coding[ ]RNA', '', gene)
	gene = re.sub('non[ ]coding[ ]RNA', '', gene)
	gene = re.sub('noncoding[ ]RNA', '', gene)
	gene = re.sub('non-coding[ ]RNA', '', gene)
	substance_replace.append(gene)
	

if __name__ == '__main__':
	filename = disease+"_add_pid_list"+".txt"
	f_2 = open(filename,'w')
	query = "SELECT * FROM "+disease+"_SUBSTANCE"
	curs.execute(query)
	rows = curs.fetchall()
	for row in rows :
		del substance_replace[:] 
		name = row[2].split(", ")
		protein_detect = protein_reg.findall(name[0])
		protein_detect_2 = protein_reg_2.findall(name[0])
		Protein_detect = Protein_reg.findall(name[0])
		micro_detect= micro_reg.findall(name[0])
		longnon_detect = longnon_reg_1.findall(name[0])
		longnon_detect_2 = longnon_2.findall(name[0])
		longnon_detect_3 = longnon_3.findall(name[0])
		longnon_detect_4 = longnon_4.findall(name[0])
		longnon_detect_5 = longnon_5.findall(name[0])
		longnon_detect_6 = longnon_6.findall(name[0])
		if micro_detect:
			micro_delete(name)
		elif longnon_detect or longnon_detect_2 or longnon_detect_3  or longnon_detect_4 or longnon_detect_5 or longnon_detect_6:
			long_delete(name)

		for elm in substance_replace:
			query = "INSERT INTO "+disease+"_PROCESSED (S_ID, PM_ID,P_NAME) VALUES (%s, %s,%s)"	
			curs.execute(query,(row[0],row[1],elm))
			conn.commit()
			query = "SELECT P_ID from "+disease+"_PROCESSED order by P_ID desc limit 1"
			curs.execute(query)
			rows = curs.fetchall()
			for row in rows:
				f_2.write(str(row[0])+'\n')
			