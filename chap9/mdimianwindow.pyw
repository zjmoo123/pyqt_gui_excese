from PyQt5.QtCore import *
import PyQt5.QtGui
from PyQt5.QtWidgets import *

class MainWindow(QMainWindow):
    def __init__(self,parent=None):
        super(MainWindow, self).__init__(parent)
        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)
        # textEdit = text