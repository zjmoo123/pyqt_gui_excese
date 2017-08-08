import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class PenPropertiesDlg(QDialog):
    def __init__(self,parent=None):
        super(PenPropertiesDlg,self).__init__(parent)
        # self.setAttribute(Qt.WA_DeleteOnClose)
        widthLabel=QLabel("&Width:")
        self.widthSpinBox=QSpinBox()
        widthLabel.setBuddy(self.widthSpinBox)
        self.widthSpinBox.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.widthSpinBox.setRange(0,24)
        self.beveledCheckBox=QCheckBox("&Beveled edges")
        StyleLabel=QLabel("&Style:")
        self.styleComboBox=QComboBox()
        StyleLabel.setBuddy(self.styleComboBox)
        self.styleComboBox.addItems(["Solid","Dashed","Dotted","DashDotted","DashDotted"])
        okButton=QPushButton("&OK")
        cancelButton=QPushButton("Cancel")

        # buttonLayout = QHBoxLayout()
        # buttonLayout.addStretch()
        # buttonLayout.addWidget(okButton)
        # buttonLayout.addWidget(cancelButton)
        buttonBox = QDialogButtonBox()
        buttonBox.setOrientation(Qt.Horizontal)  # 设置为水平方向
        buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)  # 确定
        buttonBox.rejected.connect(self.reject)  # 取消

        layout=QGridLayout()
        layout.addWidget(widthLabel,0,0)
        layout.addWidget(self.widthSpinBox,0,1)
        layout.addWidget(self.beveledCheckBox,0,2)
        layout.addWidget(StyleLabel,1,0)
        layout.addWidget(self.styleComboBox,1,1,1,2)
        # gwg = QWidget()
        # gwg.setLayout(buttonLayout)
        # buttonLayoutWidget=buttonLayout.widget()
        layout.addWidget(buttonBox,2,0,1,3)
        self.setLayout(layout)

        # okButton.clicked.connect(self.accept)
        # cancelButton.clicked.connect(self.reject)
        self.setWindowTitle("Pen Properties")
        # QDialogButtonBox信号槽示例
        # buttonBox = QDialogButtonBox()
        # buttonBox.setOrientation(Qt.Horizontal)  # 设置为水平方向
        # buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        # buttonBox.accepted.connect(self.accept)  # 确定
        # buttonBox.rejected.connect(self.reject)  # 取消

app=QApplication(sys.argv)
dialog=PenPropertiesDlg()
dialog.widthSpinBox.setValue(2)
dialog.beveledCheckBox.setChecked(True)
dialog.styleComboBox.setCurrentIndex(2)
if dialog.exec_():
    print(dialog.widthSpinBox.value())
    print(dialog.beveledCheckBox.isChecked())
    print(dialog.styleComboBox.currentText())
else:
    print(dialog.widthSpinBox.value())
    print(dialog.beveledCheckBox.isChecked())
    print(dialog.styleComboBox.currentText())
