# Hands_MediaPipe_project


## 5/23(목)
> - Postgres 사용하여 test 데이터베이스 생성
> - 임시 구축된 서버에 생성한 test 데이터베이스 연동(create 눌렀을 때 데이터 DB에 들어오는지 확인)

## 5/24(금)
> - test 데이터베이스를 관계형 데이터베이스로 변환(웹 서버 로그를 DB와 연동)
> - 웹 서버 로그를 DB와 연동 시 웹 페이지가 로그가 찍히는 JSON파일과 동일하게 로그 화면으로 바뀌는 문제 발생.
> - 로그가 2개씩 찍히는 문제 발생.

## 5/27(월)
> - @app.after_request에 if response.content_type == 'application/json': 으로 if문 걸어줌으로써 홈페이지 화면이 로그 화면으로 바뀌는 문제 해결.
> - app.run의 debug=True를 제거하니 로그가 2개씩 찍히는 문제 해결.
> - 그러나 로그가 찍힐 때마다 JSON파일로 바로 전달되는 것이 아니라 지연되어 저장되는 문제 발생 -> 네트워크 문제일 가능성이 높다고 판단되어 코드 수정 없이 그대로 유지하기로 함.

## 5/28(화)
> - Google Cloud Postgresql를 로컬 DB와 연결
> - 새로 구축된 웹 서버와 로컬 DB 연동

## 5/29(수)
> - 테이블 정의 다시 함(id 컬럼과 time 컬럼을 primary key로 지정해서 중복된 값을 받아와도 문제 없도록 수정).
> - 행동 로그 추출(label, id, coordinate, time, ...)
> - 새로운 가상 환경 구축(python -> conda)
## 5/30(목)
> - 로그인 구현하기로 결정이 되어서 랜덤 생성 아이디 받아오기(진행중)
> - 랜덤 생성 아이디 받아오는 과정에서 임시로 지정된 아이디 받아오기까지 완료, 랜덤 생성 아이디를 받아오는 작업은 내일 이어 진행 예정
> - DB 테이블 구축 완료(client_id 기준 pk-fk로 테이블 간 연결 구성 완료)
## 5/31(금)
> - 로그인 되어 있는 유저의 정보 가져오려고 노력중.(users.json 파일에서 정보 db로 읽어오기)
> - 추후 계획에 따라 추가되거나 제가되는 부분 생길 수 있음. 염두하기
> - 오류 해결에 시간 많이 씀.

## 6/3(월)
> - login정보와 game정보를 log.json으로 통합해서 가져오는 방법 여러 번 시도 -> 실패: db와 컬럼이 같지 않으면 db에 들어가지 않음을 확인
> - 하나의 json으로 받아오는 방법이 어려워져서 여러 json을 생성 후 통합하는 방법을 생각해보았으나 불필요한 json 파일 다수 생성 및 컬럼 통일 이슈가 발생할 것으로 예상
> - user, game(1,2,3)별로 테이블을 나누어 각자 데이터를 관리하기로 함 -> 테이블 생성 및 id로 테이블 간 연결까지 완료.

## 6/4(화)
> - db저장에 대한 고찰.
> - user테이블에 유저 정보가 들어가는 것 확인. -> 나머지 테이블(game1, game2, game3)에서 로그 정보가 제대로 저장되지 않는 문제 해결중.
> - 쿼리로 데이터 받아올지 아니면 logging 사용해서 데이터를 받아올지, 파일을 분할 해서 저장할지 고민중.
> - 내일까지 안되는 것 모두 해결 해야함 무조건!
> - 내일 오전까지 json에서 다시 받아오게 하는것으로 수정(id는 1로 고정)
> - nosql(mongodb)로 시도 해보기.
## 6/5(수)
> - 게임별로 json 파일 만들어서 json 파싱해서 db에 저장완료.
> - NoSql 사용으로 logging 해서 db에 저장하려고 했지만 noSql사용버의 미숙으로 사용보류.
> - json파일에서 로그가 변경될 때 db에 저장되어야 하는데 파일을 실행했을 때만 그 전 로그가 찍히는 오류가 있어서 오후중으로 해결.
> - 중복되는 값이 있을 때 새로운 로그가 입력이 되지 않는 오류가 있었는데 중복될 때 덮어쓰는 방식으로 해결.
> - watchdog을 이용한 데이터 모니터링을 통해서 json에 파일의 변경이 있을 때 db에 바로 저장되게 해결.
## 6월10일(월)
> - Game1 오류해결 하려 했으나 내일 최종 해결 예정
> - 

