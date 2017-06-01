import tokenize
import re
import pymysql
import sys
disease = sys.argv[1]

conn = pymysql.connect(host='localhost', user='root', password='',db='mesh', charset='utf8') 
curs = conn.cursor()
type_reg = re.compile('Type \w+|type \w+|subtype \w+|sub\-type \w+|Subtype \w+|Sub\-type \w+')
name_reg = re.compile('(?<=\">)[^<]*(?=\<\/nameofsubstance)')

spcae_reg = re.compile('[ ]\w+')
protein_reg = re.compile('\w*[ ]protein')
protein_reg_2 = re.compile('\w*[ ]protein$')
Protein_reg = re.compile('\w*[ ]Protein$')
longnon_reg_1 = re.compile('\w*long[ ]non-coding[ ]RNA\w*')
longnon_2 = re.compile('\w*long[ ]noncoding[ ]RNA\w*')
longnon_3 = re.compile('\w*long[ ]non coding[ ]RNA\w*')
longnon_4 = re.compile('\w*non[ ]coding[ ]RNA\w*')
longnon_5 = re.compile('\w*noncoding[ ]RNA\w*')
longnon_6 = re.compile('\w*non-coding[ ]RNA\w*')

test_cases = [['1','Antibodies, Monoclonal, Humanized'],['2','Chorionic Gonadotropin, beta Subunit, Human'],['3','Receptors, Pituitary Adenylate Cyclase-Activating Polypeptide, Type III'],['4','Receptors, Tumor Necrosis Factor, Member 10c'],['5','ATP Binding Cassette Transporter, Sub-Family G, Member 2'],['6','ABC protein, Human'],['7','Biomarkers, Tumor'],['8','Receptor, Epidermal Growth Factor'],['9', 'MicroRNA']]
substance_replace = []



def receptor(name):
	global substance_replace
	for elm in name:
		type_detect = type_reg.findall(elm)
	if type_detect :
		type_num = spcae_reg.findall(type_detect[0])
		if type_num[0] == ' I' or type_num[0] == ' 1':	
			type_num_replace = '1'
		elif type_num[0] == ' II' or type_num[0] == ' 2':	
			type_num_replace = '2'
		elif type_num[0] == ' III' or type_num[0] == '3':	
			type_num_replace = '3'
		elif type_num[0] == ' IV' or type_num[0] == '4':	
			type_num_replace = '4'
		elif type_num[0] == ' V' or type_num[0] == '5':	
			type_num_replace = '4'
		else:	
			type_num_replace = type_num[0]
		temp_sub = ' '.join(name[:len(name)-1]) + ' ' +type_num_replace	
		
	else:
		temp_sub = ' '.join(name) 
	substance_replace.append(temp_sub)
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

def anti(name):
	temp_sub = ' '.join(name)	
	substance_replace.append(temp_sub)

def protein_delete(name):
	gene_area = name[0].split(" ")
	substance_replace.append(gene_area[0])

def others(name):
	for elm in name:
		substance_replace.append(elm)
	if len(name) > 1:
		temp_name =  ' '.join(name)	
		substance_replace.append(temp_name)
	

	

if __name__ == '__main__':
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
		

		if protein_detect or Protein_detect or protein_detect_2:
			protein_delete(name)
		elif micro_detect:
			micro_delete(name)
		elif longnon_detect or longnon_detect_2 or longnon_detect_3  or longnon_detect_4 or longnon_detect_5 or longnon_detect_6:
			long_delete(name)
		else:
			if name[0] == 'Receptor' or name[0] == 'Receptors':
				receptor(name)
			elif name[0] == 'Antibodies' or name[0] == 'Antibody' or name[0] == 'Antigen' or name[0] == 'Antigens' :
				anti(name)
			else:
				others(name)
		for elm in substance_replace:
			query = "INSERT INTO "+disease+"_PROCESSED (S_ID, PM_ID,P_NAME) VALUES (%s, %s,%s)"	
			curs.execute(query,(row[0],row[1],elm))
			conn.commit()
