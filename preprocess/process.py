import tokenize
import re

type_reg = re.compile('Type \w+|type \w+|subtype \w+|sub\-type \w+|Subtype \w+|Sub\-type \w+')
name_reg = re.compile('(?<=\">)[^<]*(?=\<\/nameofsubstance)')

spcae_reg = re.compile('[ ]\w+')
protein_reg = re.compile('\w*[ ]protein')
protein_reg_2 = re.compile('\w*[ ]protein$')
Protein_reg = re.compile('\w*[ ]Protein$')
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
		print temp_sub
	substance_replace.append(temp_sub)

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
	query = "SELECT * FROM LUNG_SUBSTANCE WHERE S_ID > 50 and S_ID < 60"
	curs.execute(query)
	rows = curs.fetchall()
	for row in rows :
		del substance_replace[:] 
		name = row[2].split(", ")
		print row[2]
		protein_detect = protein_reg.findall(name[0])
		protein_detect_2 = protein_reg_2.findall(name[0])
		Protein_detect = Protein_reg.findall(name[0])
		if protein_detect or Protein_detect or protein_detect_2:
			protein_delete(name)
		else:
			if name[0] == 'Receptor' or name[0] == 'Receptors':
				receptor(name)
			elif name[0] == 'Antibodies' or name[0] == 'Antibody' or name[0] == 'Antigen' or name[0] == 'Antigens' :
				anti(name)
			else:
				others(name)
		for elm in substance_replace:
			query = "INSERT INTO LUNG_PROCESSED (S_ID, PM_ID,P_NAME) VALUES (%s, %s,%s)"	
			curs.execute(query,(row[0],row[1],elm))
			conn.commit()
		
		print substance_replace
		print "\n"
	