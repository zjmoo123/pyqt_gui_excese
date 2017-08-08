from __future__ import division
import sys
from math import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Form(QDialog):
    def __init__(self,parent=None):
        super(Form,self).__init__(parent)
        self.browser = QTextBrowser()
        self.lineedit = QLineEdit("Type an expression and press Enter")
        self.lineedit.selectAll()
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        layout.addWidget(self.lineedit)
        self.setLayout(layout)
        self.lineedit.setFocus()
        # self.lineedit.returnPressed()
        # self.connectNotify(self.lineedit,self.lineedit.returnPressed(),self.updateUi)
        self.lineedit.returnPressed.connect(self.updateUi)

        # sld = QSlider(Qt.Horizontal, self)

        # sld.valueChanged.connect()


        # self.connectNotify(self.lineedit,SIGNAL("returnPressed()")),self.updateUi)
        self.setWindowTitle("Calculate")
    def updateUi(self):
        try:
            text = self.lineedit.text()
            self.browser.append("%s = <b>%s</b>" % (text,eval(text)))
        except:
            self.browser.append("<font color=red>%s is invalid!</font>" % text)
app =QApplication(sys.argv)
form = Form()
form.show()
app.exec_()