import bisect
import collections
import sys
from PyQt5.QtCore import (QByteArray, QDataStream, QDate, QIODevice, Qt)
from PyQt5.QtWidgets import (QApplication, QMessageBox, QPushButton)
from PyQt5.QtNetwork import (QHostAddress, QTcpServer, QTcpSocket)

PORT = 9407
SIZEOF_UINT16 = 2
MAX_BOOKINGS_PER_DAY = 5

Bookings = collections.defaultdict(list)


def printBookings():
    for key in sorted(Bookings):
        print(key, Bookings[key])
    print()


class Socket(QTcpSocket):
    def __init__(self, parent=None):
        super(Socket, self).__init__(parent)
        self.readyRead.connect(self.readRequest)
        self.disconnected.connect(self.deleteLater)
        self.nextBlockSize = 0

    def readRequest(self):
        stream = QDataStream(self)
        stream.setVersion(QDataStream.Qt_5_8)
        if self.nextBlockSize == 0:
            if self.bytesAvailable() < SIZEOF_UINT16:
                return
            self.nextBlockSize = stream.readUInt16()
        if self.bytesAvailable() < self.nextBlockSize:
            return

        action = ""
        room = ""
        date = QDate()
        action = stream.readQString()
        if action in ("BOOK", "UNBOOK", "BOOKINGSONDATE",
                      "BOOKINGSFORROOM"):
            room = stream.readQString()
            stream >> date
            bookings = Bookings.get(date.toPyDate())
            uroom = str(room)
        if action == "BOOK":
            if bookings is None:
                bookings = Bookings[date.toPyDate()]
            if len(bookings) < MAX_BOOKINGS_PER_DAY:
                if uroom in bookings:
                    self.sendError("Cannot accept duplicate booking")
                else:
                    bisect.insort(bookings, uroom)
                    self.sendReply(action, room, date)
            else:
                self.sendError("{0} is fully booked".format(date.toString(Qt.ISODate)))
        elif action == "UNBOOK":
            if bookings is None or uroom not in bookings:
                self.sendError("Cannot unbook nonexistent booking")
            else:
                bookings.remove(uroom)
                self.sendReply(action, room, date)
        elif action == "BOOKINGSONDATE":
            bookings = Bookings.get(date.toPyDate())
            if bookings is not None:
                self.sendReply(action, ", ".join(bookings), date)
            else:
                self.sendError("there are no rooms booked on {0}".format(date.toString(Qt.ISODate)))
        elif action == "BOOKINGSFORROOM":
            dates = []
            for date, bookings in Bookings.items():
                if room in bookings:
                    dates.append(date)
            if dates:
                dates.sort()
                reply = QByteArray()
                stream = QDataStream(reply, QIODevice.WriteOnly)
                stream.setVersion(QDataStream.Qt_5_8)
                stream.writeUInt16(0)
                stream.writeQString(action)
                stream.writeQString(room)
                stream.writeInt32(len(dates))
                for date in dates:
                    stream << QDate(date)
                stream.device().seek(0)
                stream.writeUInt16(reply.size() - SIZEOF_UINT16)
                self.write(reply)
            else:
                self.sendError("room {0} is not booked".format(room))
        else:
            self.sendError("Unrecognized request")
        printBookings()

    def sendError(self,msg):
        reply = QByteArray()
        stream = QDataStream(reply,QIODevice.WriteOnly)
        stream.setVersion(QDataStream.Qt_5_7)
        stream.writeUInt16(0)
        stream.writeQString("ERROR")
        stream.writeQString(msg)
        stream.device().seek(0)
        stream.writeUInt16(reply.size() - SIZEOF_UINT16)
        self.write(reply)

    def sendReply(self,action,room,date):
        reply = QByteArray()
        stream = QDataStream(reply,QIODevice.WriteOnly)
        stream.setVersion(QDataStream.Qt_5_7)
        stream.writeUInt16(0)
        stream.writeQString(action)
        stream.writeQString(room)
        stream << date
        stream.device().seek(0)
        stream.writeUInt16(reply.size() - SIZEOF_UINT16)
        self.write(reply)

class TcpServer(QTcpServer):
    def __init__(self,parent=None):
        super(TcpServer, self).__init__(parent)

    def incomingConnection(self, socketId):
        socket = Socket(self)
        socket.setSocketDescriptor(socketId)

class BuildingServicesDlg(QPushButton):
    def __init__(self,parent=None):
        super(BuildingServicesDlg, self).__init__("&Close Server",parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.loadBookings()
        self.tcpServer = TcpServer(self)
        if not self.tcpServer.listen(QHostAddress("0.0.0.0"),PORT):
            QMessageBox.critical(self, "Building Services Server",
                                 "Failed to start server: {0}".format(self.tcpServer.errorString()))
            self.close()
            return

        self.clicked.connect(self.close)
        font = self.font()
        font.setPointSize(24)
        self.setFont(font)
        self.setWindowTitle("Building Services Server")

    def loadBookings(self):
        import random

        today = QDate.currentDate()
        for i in range(10):
            date = today.addDays(random.randint(7,60))
            for j in range(random.randint(1,MAX_BOOKINGS_PER_DAY)):
                floor = random.randint(0,5)
                room = random.randint(1,34)
                bookings = Bookings[date.toPyDate()]
                if len(bookings) >=MAX_BOOKINGS_PER_DAY:
                    continue
                bisect.insort(bookings,"{0:1d}{1:02d}".format(
                              floor, room))
        printBookings()

app = QApplication(sys.argv)
form = BuildingServicesDlg()
form.show()
form.move(0,0)
app.exec_()