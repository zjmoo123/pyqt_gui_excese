from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Widget(QWidget):
    def __init__(self,parent =None):
        super(Widget, self).__init__(parent)
        self.justDoubleClicked =False
        self.key = ""
        self.text = ""
        self.message = ""

    def paintEvent(self,event):
        text = self.text
        i = text.index("\n\n")
        if i>=0:
            text = text[:i]
        if not self.key.strip()==0:
            text +="\n\nYou pressed: %s" % self.key
        painter = QPainter(self)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.drawText(self.rect(),Qt.AlignCenter,text)
        if self.message:
            painter.drawText(self.rect(),Qt.AlignBottom|Qt.AlignHCenter,self.message)
            QTimer.singleShot(5000,self.message.clear)
            QTimer.singleShot(5000,self.update)


    def resizeEvent(self, QResizeEvent):
        self.text = "Resized to QSize(%d %d)" % (QResizeEvent.size().width(),QResizeEvent.size().height())
        self.update()

    def keyPressEvent(self, QKeyEvent):
        self.key = ""
        if QKeyEvent.key() ==Qt.Key_Home:
            self.key = "home"
        elif QKeyEvent.key() == Qt.Key_PageUp:
            if QKeyEvent.modifiers() & Qt.ControlModifier:
                self.key = "Ctrl+PageUp"
            else:
                self.key = "PageUp"
        elif QKeyEvent.key() == Qt.Key_PageDown:
            if QKeyEvent.modifiers() & Qt.ControlModifier:
                self.key = "Ctrl+PageDown"
            else:
                self.key = "PageDown"
        elif Qt.Key_A <= QKeyEvent.key() <= Qt.Key_Z:
            if QKeyEvent.modifiers() & Qt.ShiftModifier:
                self.key = "Shift"
            self.key += "Shift+"
        if self.key:
            self.key = self.key
            self.update()
        else:
            QWidget.keyPressEvent(self,QKeyEvent)

    def mouseDoubleClickEvent(self, QMouseEvent):
        self.justDoubleClicked = True
        self.text="Double-clicked."
        self.update()

    def mouseReleaseEvent(self, QMouseEvent):
        if self.justDoubleClicked:
            self.justDoubleClicked=False
        else:
            self.setMouseTracking(not self.hasMouseTracking())
            if self.hasMouseTracking():
                self.text = "Mouse tracking is on.\n" \
                        "Try moving the mouse!\n" \
                        "Single click to switch it off"
            else:
                self.text = "Mouse tracking is off.\n"\
                                           "Single click to switch it on"
            self.update()

    def mouseMoveEvent(self, QMouseEvent):
        if not self.justDoubleClicked:
            globalPos = self,mapToGlobal(QMouseEvent.pos())
            self.text = "The mouse is at\nQPoint({0}, {1}) "\
                    "in widget coords, and\n"\
                    "QPoint({2}, {3}) in screen coords".format(
                        QMouseEvent.pos().x(), QMouseEvent.pos().y(), globalPos.x(),
                    globalPos.y())

            self.update()

    def event(self, QEvent):
        if QEvent.type() == QEvent.keyPress and QEvent.key() == Qt.Key_Tab:
            self.key = "tab caputred in event()"
            self.update()
            return True
        return QWidget.event(self,QEvent)

