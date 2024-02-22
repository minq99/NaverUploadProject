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
from .Common import access_token, Base_url

def search_product(channelProductNo):
# 스마트스토어센터에서는 "채널상품번호"만을 제공함. -> 채널 상품 번호로 조회해야함 
    read_url = Base_url + f'/v2/products/channel-products/{channelProductNo}'
    headers = { 'Authorization': f"Bearer {access_token}" }
    response = requests.get(read_url, headers=headers)
    DATA =response.json()
    with open('./data.json', 'w', encoding='utf-8') as f:
        json.dump(DATA, f, ensure_ascii=False, indent=4)
    return response.text