# Taabao carwler

## Goals
- 할인된 상품가격, 상품명, 옵션, 옵션이미지를 반환 하는 API 제작.

## Technical Skills
- Python, Selenium, Scrapy(TextResponse)

## Requirements
- scrapy 1.8.0
- ChromeDriver 83.0.4103.39
- fake-useragent 0.1.11
- selenium 3.141.0

## How to Use

```shell
$ python taobao_crawler.py item_id user_id, user_pw
# itemid 하나 입력
# 529586077819
```

```python
from taobao_crwler import ProductCrawler
crawler = ProductCrawler()
crawler.taobao_crawler([item_ids], "user_id", "user_pw")
# itemid를 list로 입력
# [529586077819, 44226087175, 521681811578, 536004719035]
```


## Issue
- 할인된 상품가격은 requests로 가져오지 못함 : 쿠키를 활용 & 로그인 정보 입력
  - 할인된 상품가격을 제외한 나머지 정보는 Selenium을 사용하지 않고 requests를 활용해 가져올수 있음
- 티몰은 여러 종류의 할인가격이 존재 : 각 가격 종류별로 가져옴
- 테스트를 위해 여러번 요청시 Block 당함 : 새로운 프록시 가져와서 진행

## Operation Flow
- 타오바오 & 티몰 상품 여부 확인 (최신 버전에선 삭제 - taobao의 itemId만으로 진행)
- 새로운 프록시 적용 
- 로그인 정보 입력
- 할인된 상품가격 정보 획득
- requests로 나머지 정보 획득

## Versions
- **taobao_ver1 ~ ver2** 
    - 미리 cookie를 생성해 두고, webdriver에 쿠키를 추가 하는 방식으로 할인 가격을 가져오려고 시도

    <img src="./taobao/img/img2.png" width="400px">

    - cookie값에 "expiry"가 존재 하고, api를 활용할떄 마다 새로운 쿠키를 생성해야 함


- **taobao_ver3** 
    - selenium을 활용해 로그인 정보를 직접 입력시키는 방법 

    <img src="./taobao/img/img3.png" width="400px">
    
    - 티몰 사이트에서 여러 itemid의 상품을 가져오기 위한 loop문을 돌릴때, login창 제어가 되지 않음.

- **taobao_crawler**(최신)
  - 타오바오의 상품만 가져오도록 변경


## 개선점
  - 한 api로 두 플랫폼의 상품을 모두 가져올수 있도록 해야 함

  <img src="./taobao/img/img1.png" width="400px">

  - 다량의 상품을 크롤링 하려 할때 발생하는 인증창 해결 필요
