from PyQt5.QtCore import *
import PyQt5.QtGui
from PyQt5.QtWidgets import *

class MainWindow(QMainWindow):
    NextId=1
    Instances =set()
    def __init__(self,parent=None):
        super(MainWindow, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        MainWindow.Instances.add(self)
        self.groupsList = QListWidget()
        self.messagesList = QListWidget()
        self.messageView = QTextBrowser()
        self.messageSplitter = QSplitter(Qt.Vertical)
        self.messageSplitter.addWidget(self.messagesList)
        self.messageSplitter.addWidget(self.messageView)
        self.mainSplitter = QSplitter(Qt.Horizontal)
        self.mainSplitter.addWidget(self.groupsList)
        self.mainSplitter.addWidget(self.messageSplitter)
        self.setCentralWidget(self.mainSplitter)
        self.mainSplitter.setStretchFactor(0,1)
        self.mainSplitter.setStretchFactor(1,3)
        self.messageSplitter.setStretchFactor(0,1)
        self.messageSplitter.setStretchFactor(1,2)
