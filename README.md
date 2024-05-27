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
