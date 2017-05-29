1. weka를 돌리기 위해서는 arff파일을 만들어야 한다.
	-->weka_run.py를 이용한다.
	[weka_run.py]
		파라미터 : score, 질병이름
		예시 : python weka_run.py 3 LUNG
		결과 : weka/data/LUNG_3.arff 라는 파일이 만들어진다.

2. 이렇게 만들어진 arff파일을 이용해 weka 수행하기
	(1)경로설정[한 번만 하면 되고, 안될 때 한 번 더 하면 된다.]
		export CLASSPATH="/home/hogking/team_1/Capstone-2017-1/weka/weka-3-8-1/"
	(2)수행
		[1] weka/weka-3-8-1/폴더로 이동
		[2] java -cp ./weka.jar weka.associations.FPGrowth -t ../data/PROSTATE_5.arff -N 1000000 -T 0 -C 0.01 -D 0.05 -U 1.0 -M 0.00001 -S >> ../result/PROSTATE_5_large.txt
		위와 같이 하면된다.
		-C는 min confidence, -M은 min support