import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
import tools.Common
from tools.UploadTool import * 
from tools.SearchTool import *
from tools.RenewTool import *
        
form_class  = uic.loadUiType("ui/NaverSaleGUI_option.ui")[0]
class WindowClass_option(QDialog, form_class):
    def __init__(self, leafCategoryId) :
        super().__init__()
        self.setupUi(self)
        self.show()
        self.color = ''

        self.btn_confirm.clicked.connect(self.dialog_close)
        self.textEdit_color.textChanged.connect(self.set_color)
        
        self.leafCategoryId = leafCategoryId

        self.SetCatalogTable()


    def SetCatalogTable(self):
        # 데이터 추가
        self.table_OptionName.setRowCount(0)  # 초기에는 행이 없음
        result = get_standard_attribute_names(self.leafCategoryId) # NaberSaleGUI.py에서 전달받음
        for idx, recode in enumerate(result):
            self.add_row([idx, recode])
        
    
    def dialog_close(self):

        self.close()


    def add_row(self, row_data):
        current_row = self.table_OptionName.rowCount()
        self.table_OptionName.insertRow(current_row)

        for idx, data in enumerate(row_data):
            self.table_OptionName.setItem(current_row, idx, QTableWidgetItem(str(data)))

        
    def set_color(self):
        self.color = self.textEdit_color.toPlainText()


