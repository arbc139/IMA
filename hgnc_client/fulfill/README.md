# HGNC Search Client
HGNC Api 서버로 요청을 보내는 클라이언트

## Python version
`Python 3`

## Init repository
- **pip** 설치 후 `./Makefile`
- 만약 **pip** 이 설치가 안되어있다면 다음 링크를 참조
https://pip.pypa.io/en/stable/installing/

## Client 실행
`python main.py`

## Commands
LUNG fulfill 실행하기
`python main.py -s LUNG_SUBSTANCE -p LUNG_PROCESSED -g LUNG_GENES -f ../../preprocess/LUNG_add_pid_list.txt`
`nohup python main.py -s PROSTATE_SUBSTANCE -p PROSTATE_PROCESSED -g PROSTATE_GENES -f ../../preprocess/PROSTATE_add_pid_list.txt > prostate_log.out &`