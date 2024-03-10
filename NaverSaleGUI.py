import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
import time
import datetime
import requests
from itertools import product
import tools.Common
from tools.UploadTool import * 
from tools.SearchTool import *
from tools.RenewTool import *
# 옵션 화면
from NaverSaleGUI_Option import WindowClass_option
from NaverSaleGUI_Catalog import WindowClass_catalog


# UI파일 연결
#단, UI파일은 Python 현재 폴더 내부의 ui 폴더에 위치해야한다.
form_class = uic.loadUiType("ui/NaverSaleGUI.ui")[0]



print("access_token: ", access_token)

[x['name'] for x in get_Major_Categories()]
[x['id'] for x in get_Major_Categories()]
ItemInfo_notification_Categories = get_ItemInfo_notification_Categories()
ItemInfo_notifications_WEAR = ['A','B','C']
ItemInfo_notifications_SHOES = ['A','B','C','D','E','A','B','C','D','E']



#화면을 띄우는데 사용되는 Class 선언
class WindowClass_main(QDialog, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■  변수 선언  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    ##### 고정변수 ##### 

        # AS 정보
        self.afterServiceTelephoneNumber = '010-2936-1595'
        self.afterServiceGuideContent = '상품 오배송 및 파송시 A/S 도와드리겠습니다'

        # 판매 기간 정보
        self.saleStartDate = (datetime.datetime.now() + datetime.timedelta(minutes=3)).strftime('%Y-%m-%dT%H:%M:%SZ')  # 현재로부터 3분 뒤
        self.saleEndDate = '2099-01-13T01:30:56Z'
        
        # 세일 기간 정보
        self.Discount_StartDate = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H')+':00:00Z'  # 현재로부터 다음 정각
        self.Discount_EndDate = '2099-01-13T01:59:00Z'

        # 원산지 정보
        self.originAreaInfo_JAPAN = {
        "originAreaCode": get_originAreaCode('일본'),
        "importer": "japan", # 수입사인 경우 필수
        "content": "string",
        "plural": True
        }

        # 부가가치세 타입 : 디폴트는 과세상품 -> TAX(과세 상품), DUTYFREE(면세 상품), SMALL(영세 상품)
        self.taxType =  "TAX"





##### 상품등록에 필요한 변수들 #####
        # 상품 이름 // ok
        self.name = ''
        # 상품 상세설명 // ok
        self.detailContent = ''
        # 판매 가격 (필수) // ok
        self.salePrice = 0  
        # 재고량 // ok
        self.stockQuantity = 1000
        # 리프 카테고리 id  // ok
        self.leafCategoryId = ''

        # 네이버쇼핑 검색 정보 (카탈로그) //ok
        self.catalog_Id = '' 
        self.naverShoppingSearchInfo = {
        "modelId": '',
        "modelName": '',
        "manufacturerName": '',
        "brandId": '',
        "brandName": ''
        }

        #옵션 // ok
        self.ImageUrl_Main   =  []  #image_upload('image/240119/main/') 
        self.ImageUrl_Extra  =  []  #image_upload('image/240119/extra/')
        self.ImageUrl_option =  []  #image_upload('image/240119/option/')

        # 대표이미지, 추가이미지 URL // ok
        self.representativeImageURL = '' #ImageUrl_Main[0][1] # 블랙 
        self.optionalImagesURLs = '' #[ {"url": x[1]} for x in ImageUrl_Extra]

        # 사이즈 및 색깔 등 // ok
        self.options_1  = []       
        self.options_2  = []      
        self.options_3  = []      

        # 표준 옵션 -> 카테고리 아이디를 타고 가서 어떤 표준옵션을 선택할지 정해야함. // ok
        self.standard_attribute_1  = [] # get_standard_attribute(leafCategoryId, '사이즈(한국)',  options_1 )
        self.standard_attribute_2 = []
        
        # 메인/서브 이미지 등록 
        self.OptionGroup1 = {}  # 옵션 1
        self.OptionGroup2 = {}  # 옵션 2
        # 옵션 매칭
        self.items = []              # [options_color, options_size]
        self.optionStandards =  [ ]  # items 활용
        self.simpleOption_template = {}
        self.optionInfo = {} # self.optionInfo = self.simpleOption_template

        # 제조일자 : 인증 유형이 방송통신기자재 적합인증/적합등록/잠정인증인 경우 필수. 'yyyy-MM-dd' 형식 입력.
        self.manufactureDate =  '2023-11-01' # "yyyy-mm-dd" 형태
        # 유효일자: 
        self.validDate = '2033-11-01'   # "yyyy-mm-dd" 형태
        # 인증정보
        self.productCertificationInfos = []
        # 인증제외
        self.certificationTargetExcludeContent =  { },
        # 미성년자 사용 가능 여부
        self.minorPurchasable =  True
        # 상품정보제공고시
        self.productInfoProvidedNoticeType = ''
        # 문화비 소득공제 여부: 예외 카테고리 중 도서_일반, 도서_해외, 도서_중고, 도서_E북, 도서_오디오북, 문화비_소득공제에 해당하는 경우 입력할 수 있습니다. 미입력 시 false로 저장됩니다.
        self.cultureCostIncomeDeductionYn = False
        # 맞춤 제작 상품 여부
        self.customProductYn = False
        # 자체 제작 상품 여부
        self.itselfProductionProductYn =  False
        # (SEO(Search engine optimization) 정보) : pageTitle/metaDescription : 상품 정보를 SNS 등 소셜 서비스에 공유 시 검색 최적화를 위한 기능으로 검색에 활용될 수 있도록 설정할 수 있습니다.
        self.pageTitle = "title태그"
        self.metaDescription = "한줄 설명"
        self.tags = []
        self.seoInfo = {}

        # 할인 정보
        self.discount_unitType = 'PERCENT' # 할인 단위 타입 ->  PERCENT, WON만 입력 가능합니다.
        self.discount_value  = ''        # 할인 단위에 따른 값을 입력합니다.
        self.discount_startDate = ''
        self.discount_endDate = ''

        # 배송요금 // ok
        self.baseFee = 4000  # 기본요금
        self.area2extraFee = 7000
        self.returnDeliveryFee = 4000
        self.exchangeDeliveryFee = 8000
        

        self.deliveryInfo =  {
                            "deliveryType": "DELIVERY",                  # DELIVERY(택배, 소포, 등기), DIRECT(직접배송(화물배달))
                            "deliveryAttributeType": "NORMAL",
                            "deliveryCompany": "EPOST",
                            "deliveryBundleGroupUsable": True,
                            # "deliveryBundleGroupId": 0,
                            "deliveryFee": {
                                "deliveryFeeType": "PAID",
                                "baseFee": self.baseFee,
                                "deliveryFeePayType": "PREPAID",
                                "deliveryFeeByArea": {
                                "deliveryAreaType": "AREA_2",
                                "area2extraFee": self.area2extraFee,
                                },
                            },

                            "claimDeliveryInfo": {
                                "returnDeliveryCompanyPriorityType": "PRIMARY",
                                "returnDeliveryFee": self.returnDeliveryFee,
                                "exchangeDeliveryFee":self.exchangeDeliveryFee,
                            },
                            # "installationFee": False, # 별도 설치비 유무
                            # "expectedDeliveryPeriodType": "ETC",
                            # "expectedDeliveryPeriodDirectInput": "string",
                            # "todayStockQuantity": 0,
                            # "customProductAfterOrderYn": True,
                            # "hopeDeliveryGroupId": 0
                            }    

##### 로직에 필요한 중간 변수들 #####
        self.lineedits_ItemInfo_notification = []
        self.Major_categories = get_Major_Categories()
        self.categories2= []
        self.categories3= []

        self.ctgy1 = '' # 대분류 id
        self.ctgy2 = '' # 중분류 id
        self.ctgy3 = '' # 소분류 id
        self.ctgy4 = '' # 세분류 id
        
        self.category_Name = ''

        # 이미지 경로
        self.MainImgPath   =  ''  # image/240119/main/
        self.ExtraImgPath  =  ''  # image/240119/extra/
        self.OptionImgPath =  ''  # image/240119/option/

        # 표준 옵션 이름
        self.standard_option_name_1 = '사이즈(한국)'
        self.standard_option_name_2 = '색상'
        self.standard_option_name_3 = ''

#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■  메소드  ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■


#### 버튼 메소드 ########################################################################################################################################################################################################

        self.btn_PrintValues.clicked.connect(self.print_values)
        self.btn_GetFromUrl.clicked.connect(self.changeTextFunction)
        self.btn_option.clicked.connect(self.popup_option)
        self.btn_search_catalog.clicked.connect(self.popup_catalog)



#### 입력창 메소드/ 세팅 ########################################################################################################################################################################################################
        # 제목
        self.textEdit_ItemName.textChanged.connect(self.set_Itemname)
        # 상품상세
        self.textEdit_detailContent.textChanged.connect(self.set_detailContent)
        # 가격
        self.lineEdit_salePrice.textChanged.connect(self.set_salePrice)
        # 재고량
        self.lineEdit_stockQuantity.setText(str(self.stockQuantity))
        self.lineEdit_stockQuantity.textChanged.connect(self.set_stockQuantity)

        # 판매시작/판매마감/할인시작/할인마감 데이터 
        self.dateEdit_SaleFrom.setDate(QDateTime.fromString(self.saleStartDate, Qt.ISODate).date())
        self.timeEdit_SaleFrom.setTime(QDateTime.fromString(self.saleStartDate, Qt.ISODate).time())
        self.dateEdit_SaleTo.setDate(QDateTime.fromString(self.saleEndDate, Qt.ISODate).date())
        self.timeEdit_SaleTo.setTime(QDateTime.fromString(self.saleEndDate, Qt.ISODate).time())
        self.dateEdit_DiscountFrom.setDate(QDateTime.fromString(self.Discount_StartDate, Qt.ISODate).date())
        self.timeEdit_DiscountFrom.setTime(QDateTime.fromString(self.Discount_StartDate, Qt.ISODate).time())
        self.dateEdit_DiscountTo.setDate(QDateTime.fromString(self.Discount_EndDate, Qt.ISODate).date())
        self.timeEdit_DiscountTo.setTime(QDateTime.fromString(self.Discount_EndDate, Qt.ISODate).time())
        self.dateEdit_SaleFrom.dateChanged.connect(self.SaleFrom_datetime)
        self.timeEdit_SaleFrom.timeChanged.connect(self.SaleFrom_datetime)
        self.dateEdit_SaleTo.dateChanged.connect(self.SaleTo_datetime)
        self.timeEdit_SaleTo.timeChanged.connect(self.SaleTo_datetime)
        self.dateEdit_DiscountFrom.dateChanged.connect(self.DiscountFrom_datetime)
        self.timeEdit_DiscountFrom.timeChanged.connect(self.DiscountFrom_datetime)
        self.dateEdit_DiscountTo.dateChanged.connect(self.DiscountTo_datetime)
        self.timeEdit_DiscountTo.timeChanged.connect(self.DiscountTo_datetime)

        # 이미지 경로 입력창
        self.lineEdit_MainImage.textChanged.connect(self.set_MainImagePath)    
        self.lineEdit_ExtraImage.textChanged.connect(self.set_ExtraImagePath)    
        self.lineEdit_OptionImage.textChanged.connect(self.set_OptionImage)   

        # 옵션
        self.lineEdit_option1.textChanged.connect(self.set_Option1)  
        self.lineEdit_option2.textChanged.connect(self.set_Option2)  
        self.lineEdit_option3.textChanged.connect(self.set_Option3)  


        # 배송비 입력창
        self.lineEdit_baseFee.setText(str(self.baseFee))
        self.lineEdit_area2extraFee.setText(str(self.area2extraFee))
        self.lineEdit_returnDeliveryFee.setText(str(self.returnDeliveryFee))
        self.lineEdit_exchangeDeliveryFee.setText(str(self.exchangeDeliveryFee))
        self.lineEdit_baseFee.textChanged.connect(self.set_Basefee)
        self.lineEdit_area2extraFee.textChanged.connect(self.set_area2extraFee)
        self.lineEdit_returnDeliveryFee.textChanged.connect(self.set_returnDeliveryFee)
        self.lineEdit_exchangeDeliveryFee.textChanged.connect(self.set_exchangeDeliveryFee)









#### 콤보박스 데이터 추가 및 메소드 ########################################################################################################################################################################################################
        self.comboBox_ItemInfo_notification.addItems([x[0] for x in ItemInfo_notification_Categories])
        self.comboBox_ItemInfo_notification.currentIndexChanged.connect(self.update_ItemInfo_notification)
        self.update_ItemInfo_notification() # 일단 index 0번으로 화면 만들기

        self.comboBox_Ctgy1.addItems([x['name'] for x in self.Major_categories])
        self.comboBox_Ctgy1.currentIndexChanged.connect(self.update_Ctgy1)
        self.comboBox_Ctgy2.currentIndexChanged.connect(self.update_Ctgy2)
        self.comboBox_Ctgy3.currentIndexChanged.connect(self.update_Ctgy3)
        self.comboBox_Ctgy4.currentIndexChanged.connect(self.update_Ctgy4)
        self.update_Ctgy1()



        # 사이즈 재조정
        # self.setFixedSize(1800,1200)




    def print_values(self):
        print("****************** values click! ******************")
        print("name: ", self.name)
        print("detailContent: ",  self.detailContent)
        print("salePrice: ", self.salePrice)
        print("stockQuantity: ", self.stockQuantity)
        print("leafCategoryId: ", self.leafCategoryId)

        print("saleStartDate: ", self.saleStartDate)
        print("saleEndDate: ", self.saleEndDate)
        print("Discount_StartDate: ",self.Discount_StartDate)
        print("Discount_EndDate: ", self.Discount_EndDate) 

        print("MainImgPath: ", self.MainImgPath)   
        print("ExtraImgPath: ", self.ExtraImgPath) 
        print("OptionImgPath: ", self.OptionImgPath) 

        # # 메인, 추가, 옵션 이미지
        # self.ImageUrl_Main   = image_upload(self.MainImgPath) 

        # if self.ExtraImgPath: 
        #     self.ImageUrl_Extra  = image_upload(self.ExtraImgPath)
        #     self.optionalImagesURLs = self.ImageUrl_Main[0][1]

        # if self.OptionImgPath: 
        #     self.ImageUrl_option = image_upload(self.OptionImgPath)
        #     self.optionalImagesURLs = [ {"url": x[1]} for x in self.ImageUrl_Extra]

        print("ImageUrl_Main: ", self.ImageUrl_Main)   
        print("ImageUrl_Extra: ", self.ImageUrl_Extra) 
        print("ImageUrl_option: ", self.ImageUrl_option) 

        print(f"{self.standard_option_name_1}: ", self.options_1)
        print(f"{self.standard_option_name_2}: ", self.options_2)
        print(f"{self.standard_option_name_3}: ", self.options_3)

        # # standard_attribute 설정 -> standard_option_name 설정해야함
        # if self.standard_option_name_1:
        #     self.standard_attribute_1  = get_standard_attribute(self.leafCategoryId, self.standard_option_name_1,  self.options_1 )
        # if self.standard_option_name_2:
        #     self.standard_attribute_2  = get_standard_attribute(self.leafCategoryId, self.standard_option_name_2,  self.options_2 )
        # if self.standard_option_name_3:
        #     self.standard_attribute_3  = get_standard_attribute(self.leafCategoryId, self.standard_option_name_3,  self.options_3 )







    def set_Itemname(self):
        self.name = self.textEdit_ItemName.toPlainText()
    
    def set_detailContent(self):
        self.detailContent = self.textEdit_detailContent.toPlainText()
        
    def set_salePrice(self):
        self.salePrice = int(self.lineEdit_salePrice.text())

    def set_stockQuantity(self):
        self.stockQuantity = int(self.lineEdit_stockQuantity.text())

    def changeTextFunction(self):
        self.textEdit_name.setText("url으로부터 가져온 이름")

    def update_ItemInfo_notification(self):

        # 기존 LineEdits Clear 
        for lineedit in self.lineedits_ItemInfo_notification:
            lineedit[0].setParent(None)
            lineedit[1].setParent(None)
        
        # 현재 카테고리 가져오기
        self.category = ItemInfo_notification_Categories[self.comboBox_ItemInfo_notification.currentIndex()][1]
        self.lineedits_ItemInfo_notification = [[QLabel(x[1]), QLineEdit()] for x in get_ItemInfo_notifications(self.category)]

        for lineedit in self.lineedits_ItemInfo_notification:
            self.verticalLayout_ItemInfo_notification.addWidget(lineedit[0])    
            self.verticalLayout_ItemInfo_notification.addWidget(lineedit[1])    



    def update_Ctgy1(self):
        # Ctgr1이 변하면서 self.ctgy1 입력 + 나머지 Ctgy 2 변경 및 3,4를 초기화

        # 우선 update_Ctgy2 시그널 해제
        self.comboBox_Ctgy2.currentIndexChanged.disconnect(self.update_Ctgy2)

        self.ctgy1 =  self.Major_categories[self.comboBox_Ctgy1.currentIndex()]['id']
        self.comboBox_Ctgy2.clear()
        self.categories2 = get_Child_Categories(self.ctgy1)
        self.comboBox_Ctgy2.addItems([x['name'] for x in self.categories2])
        self.comboBox_Ctgy2.setCurrentIndex(-1)
        self.comboBox_Ctgy3.clear()
        self.comboBox_Ctgy4.clear()
        self.leafCategoryId = self.ctgy1
        self.lineEdit_categoryID.setText(self.leafCategoryId)
        # 이후 update_Ctgy2 시그널 재설정
        self.comboBox_Ctgy2.currentIndexChanged.connect(self.update_Ctgy2)

    def update_Ctgy2(self):
        # Ctgr2가 변하면서 self.ctgy2 입력 + 나머지 Ctgy 3 변경 및 4를 초기화

        # 우선 update_Ctgy3 시그널 해제
        self.comboBox_Ctgy3.currentIndexChanged.disconnect(self.update_Ctgy3)

        self.ctgy2 =  self.categories2[self.comboBox_Ctgy2.currentIndex()]['id']
        self.comboBox_Ctgy3.clear()
        self.categories3 = get_Child_Categories(self.ctgy2)
        self.comboBox_Ctgy3.addItems([x['name'] for x in self.categories3])
        self.comboBox_Ctgy3.setCurrentIndex(-1)
        self.comboBox_Ctgy4.clear()
        self.leafCategoryId = self.ctgy2
        self.lineEdit_categoryID.setText(self.leafCategoryId)

        # 이후 update_Ctgy3 시그널 재설정
        self.comboBox_Ctgy3.currentIndexChanged.connect(self.update_Ctgy3)



    def update_Ctgy3(self):
        # Ctgr3가 변하면서 self.ctgy3 입력 + 나머지 Ctgy 4 변경
        if  self.comboBox_Ctgy3.currentIndex() == -1 :
            return
        # 우선 update_Ctgy4 시그널 해제
        self.comboBox_Ctgy4.currentIndexChanged.disconnect(self.update_Ctgy4)

        self.ctgy3 =  self.categories3[self.comboBox_Ctgy3.currentIndex()]['id']
        self.comboBox_Ctgy4.clear()
        self.categories4 = get_Child_Categories(self.ctgy3)
        self.comboBox_Ctgy4.addItems([x['name'] for x in self.categories4])
        self.comboBox_Ctgy4.setCurrentIndex(-1)
        self.leafCategoryId = self.ctgy3
        self.lineEdit_categoryID.setText(self.leafCategoryId) 

        if len(self.categories4) == 0:
            print("self.comboBox_Ctgy4 disabled")
            self.comboBox_Ctgy4.setEnabled(False)
        else:
            print("self.comboBox_Ctgy4 enabled")
            self.comboBox_Ctgy4.setEnabled(True)

        # update_Ctgy4 시그널 재설정
        self.comboBox_Ctgy4.currentIndexChanged.connect(self.update_Ctgy4)


    def update_Ctgy4(self):
        # Ctgr4가 변하면서 self.ctgy4 입력
        if (len(self.categories4) < 0):
            print("len(self.categories4) < 0")
            return

        if (self.comboBox_Ctgy4.currentIndex() != -1):
            print(self.comboBox_Ctgy4.currentIndex())
            self.ctgy4 =  self.categories4[self.comboBox_Ctgy4.currentIndex()]['id']
            self.leafCategoryId = self.ctgy4
            self.lineEdit_categoryID.setText(self.leafCategoryId)
    


    def SaleFrom_datetime(self):
        updated_date = self.dateEdit_SaleFrom.date()
        updated_time = self.timeEdit_SaleFrom.time()
        updated_datetime = QDateTime(updated_date, updated_time)
        self.saleStartDate = updated_datetime.toString(Qt.ISODate)

    def SaleTo_datetime(self):
        updated_date = self.dateEdit_SaleTo.date()
        updated_time = self.timeEdit_SaleTo.time()
        updated_datetime = QDateTime(updated_date, updated_time)
        self.saleEndDate = updated_datetime.toString(Qt.ISODate)

    def DiscountFrom_datetime(self):
        updated_date = self.dateEdit_DiscountFrom.date()
        updated_time = self.timeEdit_DiscountFrom.time()
        updated_datetime = QDateTime(updated_date, updated_time)
        self.Discount_StartDate = updated_datetime.toString(Qt.ISODate)


    def DiscountTo_datetime(self):
        updated_date = self.dateEdit_DiscountTo.date()
        updated_time = self.timeEdit_DiscountTo.time()
        updated_datetime = QDateTime(updated_date, updated_time)
        self.Discount_EndDate = updated_datetime.toString(Qt.ISODate)



    # 팝업 옵션
    def popup_option(self):
        self.window2 = WindowClass_option(self.leafCategoryId)
        self.window2.exec_()
        # exec_() 아래 코드는 팝업이 닫히고 난 뒤 실행됨
        self.lineEdit_color.setText(self.window2.color) 
        self.color = self.window2.color

        self.show()


    def popup_catalog(self):
        self.window3 = WindowClass_catalog()
        self.window3.exec_()
        # exec_() 아래 코드는 팝업이 닫히고 난 뒤 실행됨

        self.lineEdit_catalogID.setText(self.window3.catalog_Id) 
        self.catalog_Id = self.window3.catalog_Id

        self.lineEdit_catalogName.setText(self.window3.catalog_Name) 
        self.naverShoppingSearchInfo = self.window3.catalog_Name

        self.lineEdit_categoryID.setText(self.window3.leafCategoryId_popup) 
        self.leafCategoryId = self.window3.leafCategoryId_popup

        self.category_Name = self.window3.category_Name
        for comboBox in [self.comboBox_Ctgy1, self.comboBox_Ctgy2, self.comboBox_Ctgy3, self.comboBox_Ctgy4]:
            comboBox.setCurrentIndex(-1)




    def set_Option1(self):
        self.options_1 = self.lineEdit_option1.text()
    
    def set_Option2(self):
        self.options_2 = self.lineEdit_option2.text()


    def set_Option3(self):
        self.options_3 = self.lineEdit_option3.text()





    def set_MainImagePath(self): 
        self.MainImgPath   =  self.lineEdit_MainImage.text()

    def set_ExtraImagePath(self): 
        self.ExtraImgPath  =  self.lineEdit_ExtraImage.text()

    def set_OptionImage(self): 
        self.OptionImgPath =  self.lineEdit_OptionImage.text()

    def set_Basefee(self): 
        self.baseFee = self.lineEdit_baseFee.text()

    def set_area2extraFee(self): 
        self.area2extraFee = self.lineEdit_area2extraFee.text()

    def set_returnDeliveryFee(self): 
        self.returnDeliveryFee = self.lineEdit_returnDeliveryFee.text()
        
    def set_exchangeDeliveryFee(self): 
        self.exchangeDeliveryFee = self.lineEdit_exchangeDeliveryFee.text()








        self.show()




if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv) 

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass_main() 

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()

    
