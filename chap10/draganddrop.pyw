from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import sys

class Form(QDialog):
    def __init__(self,parent=None):
        super(Form, self).__init__(parent)

        listWidget = QListWidget()
        listWidget.setAcceptDrops(True)
        listWidget.setDragEnabled(True)
        path = os.path.dirname(__file__)
        for image in sorted(os.listdir(os.path.join(path, "images"))):
            if image.endswith(".png"):
                item = QListWidgetItem(image.split(".")[0].capitalize())
                item.setIcon(QIcon(os.path.join(path,
                                                "images/{0}".format(image))))
                listWidget.addItem(item)

        iconListWidget = QListWidget()
        iconListWidget.setAcceptDrops(True)
        iconListWidget.setDragEnabled(True)
        iconListWidget.setViewMode(QListWidget.IconMode)

        tableWidget = QTableWidget()
        tableWidget.setRowCount(5)
        tableWidget.setColumnCount(2)
        tableWidget.setHorizontalHeaderLabels(["Column #1", "Column #2"])
        tableWidget.setAcceptDrops(True)
        tableWidget.setDragEnabled(True)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(listWidget)
        splitter.addWidget(iconListWidget)
        splitter.addWidget(tableWidget)
        layout = QHBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)

        self.setWindowTitle("Drag and Drop")

app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()