import requests
import json
import os
from .Common import Base_url, access_token

Base_url = 'https://api.commerce.naver.com/external'


# 브랜드 id 조회 함수
def find_brand_id(brand):
    headers = { 'Authorization': f"Bearer {access_token}" }
    params = {'name': brand}
    return requests.get(url = Base_url + '/v1/product-brands', params=params, headers=headers ).json()

# 제조사 조회 함수
def find_manufacturers_id(manufacturers):
    headers = { 'Authorization': f"Bearer {access_token}" }
    return requests.get(url = Base_url + f'/v1/product-manufacturers?name={manufacturers}', headers=headers ).json()

# 카테고리 리스트 조회 함수
def get_Category_List():
    url = Base_url + "/v1/categories"
    params = { 'last' : True }
    headers = { 'Authorization': f"Bearer {access_token}" }
    res = requests.get(url, headers=headers, params = params)
    
    return res

def get_Major_Categories():
    url = Base_url + "/v1/categories"
    params = { 'last' : False }
    headers = { 'Authorization': f"Bearer {access_token}" }
    res = requests.get(url, headers=headers, params = params)
    categories = json.loads(res.text)
    MajorCategories =  [category for category in categories if category['wholeCategoryName'].find('>') == -1]
    return MajorCategories


def get_Child_Categories(ParentCategoryID):
    try:
        url = Base_url + f"/v1/categories/{ParentCategoryID}/sub-categories"
        headers = { 'Authorization': f"Bearer {access_token}" }
        res = requests.get(url, headers=headers)
        ChildCategories = json.loads(res.text)
 

        if res.status_code == 200:
            print(f"*** 하위 카테고리 조회 성공: {len(ChildCategories)} 건 / {[x['name'] for x in ChildCategories]}***")
            return ChildCategories
        else: 
            print(f"*** 하위 카테고리 조회 결과 없음: {ChildCategories['message']} ***") 
            return [] # 하위 카테고리가 없을 때
        
    except:
        print("*** 하위 카테고리 조회 실패 ***")



# 카탈로그 리스트 검색 함수 -> 검색어를 입력하면, 여러개의 후보를 검색해줌
def find_catalog_list(keyword):
    try:
        headers = { 'Authorization': f"Bearer {access_token}" }
        result = requests.get(url = Base_url + f'/v1/product-models?name={keyword}', headers=headers ).json()
        num = result['totalElements']
        print(f'[{keyword}] 검색 성공 : {num}건')
        return result
    except:
        print(f'[{keyword}] 검색 실패 ')

# 특정 카탈로그 정보 획득 함수 -> 카탈로그 안에 브랜드와 제조사 정보도 다 들어있음.
def get_catalog_record(id):
    headers = { 'Authorization': f"Bearer {access_token}" }
    return requests.get(url = Base_url + f'/v1/product-models/{id}', headers=headers ).json()


# 원산지 코드 검색 함수
def get_originAreaCode(area):
    headers = { 'Authorization': f"Bearer {access_token}" }
    return requests.get(url = Base_url + f'/v1/product-origin-areas/query?name={area}', headers=headers ).json()['originAreaCodeNames'][0]['code']


# 이미지 업로드 및 주소 획득 함수
def image_upload(image_folder_path):
    try:
        img_upload_url = Base_url + "/v1/product-images/upload"
        image_files = [os.path.join(image_folder_path, file) for file in os.listdir(image_folder_path)]
        files = {}
        
        for idx,image in enumerate(image_files):
            image_binary = open(image, 'rb').read()

            files[f"imageFiles[{idx}]"] = (f"image{idx}.jpg",image_binary,'image/jpeg')

            headers = {'Authorization': f'Bearer {access_token}'}

        upload_result = requests.post(img_upload_url, headers=headers, files=files)
        
        result = []
        for idx,item in enumerate(upload_result.json()['images']):
            result.append((os.listdir(image_folder_path)[idx][:-4], item['url']))

        print("*** 이미지 업로드 성공 ***")
        return result

    except:
        print("*** 이미지 업로드 실패 ***")


