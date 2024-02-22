from .Common import access_token, Base_url
import requests
import json


def Update_ItemInfoNotification():
    try:
        url = Base_url + f'/v1/products-for-provided-notice'
        headers = {'Authorization': f'Bearer {access_token}'}
        res = requests.get(url = url, headers=headers)
        data_dict = json.loads(res.text)
        with open('data/ItemInfo_notification_MASTER.json', 'w') as outfile:
            json.dump(data_dict, outfile)
        print('*** 상품정보 제공공시 master 업데이트 완료 (ItemInfo_notification.json) ***')
    except:
        print('*** 상품정보 제공공시 master 업데이트 실패 (ItemInfo_notification.json) ***')


# 카테고리 리스트 최신화
def Update_Category_List():
    url = Base_url + "/v1/categories"
    params = { 'last' : True }
    headers = { 'Authorization': f"Bearer {access_token}" }
    res = requests.get(url, headers=headers, params = params)

    data_dict = json.loads(res.text)
    with open('data/Categories.json', 'w') as outfile:
        json.dump(data_dict, outfile)