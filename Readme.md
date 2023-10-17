# WebCrawling for Naver Smart Place 
### 네이버 스마트 플레이스 예매자 페이지 웹 크롤링 

---
### 2023-10-17 Update

윈도우에서 크롬을 업데이트 할 경우 크롬 드라이버도 같이 업데이트 함. 
```commandline
pip install webdriver-auto-update
```


---
<img width="1210" alt="smartplace" src="https://github.com/AllenEdgarPoe/Naver-Crawling/assets/43398106/c1d0f7d3-7112-4176-840a-2ba97a930c16">
<br>

업체가 네이버 스마트 플레이스 를 통해 예약 페이지를 만들면, 네이버 에서는 페이지 자체는 만들어주지만 **유저의 정보를 자동으로 데이터베이스화 해주진 않는다!** <br>
엑셀로 만들어주는 기능이 있긴 한데, 업체가 어떤 조건을 만족하지 않으면 (연매출 1억 이하 라던지..) 엑셀 파일 다운 받아봤자 blank page 임. <br>
따라서 열 받아서 만든 네이버 스마트 플레이스 용 웹 크롤러. <br>

---

## 기능 
1. selenium, beautifulSoup 을 사용한 웹 크롤링. 예약한 사람들의 내역을 pandas Dataframe 화 해서 guests.csv 로 저장함
2. 우리 회사에서는 해당 db를 가지고 QR 정보를 쏘기 때문에 send_api 함수를 호출함 (restful API)
3. 이때 기존 db랑 비교해서 새로 예약한 내역 만 보낼 수 있다. 
4. scheduler 를 사용해서 5분에 한 번 마다 사용자 정보를 db에 업데이트함. 

## 사용법 
1. config.json 파일에서 **웹크롤링 페이지(url), api 호출 url(api_path), 네이버 아이디(userId), 비번(userPw)** 를 입력 
    ```
   {"url" : "로그인이 필요한 예약페이지 url",
   "api_path" : "api 호출 url",
   "userId": "네이버 아이디",
   "userPw": "네이버 비번"
    }
   ```
2. command line 에 ```python -m venv venv``` 로 새 가상환경 만듬. 
3. venv 킨다음 ```pip install -r requirements.txt``` 로 관련 라이브러리 깔기
4. 함수들 보면서 원하는 방식대로 바꾸기. 

---

### 여담 
위시켓 보니까 관련 작업 2500만원에 외주 올라와있었음. 

<img width="387" alt="외주" src="https://github.com/AllenEdgarPoe/Naver-Crawling/assets/43398106/001c47ed-5643-4d26-841a-b8d8d551df25">