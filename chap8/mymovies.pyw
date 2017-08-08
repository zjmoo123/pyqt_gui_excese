from PyQt5.QtCore import *
import PyQt5.QtGui
from PyQt5.QtWidgets import *

class MainWindow(QMainWindow):
    def __init__(self,parent=None):
        super(MainWindow, self).__init__(parent)
        self.movies = moviedata.MovieContainer()
        self.table = QTableWidget()
        self.setCentralWidget(self.table)

    def updateTable(self,current=None):
        self.table.clear()
        self.table.setRowCount(len(self.movies))
