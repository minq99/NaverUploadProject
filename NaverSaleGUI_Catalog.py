import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from tools.UploadTool import *

form_class  = uic.loadUiType("ui/NaverSaleGUI_catalog.ui")[0]
class WindowClass_catalog(QDialog, form_class):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.show()
        
        self.leafCategoryId_popup = ''
        self.catalog_Id = '' 
        self.catalog_Name = '' 
        self.category_Name = ''
        self.naverShoppingSearchInfo = {
        "modelId": '',
        "modelName": '',
        "manufacturerName": '',
        "brandId": '',
        "brandName": ''
        }


        # 확정/검색 버튼
        self.btn_confirm.clicked.connect(self.DialogClose)
        self.btn_search.clicked.connect(self.SetCatalogTable)


        # 테이블 이벤트 코딩
        self.highlighted_row = None         # 강조된 행의 인덱스 저장
        self.table_catalog.cellClicked.connect(self.cell_clicked)
        self.table_catalog.itemDoubleClicked.connect(self.item_double_clicked)
        

        # 검색어창
        self.keyword = ''
        self.lineEdit_keyword.textChanged.connect(self.set_keyword)



    def set_keyword(self):
        self.keyword = self.lineEdit_keyword.text()


        
    def DialogClose(self):
        self.close()


    def SetCatalogTable(self):
        if self.keyword == '':
            QMessageBox.warning(self, "경고", "keyword를 입력하세요")
            return
        
        # 데이터 추가
        self.table_catalog.setRowCount(0)  # 초기에는 행이 없음
        result = find_catalog_list(self.keyword)['contents']
        for recode in result:
            try: 
                self.add_row([recode['wholeCategoryName'], recode['categoryId'], recode['manufacturerCode'], recode['manufacturerName'], recode['brandCode'], recode['brandName'], recode['id'], recode['name']])
            except:
                # 가끔 특정 열의 누락이 있을 수 있음
                for key in ['wholeCategoryName','categoryId','manufacturerCode','manufacturerName','brandCode','brandName','id','name']:
                    if key not in recode.keys():
                        recode[key] = ''
                self.add_row([recode['wholeCategoryName'], recode['categoryId'], recode['manufacturerCode'], recode['manufacturerName'], recode['brandCode'], recode['brandName'], recode['id'], recode['name']])            

    def add_row(self, row_data):
        current_row = self.table_catalog.rowCount()
        self.table_catalog.insertRow(current_row)

        for idx, data in enumerate(row_data):
            self.table_catalog.setItem(current_row, idx, QTableWidgetItem(str(data)))


    def cell_clicked(self, row, col):
        # 셀 클릭 시그널 핸들러
        self.highlight_row(row)


    def item_double_clicked(self, item):
        # 더블클릭 시그널 핸들러
        if item is not None:
            row = item.row()  # 클릭한 아이템의 행 인덱스 가져오기
            row_data = [self.table_catalog.item(row, col).text() for col in range(self.table_catalog.columnCount())]

            # 필요 정보 맵핑
            self.catalog_Id = row_data[6]
            self.catalog_Name= row_data[7]
            self.category_Name = row_data[0]
            self.leafCategoryId_popup = row_data[1]
            self.naverShoppingSearchInfo = {
                "modelId": row_data[6],
                "modelName": row_data[7],
                "manufacturerName": row_data[3],
                "brandId": row_data[4],
                "brandName": row_data[5]
                }
            self.close()

        else:
            QMessageBox.warning(self, "경고", "더블클릭한 셀에 아이템이 없습니다.")

    def highlight_row(self, row):
        # 이전에 강조된 행을 되돌리기
        if self.highlighted_row is not None:
            for col in range(self.table_catalog.columnCount()):
                item = self.table_catalog.item(self.highlighted_row, col)
                if item is not None:
                    item.setBackground(Qt.white)

        # 현재 행을 강조
        for col in range(self.table_catalog.columnCount()):
            item = self.table_catalog.item(row, col)
            if item is not None:
                item.setBackground(Qt.darkCyan)
        
        # 강조된 행의 인덱스 업데이트
        self.highlighted_row = row