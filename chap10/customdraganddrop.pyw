from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import sys


class DropLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(DropLineEdit, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, QDragEnterEvent):
        if QDragEnterEvent.mimeData().hasFormat("application/x-icon-and-text"):
            QDragEnterEvent.accept()
        else:
            QDragEnterEvent.ignore()

    def dragMoveEvent(self, QDragMoveEvent):
        if QDragMoveEvent.mimeData().hasFormat("application/x-icon-and-text"):
            QDragMoveEvent.setDropAction(Qt.CopyAction)
            QDragMoveEvent.accept()
        else:
            QDragMoveEvent.ignore()

    def dropEvent(self, QDropEvent):
        if QDropEvent.mimeData().hasFormat("application/x-icon-and-text"):
            data = QDropEvent.mimeData().data("application/x-icon-and-text")
            stream = QDataStream(data, QIODevice.ReadOnly)
            text = ""
            # stream >> text
            text = stream.readQString()
            self.setText(text)
            QDropEvent.setDropAction(Qt.CopyAction)
            QDropEvent.accept()
        else:
            QDropEvent.ignore()


class DnDlistWidget(QListWidget):
    def __init__(self, parent=None):
        super(DnDlistWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-icon-and-text"):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-icon-and-text"):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-icon-and-text"):
            data = event.mimeData().data("application/x-icon-and-text")
            stream = QDataStream(data, QIODevice.ReadOnly)
            text = ""
            icon = QIcon()
            # stream >> text >> icon
            text = stream.readQString()
            stream >> icon
            item = QListWidgetItem(text, self)
            item.setIcon(icon)
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def startDrag(self, dropActions):
        item = self.currentItem()
        icon = item.icon()
        data = QByteArray()
        stream = QDataStream(data, QIODevice.WriteOnly)
        # stream << item.text() << icon
        stream.writeQString(item.text())
        stream << icon
        mimeData = QMimeData()
        mimeData.setData("application/x-icon-and-text", data)
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        pixmap = icon.pixmap(24, 24)
        drag.setHotSpot(QPoint(12, 12))
        drag.setPixmap(pixmap)
        if drag.exec(Qt.MoveAction) == Qt.MoveAction:
            self.takeItem(self.row(item))

class DnDMenuListWidget(QListWidget):
    def __init__(self,parent=None):
        super(DnDMenuListWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.dropAction = Qt.CopyAction

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-icon-and-text"):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-icon-and-text"):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, QDropEvent):
        if QDropEvent.mimeData().hasFormat("application/x-icon-and-text"):
            data = QDropEvent.mimeData().data("application/x-icon-and-text")
            stream = QDataStream(data,QIODevice.ReadOnly)
            text = ""
            icon = QIcon()
            text = stream.readQString()
            stream >> icon
            menu = QMenu(self)
            menu.addAction("&Copy",self.setCopyAction)
            menu.addAction("&Move",self.setMoveAction)
            if menu.exec_(QCursor.pos()):
                item = QListWidgetItem(text,self)
                item.setIcon(icon)
                QDropEvent.setDropAction(self.dropAction)
                QDropEvent.accept()
                return
            else:
                QDropEvent.setDropAction(Qt.IgnoreAction)
        QDropEvent.ignore()

    def setCopyAction(self):
        self.dropAction = Qt.CopyAction

    def setMoveAction(self):
        self.dropAction = Qt.MoveAction

    def startDrag(self, dropActions):
        item = self.currentItem()
        icon = item.icon()
        data = QByteArray()
        stream = QDataStream(data, QIODevice.WriteOnly)
        stream.writeQString(item.text())
        stream<<icon
        mimeData = QMimeData()
        mimeData.setData("application/x-icon-and-text", data)
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        pixmap = icon.pixmap(24, 24)
        drag.setHotSpot(QPoint(12, 12))
        drag.setPixmap(pixmap)
        if (drag.exec(Qt.MoveAction|Qt.CopyAction) == Qt.MoveAction):
            self.takeItem(self.row(item))

class DnDCtrlListWidget(QListWidget):
    def __init__(self,parent=None):
        super(DnDCtrlListWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-icon-and-text"):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-icon-and-text"):
            action = Qt.MoveAction
            if event.keyboardModifiers() & Qt.ControlModifier:
                action = Qt.CopyAction
            event.setDropAction(action)
            event.accept()
        else:
            event.ignore()
