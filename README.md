# Introduce
2017-1 소프트웨어 종합설계 Repository \
김도영, 방창배, 황현서

# Subject
생물학 논문에서의 MeSH term과 Association rule을 이용하여 질병과 관련된 gene들을 찾아냄. \
IMA: Identifying disease-related genes using MeSH term and Association Rule

# Structure

## preprocess
MeSH term을 HGNC API가 잘 읽을 수 있는 형태로 바꾸는 작업.

## gene_db_server
구축한 Gene DB에 접근할 수 있는 server.

## hgnc_client
HGNC API에 preprocess된 query를 보내는 client.

## DB Cleaning
이전에 잘못 구현한 방식을 hotfix 형태로 수정하는 작업들.

### mesh_family_processing
MeSH term 중에 Family를 나타내는 MeSH term을 알아내기 위한 작업

### make_mesh_db
MeSH DB를 구축하기 위한 스크립트

## weka
MeSH Term으로부터 알아낸 Gene을 대상으로 Association rule을 수행하는 스크립트

## weka_analysis
Weka에서 나온 Association rule 결과를 gene relation으로 바꾸는 스크립트
