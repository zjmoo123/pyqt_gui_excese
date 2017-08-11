from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import sys

LEFT, ABOVE = range(2)


class LabelledLineEdit(QWidget):
    def __init__(self, labelText="", position=LEFT, parent=None):
        super(LabelledLineEdit, self).__init__(parent)
        self.label = QLabel(labelText)
        self.lineEdit = QLineEdit()
        self.label.setBuddy(self.lineEdit)
        layout = QBoxLayout(QBoxLayout.LeftToRight if position == LEFT else QBoxLayout.TopToBottom)
        layout.addWidget(self.label)
        layout.addWidget(self.lineEdit)
        self.setLayout(layout)


class LabelledTextEdit(QWidget):
    def __init__(self, labelText="", position=LEFT,
                 parent=None):
        super(LabelledTextEdit, self).__init__(parent)
        self.label = QLabel(labelText)
        self.textEdit = QTextEdit()
        self.label.setBuddy(self.textEdit)
        layout = QBoxLayout(QBoxLayout.LeftToRight
                            if position == LEFT else QBoxLayout.TopToBottom)
        layout.addWidget(self.label)
        layout.addWidget(self.textEdit)
        self.setLayout(layout)


class Dialog(QDialog):
    def __init__(self, address=None, parent=None):
        super(Dialog, self).__init__(parent)

        self.street = LabelledLineEdit("&Street:")
        self.city = LabelledLineEdit("&City:")
        self.state = LabelledLineEdit("St&ate:")
        self.zipcode = LabelledLineEdit("&Zipcode:")
        self.notes = LabelledTextEdit("&Notes:", ABOVE)
        if address is not None:
            self.street.lineEdit.setText(address.get("street"))
            self.city.lineEdit.setText(address.get("city"))
            self.state.lineEdit.setText(address.get("state"))
            self.zipcode.lineEdit.setText(address.get("zipcode"))
            self.notes.textEdit.setPlainText(address.get("notes"))
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok |
                                     QDialogButtonBox.Cancel)

        grid = QGridLayout()
        grid.addWidget(self.street, 0, 0)
        grid.addWidget(self.city, 0, 1)
        grid.addWidget(self.state, 1, 0)
        grid.addWidget(self.zipcode, 1, 1)
        grid.addWidget(self.notes, 2, 0, 1, 2)
        layout = QVBoxLayout()
        layout.addLayout(grid)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.setWindowTitle("Labelled Widgets")


if __name__ == "__main__":
    fakeAddress = dict(street="3200 Mount Vernon Memorial Highway",
                       city="Mount Vernon", state="Virginia",
                       zipcode="22121")
    app = QApplication(sys.argv)
    form = Dialog(fakeAddress)
    form.show()
    app.exec_()
    print("Street:", form.street.lineEdit.text())
    print("City:", form.city.lineEdit.text())
    print("State:", form.state.lineEdit.text())
    print("Notes:")
    print(form.notes.textEdit.toPlainText())