#结束拖动
    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-icon-and-text"):
            data = event.mimeData().data("application/x-icon-and-text")
            stream = QDataStream(data, QIODevice.ReadOnly)
            text = ""
            icon = QIcon()
            text = stream.readQString()
            stream >> icon
            item = QListWidgetItem(text, self)
            item.setIcon(icon)
            action = Qt.MoveAction
            if event.keyboardModifiers() & Qt.ControlModifier:
                action = Qt.CopyAction
            event.setDropAction(action)
            event.accept()
        else:
            event.ignore()
#开始拖动
    def startDrag(self, dropActions):
        item = self.currentItem()
        icon = item.icon()
        data = QByteArray()
        stream = QDataStream(data, QIODevice.WriteOnly)
        stream.writeQString(item.text())
        stream << icon
        mimeData = QMimeData()
        mimeData.setData("application/x-icon-and-text", data)
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        pixmap = icon.pixmap(24, 24)
        drag.setHotSpot(QPoint(12, 12))
        drag.setPixmap(pixmap)
        if (drag.exec(Qt.MoveAction | Qt.CopyAction) == Qt.MoveAction):
            self.takeItem(self.row(item))

class DnDWidget(QWidget):
    def __init__(self, text, icon=QIcon(), parent=None):
        super(DnDWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.text = text
        self.icon = icon

    def minimumSizeHint(self):
        fm = QFontMetricsF(self.font())
        if self.icon.isNull():
            return QSize(fm.width(self.text), fm.height() * 1.5)
        return QSize(34 + fm.width(self.text), max(34, fm.height() * 1.5))

    def paintEvent(self, event):
        height = QFontMetricsF(self.font()).height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.fillRect(self.rect(), QColor(Qt.yellow).lighter())
        if self.icon.isNull():
            painter.drawText(10, height, self.text)
        else:
            pixmap = self.icon.pixmap(24, 24)
            painter.drawPixmap(0, 5, pixmap)
            painter.drawText(34, height,
                             self.text + " (Drag to or from me!)")

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-icon-and-text"):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-icon-and-text"):
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-icon-and-text"):
            data = event.mimeData().data("application/x-icon-and-text")
            stream = QDataStream(data, QIODevice.ReadOnly)
            self.text = ""
            self.icon = QIcon()
            self.text = stream.readQString()
            stream >> self.icon
            # stream >> self.text >> self.icon
            event.setDropAction(Qt.CopyAction)
            event.accept()
            self.updateGeometry()
            self.update()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        self.startDrag()
        QWidget.mouseMoveEvent(self, event)

    def startDrag(self):
        icon = self.icon
        if icon.isNull():
            return
        data = QByteArray()
        stream = QDataStream(data, QIODevice.WriteOnly)
        # stream << self.text << icon
        stream.writeQString(self.text)
        stream << icon
        mimeData = QMimeData()
        mimeData.setData("application/x-icon-and-text", data)
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        pixmap = icon.pixmap(24, 24)
        drag.setHotSpot(QPoint(12, 12))
        drag.setPixmap(pixmap)
        drag.exec(Qt.CopyAction)


class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        dndListWidget = DnDMenuListWidget()
        path = os.path.dirname(__file__)
        for image in sorted(os.listdir(os.path.join(path, "images"))):
            if image.endswith(".png"):
                item = QListWidgetItem(image.split(".")[0].capitalize())
                item.setIcon(QIcon(os.path.join(path,
                                                "images/{0}".format(image))))
                dndListWidget.addItem(item)
        dndIconListWidget = DnDCtrlListWidget()
        dndIconListWidget.setViewMode(QListWidget.IconMode)
        dndWidget = DnDWidget("Drag to me!")
        dropLineEdit = DropLineEdit()

        layout = QGridLayout()
        layout.addWidget(dndListWidget, 0, 0)
        layout.addWidget(dndIconListWidget, 0, 1)
        layout.addWidget(dndWidget, 1, 0)
        layout.addWidget(dropLineEdit, 1, 1)
        self.setLayout(layout)

        self.setWindowTitle("Custom Drag and Drop")


app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()
