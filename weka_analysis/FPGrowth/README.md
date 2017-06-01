Process weka results to csv file.

nohup python main.py -i input/BREAST_3_c001_m00001.txt -o output/s3_conf_001_sup_00001_BC_edge.csv > breast_log.out &
nohup python main.py -i input/COLO_3_c001_m00001.txt -o output/s3_conf_001_sup_00001_CC_edge.csv > colo_log.out &
nohup python main.py -i input/STOMACH_3_c001_m00001.txt -o output/s3_conf_001_sup_00001_SC_edge.csv > stomach_log.out &