# 카테고리별 표준옵션 조회
def get_standard_option_id(CategoryId):
    try:
        url = Base_url + f'/v1/options/standard-options?categoryId={CategoryId}'
        headers = {'Authorization': f'Bearer {access_token}'}

        print(f'*** [CategoryId: {CategoryId}] 카테고리의 표준 옵션 항목 가져오기 성공 ***')
        return requests.get(url = url, headers=headers)
    except:
        print(f'*** [CategoryId: {CategoryId}] 카테고리의 표준 옵션 항목 가져오기 실패 ***')


# leafCategoryId : 어떤 카테고리의 표준 옵션 정보를 가져올건지? id 입력: ex) 
# option_ClassName : 표준 사이즈 옵션 종류 -- ex) 사이즈(한국), 색상
# options : 주문 가능한 표준 옵션 목록     -- ex) [225, 230, 235 ...]
def get_standard_attribute( leafCategoryId, option_ClassName , options ):
    try:
        url = Base_url + f'/v1/options/standard-options?categoryId={leafCategoryId}'
        headers = {'Authorization': f'Bearer {access_token}'}
        res = requests.get(url = url, headers=headers)
                
        # 표준 옵션 없을 때
        if json.loads(res.text)['useStandardOption'] == False:
            return []

        # 표준 옵션 목록
        standard_options = json.loads(res.text)['standardOptionCategoryGroups']
        #  표준 옵션 : option_ClassName에 대한 표준옵션
        standard_option = list(filter( lambda x: x['attributeName'] == option_ClassName , standard_options ))[0]

        print(f'*** [leafCategoryId: {leafCategoryId}] 카테고리의 {option_ClassName} 표준 옵션 가져오기 성공 ***')
        # 주문가능 옵션 (사이즈명, attributeId,attributeValueId) 리스트
        return list(filter( lambda x: x['attributeValueName'] in options , standard_option['standardOptionAttributes']))

    except:
         print(f'*** [leafCategoryId: {leafCategoryId}] 카테고리의 {option_ClassName} 표준 옵션 가져오기 실패 ***')


# leafCategoryId : 어떤 카테고리의 표준 옵션 정보를 가져올건지? id 입력: ex) 
def get_standard_attribute_names(leafCategoryId):
    try:
        url = Base_url + f'/v1/options/standard-options?categoryId={leafCategoryId}'
        headers = {'Authorization': f'Bearer {access_token}'}
        res = requests.get(url = url, headers=headers)

        # 표준 옵션 없을 때
        if json.loads(res.text)['useStandardOption'] == False:
            return []

        # 표준 옵션 목록
        standard_option_classes = json.loads(res.text)['standardOptionCategoryGroups']
        standard_option_classes_name = [x['attributeName'] for x in  standard_option_classes ]
        print(f'*** [leafCategoryId: {leafCategoryId}] 카테고리의 표준 옵션 클래스 리스트 가져오기 성공 ***')
        # 주문가능 옵션 (사이즈명, attributeId,attributeValueId) 리스트
        return standard_option_classes_name

    except:
        print(f'*** [leafCategoryId: {leafCategoryId}] 카테고리의 표준 옵션 클래스 리스트 가져오기 실패 ***')




# 상품정보제공공시 기준 카테고리 리스트 조회
def get_ItemInfo_notification_Categories():
    try:
        source = json.load(open('data/ItemInfo_notification_MASTER.json','r'))
        categories = [(category['productInfoProvidedNoticeTypeName'] , category['productInfoProvidedNoticeType']) for category in source]
      
        print('*** 상품정보 제공공시 카테고리 리스트 가져오기 성공 ***')
        return categories
    except:
        print('*** 상품정보 제공공시 카테고리 리스트 가져오기 실패 ***')


# 상품정보제공공시 기준 특정 카테고리의 항목 조회
def get_ItemInfo_notifications(my_category):
    try:
        source = json.load(open('data/ItemInfo_notification_MASTER.json','r'))
        Info_Nofications = list(filter( lambda x: x['productInfoProvidedNoticeType'] == my_category , source ))[0]
        Info_Nofications_keyword = [(field['fieldName'],field['fieldDescription']) for field in Info_Nofications['productInfoProvidedNoticeContents'] ]
      
        print(f'*** {my_category} 상품정보 제공공시 항목 가져오기 성공 ***')
        return Info_Nofications_keyword

    except:
        print(f'*** {my_category} 상품정보 제공공시 항목 가져오기 실패 ***')