2021년 경북대학교 SW 해커톤 - 제출용 Repo
===

## 참가자 정보
팀명: 하윤성<br>
참가자: 하윤성(컴퓨터학부 심컴 21학번) - 1인

## 작품명: UnivChat (Flask와 SocketIO를 이용한)

## 주제
대학생을 위한 익명 채팅

## 개발 동기 및 목적
1. 코로나19로 인하여 많은 동기 및 선후배를 만날 기회가 사라짐.
2. (특히 신입생) 코로나19로 인하여 대학 생활 안내 등을 기존만큼 받지 못하여 대학 생활 진행에 어려움을 겪음
3. 코로나19의 위험성 때문에 집 등에서 홀로 보내는 시간이 많아짐.<br>
→ 관계를 형성할 만한, 그리고 다수의 사람들과 시간을 보낼 필요성이 증가함.<br>
다만, "카카오톡 오픈채팅" 등은 링크를 특정 방법으로 공유해아 참여가 가능하고, 기존의 "에브리타임" 등의 서비스는 실시간 채팅에는 부적절한 부분이 있음.<br>
따라서, 익명 채팅 서비스를 개발해 보기로 결심함.

## 용도
대학생용 익명 채팅 사이트: 커뮤니티의 목적 및 질문방 (대학원생, 교수 구분 존재)으로 사용 가능.

## 기능
채팅 사이트 (로그인, 회원가입, 게스트, 채팅방)

## 영향
비록 디자인적인 면과 보안적 면에서 완성되지 못한 현재의 상태로는 큰 영향을 미치기 힘들겠지만, 이 코드를 바탕으로 디자인을 다듬어서 서비스를 출시한다면 대학생들의 여가 시간에 불특정 다수와 소통할 수 있는, 그리고 대학 생활에 필요한 정보를 얻는 서비스가 될 수 있을 것이라고 생각함.

## 시연 영샹: [링크](https://youtu.be/Bw4Lk3liJ0Q)

## 실행 방법
Repository 클론 후, src/clean-data 폴더를 src/data 폴더로 이름 변경 또는 복사 (빈 사용자 db 등 초기 데이터 포함됨 - 없을 시 오류 발생)<br>
python 설치 후, Flask, Flask-SocketIO, PySide6 라이브러리 설치 (pip install Flask Flask-SocketIO PySide6)<br>
이후, src/main.py 및 src/tools/UserManage.pyw 실행<br>
(현재 미완성 단계이기 때문에 Flask 내장 테스트 서버 사용, 실제 서비스에는 성능 및 보안상 FastCGI 등 사용 필요)
