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
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Title","Year","Mins","Acquired","Notes"])
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        selected=None
        for row,movie in enumerate(self.movies):
            item = QTableWidgetItem(movie.title)
            if current is not None and current== id(movie):
                selected = item
            item.setData(Qt.UserRole,QVariant(int(id(movie))))
            self.table.setItem(row,0,item)
            year = movie.year
            if year !=movie.UNKNOWNYEAR:
                item = QTableWidgetItem("%d"%year)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row,1,item)
            minutes = movie.minutes
            if minutes!=movie.UNKNOWNMINUTES:
                item=QTableWidgetItem("%d"%minutes)
                item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                self.table.setItem(row,2,item)
            item=QTableWidgetItem(movie.acquired.toString(moviedata.DATEFORMAT))
            item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
            self.table.setItem(row,3,item)
            notes = movie.notes
            if notes.length()>40:
                notes = notes.left(39)+"..."
            self.table.setItem(row,4,QTableWidgetItem(notes))
            self.table.resizeColumnsToContents()
            if selected is not None:
                selected.setSelected(True)
                self.table.setCurrentItem(selected)
                self.table.scrollToItem(selected)

    def fileNew(self):
        if not self.okToContinue():
            return
        self.movies.clear()
        self.statusBar().clearMessage()
        self.updateTable()

    def fileOpen(self):
        if not self.okToContinue():
            return
        path = QFileInfo(self.movies.filename()).path() if not self.movies.filename().isEmpty() else "."
        fname = QFileDialog.getOpenFileName(self,"My Movies - Load Movie Data",path,"My Movies data files (%s)"%self.movies.formats())
        if not fname.isEmpty():
            ok,msg=self.movies.load(fname)
            self.statusBar().showMessage(msg,5000)
            self.updateTable()

    def fileSave(self):
        if self.movies.filename().isEmpty():
            self.fileSaveAs()
        else:
            ok,msg=self.movies.save()
            self.statusBar().showMessage(msg,5000)

    def fileSaveAs(self):
        fname = (self.movies.filename()
                 if not self.movies.filename().isEmpty() else ".")
        fname = QFileDialog.getSaveFileName(self,
                "My Movies - Save Movie Data", fname,
                "My Movies data files ({0})".format(self.movies.formats()))
        if not fname.isEmpty():
            if not fname.contains("."):
                fname += ".mqb"
            ok, msg = self.movies.save(fname)
            self.statusBar().showMessage(msg, 5000)
            return ok
        return False

    def fileImportBOM(self):
        self.fileImport("dom")
    def fileImportSAX(self):
        self.fileImport("sax")

    def fileImport(self,format):
        if not self.okToContinue():
            return
        path = QFileInfo(self.movies.filename()).path() if not self.movies.filename().isEmpty() else "."
        fname = QFileDialog.getOpenFileName(self,"My Movies - Import Movie Data",path,"My Movies XML files (*.xml)")
        if not fname.isEmpty():
            if format == "dom":
                ok,msg = self.movies.importDOM(fname)
            else:
                ok,msg = self.movies.importSAX(fname)
            self.statusBar().shoeMessage(msg,5000)
            self.updateTable()

    def fileExportXml(self):
        fname = self.movies.filename()
        if fname.isEmpty():
            fname ="."
        else:
            i = fname.lastIndexOf(".")
            if i>0:
                fname = fname.left(i)
            fname+=".xml"
        fname = QFileDialog.getSaveFileName(self,"My Movies - Export Movie Data",fname,"My Movies XML files (*.xml)")
        if not fname.isEmpty():
            if not fname.contains("."):
                fname+=".xml"
            ok,msg = self.movies.exportXml(fname)
            self.statusBar().showMessage(msg,5000)



    def okToContinue(self):
        if self.movies.isDirty():
            reply = QMessageBox.question(self,
                                         "Image Changer - Unsaved Changes",
                                         "Save unsaved changes?",
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.Yes:
                return self.fileSave()
        return True


