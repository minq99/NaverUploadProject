import bcrypt
import pybase64
import time
import requests
import json
import http.client
import pandas as pd
import time
import datetime
import os
import base64

# access_token 획득 함수
def get_access_token():
    try:
        # 전자서명 발급시 필요 정보
        clientId = "5jmD80YKg6npnmIulyuXvQ"               # 어플리케이션 아이디
        clientSecret = "$2a$04$gpPp8MzbTxgXyAJdJ7C.eO"    # 어플리케이션 시크릿
        timestamp = int(time.time() * 1000) - 10000        # 밀리초(millisecond) 단위의 Unix 시간 : 동기화 문제때문에 1초 과거 시간으로

        # bcrypt 방식으로 인코딩(hashing)
        password = clientId + "_" + str(timestamp)
        hashed = bcrypt.hashpw(password.encode('utf-8'), clientSecret.encode('utf-8'))

        # 전자서명
        elec_sign = pybase64.standard_b64encode(hashed).decode('utf-8')

        # 인증 토큰 API
        Auth_URL = Base_url + "/v1/oauth2/token"
        params = {
        "client_id" : clientId,
        "timestamp" : timestamp,
        "client_secret_sign": elec_sign ,
        "grant_type": 'client_credentials',
        "type": "SELF",  # or self
        #"account_id": 'eun21207',	
        }
        response = requests.post(Auth_URL, params=params)

        access_token = response.json()["access_token"]

        return access_token
    except:
        print("Access Token 발급 실패")





Base_url = 'https://api.commerce.naver.com/external'

## 1로 바꿔야함
access_token = get_access_token()

