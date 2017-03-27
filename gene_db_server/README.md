# Gene DB server

## 서버 구축 방법
- `ps -a` 을 이용하여 **ngrok** 가 실행되어있는지 확인.
  - **ngrok**이 실행되어있지 않다면 `nohup ngrok http 3000 &`
  - `curl localhost:4040/api/tunnels` 을 이용하여 3000 포트와 연결된 domain 주소를 확인
- `npm start`

## 서버 사용 방법
- `${domain 주소}/sql?query=${쿼리}`

## Database 계정 수정 방법
`vim configs/database.js`
