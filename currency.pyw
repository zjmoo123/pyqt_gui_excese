import sys
from urllib import request
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        date = self.getdata()
        rates = sorted(self.rates.keys)

        dateLabel = QLabel(date)

        self.fromComboBox = QComboBox()
        self.fromComboBox.addItem(rates)
        self.fromSpinBox = QDoubleSpinBox()
        self.fromSpinBox.setRange(0.01, 10000000.00)
        self.fromSpinBox.setValue(1.00)
        self.toComBox = QComboBox()
        self.toComBox.addItem(rates)
        self.toLabel = QLabel("1.00")

        grid = QGridLayout()
        grid.addWidget(dateLabel, 0, 0)
        grid.addWidget(self.fromComboBox, 1, 0)
        grid.addWidget(self.fromSpinBox, 1, 1)
        grid.addWidget(self.toComBox, 2, 0)
        grid.addWidget(self.toLabel, 2, 1)
        self.setLayout(grid)

        self.fromComboBox.currentIndexChanged(int).connect(self.updateUi)
        self.toComBox.currentIndexChanged(int).connect(self.updateUi)
        self.fromSpinBox.valueChanged(float).connect(self.updateUi)
        self.setWindowTitle("Currency")
    def updateUi(self):
        to = self.toComBox.currentText()
        from_=self.fromComboBox.currentText()
        amount = (self.rates[from_]/ self.rates[to]) *self.fromSpinBox.value()
        self.toLabel.setText("%0.2f"%amount)
    def getdata(self):
        self.rates={}
        try:
            date = "Unknown"
            # fh=request.urlopen("http://www.bankofcanada.ca/valet/observations/group/FX_RATES_DAILY/csv")
        except:
            pass

class TaxRate(QObject):
    valueChanged=pyqtSignal(int)
    def __init__(self):
        super(TaxRate,self).__init__()
        self.__rate=17.5
    def rate(self):
        return self.__rate
    def connect_and_emit_valueChanged(self,value):
        self.valueChanged.connect(self.handle_valueChanged)
        self.valueChanged.emit(value)

    def handle_valueChanged(self,value):
        print("trigger signal received %d"% value)

x=TaxRate()
x.connect_and_emit_valueChanged(2);