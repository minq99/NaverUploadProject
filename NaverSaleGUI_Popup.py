import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *

form_class_option  = uic.loadUiType("ui/NaverSaleGUI_option.ui")[0]
class WindowClass_option(QDialog, form_class_option):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.show()
        self.color = ''

        self.btn_confirm.clicked.connect(self.dialog_close)
        self.textEdit_color.textChanged.connect(self.set_color)

    def dialog_close(self):

        self.close()

    def set_color(self):
        self.color = self.textEdit_color.toPlainText()


