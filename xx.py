import sys
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QCheckBox, QDialog, QFrame,
                             QGridLayout, QHBoxLayout, QLabel, QLayout, QLineEdit,
                             QPushButton, QVBoxLayout)


class FindAndReplaceDlg(QDialog):
    find = pyqtSignal(str, bool, bool, bool, bool, bool)
    replace = pyqtSignal(str, str, bool, bool, bool, bool, bool)

    def __init__(self, parent=None):
        super(FindAndReplaceDlg, self).__init__(parent)

        findLabel = QLabel("Find &what:")
        self.findLineEdit = QLineEdit()
        findLabel.setBuddy(self.findLineEdit)
        replaceLabel = QLabel("Replace w&ith:")
        self.replaceLineEdit = QLineEdit()
        replaceLabel.setBuddy(self.replaceLineEdit)
        self.caseCheckBox = QCheckBox("&Case sensitive")
        self.wholeCheckBox = QCheckBox("Wh&ole words")
        self.wholeCheckBox.setChecked(True)
        self.moreFrame = QFrame()
        self.moreFrame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.backwardsCheckBox = QCheckBox("Search &Backwards")
        self.regexCheckBox = QCheckBox("Regular E&xpression")
        self.ignoreNotesCheckBox = QCheckBox("Ignore foot&notes "
                                             "and endnotes")
        line = QFrame()
        line.setFrameStyle(QFrame.VLine | QFrame.Sunken)
        self.findButton = QPushButton("&Find")
        self.replaceButton = QPushButton("&Replace")
        closeButton = QPushButton("Close")
        self.moreButton = QPushButton("&More")
        self.moreButton.setCheckable(True)

        gridLayout = QGridLayout()
        gridLayout.addWidget(findLabel, 0, 0)
        gridLayout.addWidget(self.findLineEdit, 0, 1)
        gridLayout.addWidget(replaceLabel, 1, 0)
        gridLayout.addWidget(self.replaceLineEdit, 1, 1)
        frameLayout = QVBoxLayout()
        frameLayout.addWidget(self.backwardsCheckBox)
        frameLayout.addWidget(self.regexCheckBox)
        frameLayout.addWidget(self.ignoreNotesCheckBox)
        self.moreFrame.setLayout(frameLayout)
        leftLayout = QVBoxLayout()
        leftLayout.addLayout(gridLayout)
        leftLayout.addWidget(self.caseCheckBox)
        leftLayout.addWidget(self.wholeCheckBox)
        leftLayout.addWidget(self.moreFrame)
        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(self.findButton)
        buttonLayout.addWidget(self.replaceButton)
        buttonLayout.addWidget(closeButton)
        buttonLayout.addWidget(self.moreButton)
        buttonLayout.addStretch()
        mainLayout = QHBoxLayout()
        mainLayout.addLayout(leftLayout)
        mainLayout.addWidget(line)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

        self.moreFrame.hide()
        mainLayout.setSizeConstraint(QLayout.SetFixedSize)

        self.moreButton.toggled[bool].connect(self.setvisible)

        self.findLineEdit.textEdited.connect(self.updateUi)
        self.findButton.clicked.connect(self.findClicked)
        self.replaceButton.clicked.connect(self.replaceClicked)

        self.updateUi()
        self.setWindowTitle("Find and Replace")

    def setvisible(self, YN):
        self.moreFrame.setVisible(YN)

    def findClicked(self):
        self.find.emit(self.findLineEdit.text(),
                       self.caseCheckBox.isChecked(),
                       self.wholeCheckBox.isChecked(),
                       self.backwardsCheckBox.isChecked(),
                       self.regexCheckBox.isChecked(),
                       self.ignoreNotesCheckBox.isChecked())

    def replaceClicked(self):
        self.replace.emit(self.findLineEdit.text(),
                          self.replaceLineEdit.text(),
                          self.caseCheckBox.isChecked(),
                          self.wholeCheckBox.isChecked(),
                          self.backwardsCheckBox.isChecked(),
                          self.regexCheckBox.isChecked(),
                          self.ignoreNotesCheckBox.isChecked())

    def updateUi(self):
        enable = self.findLineEdit.text()
        self.findButton.setEnabled(bool(enable))
        self.replaceButton.setEnabled(bool(enable))


if __name__ == "__main__":
    def find(what, *args):
        print("Find {0} {1}".format(what, [x for x in args]))


    def replace(old, new, *args):
        print("Replace {0} with {1} {2}".format(
            old, new, [x for x in args]))


    app = QApplication(sys.argv)
    form = FindAndReplaceDlg()
    form.find.connect(find)
    form.replace.connect(replace)
    form.show()
    app.exec_()