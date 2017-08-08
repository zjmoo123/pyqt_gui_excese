import os
import platform
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import qrc_resources
import newimagedialog

__version__ = "1.0.0"


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.image = QImage()
        self.dirty = False
        self.filename = None
        self.mirroredvertically = False
        self.mirroredhorizontally = False
        self.imageLabel = QLabel()
        self.imageLabel.setMinimumSize(200, 200)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.setCentralWidget(self.imageLabel)
        logDockWidget = QDockWidget("log", self)
        logDockWidget.setObjectName("logdockwidget")
        logDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.listWidget = QListWidget()
        logDockWidget.setWidget(self.listWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, logDockWidget)

        self.printer = None

        self.sizeLabel = QLabel()
        self.sizeLabel.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.addPermanentWidget(self.sizeLabel)
        status.showMessage("Ready", 5000)

        # fileNewAction = QAction(QIcon(":/filenew.png"), "&New...", self)
        # fileNewAction.setShortcut(QKeySequence.New)
        # helpText = "Create a new image"
        # fileNewAction.setToolTip(helpText)
        # fileNewAction.setStatusTip(helpText)
        # fileNewAction.triggered.connect(self.fileNew)
        # fileMenu.addAction(fileNewAction)
        # fileToolbar.addAction(fileNewAction)
        fileNewAction=self.createAction("&New...",  QKeySequence.New, "filenew", "Create an image file")
        fileNewAction.triggered.connect(self.fileNew)
        fileOpenAction = self.createAction("&Open...", "Ctrl+O", "fileopen", "Open an image file")
        fileOpenAction.triggered.connect(self.fileOpen)
        fileSaveAction = self.createAction("&Save",
                                           QKeySequence.Save, "filesave", "Save the image")
        fileSaveAction.triggered.connect(self.fileSave)
        fileSaveAsAction = self.createAction("Save &As...", icon="filesaveas",
                                             tip="Save the image using a new name")
        fileSaveAsAction.triggered.connect(self.fileSaveAs)
        fileQuitAction = self.createAction("&Quit", "Ctrl+Q", "filequit", "Close the application")
        fileQuitAction.triggered.connect(self.close)

        editInvertAction = self.createAction("&Invert", "Ctrl+I", "editinvert",
                                             "Invert the image's colors", True)
        editInvertAction.toggled[bool].connect(self.editInvert)

        editSwapRedAndBlueAction = self.createAction("Sw&ap Red and Blue", "Ctrl+A",
                                                     "editswap", "Swap Red and Blue",True)
        editSwapRedAndBlueAction.toggled[bool].connect(self.editSwapRedAndBlue)
        editZoomAction = self.createAction("&Zoom...", "Alt+Z", "editzoom", "Zoom the image")
        editZoomAction.triggered.connect(self.editZoom)
        mirrorGroup = QActionGroup(self)
        editUnMirrorAction = self.createAction("&Unmirror", "Ctrl+U", "editunmirror",
                                               "UnMirror the image", True)
        editUnMirrorAction.toggled[bool].connect(self.editUnMirror)
        mirrorGroup.addAction(editUnMirrorAction)
        editMirrorHorizontalAction = self.createAction("&Mirror Horizontally", "Ctrl+H",
                                                       "editmirrorhoriz", "MirrorHorizontal the image", True)
        editMirrorHorizontalAction.toggled[bool].connect(self.editMirrorHorizontal)
        mirrorGroup.addAction(editMirrorHorizontalAction)
        editMirrorVerticalAction = self.createAction("&Mirror Vertically", "Ctrl+V",
                                                     "editmirrorvert", "MirrorVertical the image", True)
        editMirrorVerticalAction.toggled[bool].connect(self.editMirrorVertical)
        mirrorGroup.addAction(editMirrorVerticalAction)
        editUnMirrorAction.setChecked(True)

        helpAboutAction = self.createAction("&About Image Changer")
        helpAboutAction.triggered.connect(self.helpAbout)

        self.fileMenu = self.menuBar().addMenu("&Flie")
        self.fileMenuActions = (fileNewAction, fileOpenAction, fileSaveAction, fileSaveAsAction, None, fileQuitAction)
        self.fileMenu.aboutToShow.connect(self.updateFileMenu)

        editMenu = self.menuBar().addMenu("&Edit")
        self.addActions(editMenu, (editInvertAction, editSwapRedAndBlueAction, editZoomAction))
        mirrorMenu = editMenu.addMenu(QIcon(":/editmirror.png"), "&Mirror")
        self.addActions(mirrorMenu, (editUnMirrorAction, editMirrorHorizontalAction, editMirrorVerticalAction))

        helpMenu = self.menuBar().addMenu("&Help")
        self.addActions(helpMenu, (helpAboutAction,))

        fileToolbar = self.addToolBar("File")
        fileToolbar.setObjectName("FileToolBar")
        self.addActions(fileToolbar, (fileNewAction, fileOpenAction, fileSaveAsAction))

        editToolbar = self.addToolBar("Edit")
        editToolbar.setObjectName("EditToolBar")
        self.addActions(editToolbar, (editInvertAction,
                                      editSwapRedAndBlueAction, editUnMirrorAction,
                                      editMirrorVerticalAction, editMirrorHorizontalAction))

        self.zoomSpinBox = QSpinBox()
        self.zoomSpinBox.setRange(1, 400)
        self.zoomSpinBox.setSuffix(" %")
        self.zoomSpinBox.setValue(100)
        self.zoomSpinBox.setToolTip("Zoom the image")
        self.zoomSpinBox.setStatusTip(self.zoomSpinBox.toolTip())
        self.zoomSpinBox.setFocusPolicy(Qt.NoFocus)
        self.zoomSpinBox.valueChanged[int].connect(self.showImage)
        editToolbar.addWidget(self.zoomSpinBox)

        self.addActions(self.imageLabel, (
            editInvertAction, editSwapRedAndBlueAction, editUnMirrorAction, editMirrorVerticalAction,
            editMirrorHorizontalAction))

        # separator = QAction()
        # separator.setSeparator(True)
        # self.addActions(editToolbar,(editInvertAction,editSwapRedAndBlueAction,separator,editUnMirrorAction,editMirrorHorizontalAction,editMirrorVerticalAction))

        self.resetableActions = ((editInvertAction, False),
                                 (editSwapRedAndBlueAction, False),
                                 (editUnMirrorAction, True))
        imageTemp = QImage("D:\\py_workspace\\alert\\sftp2.PNG")
        if imageTemp.isNull():
            message = "Failed to read "
            self.updateStatus(message)
        else:
            self.image = imageTemp
            self.showImage()

            # settings = QSettings()
            # self.recentFiles = settings.value("RecentFiles",type=QProcessEnvironment).toStringList()
            # size = settings.value("MainWindow/Size", QVariant(QSizeF(600, 500))).toSize()
            # self.resize(size)
            # position = settings.value("MainWindow/Position", QVariant(QPointF(0, 0))).toPoint()
            # self.move(position)
            # self.restoreState(settings.value("MainWindow/State",type=QUuid).toByteArray())
            # self.setWindowTitle("Image Changer")
            # self.updateFileMenu()
            # QTimer.singleShot(0, self.loadInitialFile)

    def createAction(self, text, shortcut=None, icon=None,
                     tip=None, checkable=False):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if checkable:
            action.setCheckable(True)
        return action

    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def loadInitialFile(self):
        settings = QSettings()
        fname = settings.value("LastFile").toString()
        if fname and QFile.exists(fname):
            self.loadFile(fname)

    def okToContinue(self):
        if self.dirty:
            reply = QMessageBox.question(self,
                                         "Image Changer = Unsaved Changes",
                                         "Save unsaved changes?",
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.Yes:
                self.fileSave()
        return True

    def updateFileMenu(self):
        self.fileMenu.clear()
        self.addActions(self.fileMenu, self.fileMenuActions[:-1])
        current = self.filename if self.filename is not None else None
        recentFiles = []
        for fname in self.recentFiles:
            if fname != current and QFile.exists(fname):
                recentFiles.append(fname)
        if recentFiles:
            self.fileMenu.addSeparator()
            for i, fname in enumerate(recentFiles):
                action = QAction(QIcon(":/icon.png"), "&%d %s" % (i + 1, QFileInfo(fname).fileName()), self)
                action.setData(QVariant(fname))
                action.triggered.connect(self.loadFile)
                self.fileMenu.addAction(action)
                self.fileMenu.addSeparator()
                self.fileMenu.addAction(self.fileMenuActions[:-1])

    def addRecentFile(self, fname):
        if fname is None:
            return
        if not self.recentFiles.contains(fname):
            self.recentFiles.prepend(fname)
            while self.recentFiles.count() > 9:
                self.recentFiles.takeLast()

    def fileNew(self):
        if not self.okToContinue():
            return
        dialog = newimagedialog.NewImageDlg()
        if dialog.exec_():
            self.addRecentFile(self.filename)
            self.image = QImage()
            for action, check in self.resetableActions:
                action.setChecked(check)
            self.image = dialog.image()
            self.filename = None
            self.dirty = True
            self.showImage()
            self.sizeLabel.setText("%d x %d" % (self.image.width(), self.image.height()))
            self.updateStatus("Create new image")

    def updateStatus(self, message):
        self.statusBar().showMessage(message, 5000)
        self.listWidget.addItem(message)
        if self.filename is not None:
            self.setWindowTitle("Image Changer - %s[*]" % os.path.basename(self.filename))
        elif not self.image.isNull():
            self.setWindowTitle("Image Changer - Unnamed[*]")
        else:
            self.setWindowTitle("Image Changer[*]")
        self.setWindowModified(self.dirty)

    def fileOpen(self):
        if not self.okToContinue():
            return
        dir = os.path.dirname(self.filename) if self.filename is not None else "."
        formats = ["*.%s" % format.lower() for format in QImageReader.supportedImageFormats()]
        fname = QFileDialog.getOpenFileName(self, "%s - Choose Image" % QApplication.applicationName(), dir,
                                            "Image files (%s)" % " ".join(formats))
        if fname:
            self.loadFile(fname)

    def loadFile(self, fname=None):
        if fname is None:
            action = self.sender()
            if isinstance(action, QAction):
                fname = action.data().toString()
                if not self.okToContinue():
                    return
            else:
                return
        if fname:
            self.filename = None
            image = QImage(fname)
        if image.isNull():
            message = "Failed to read %s" % fname
        else:
            self.addRecentFile(fname)
            self.image = QImage()
            for action, check in self.resetableActions:
                action.setChecked(check)
            self.image = image
            self.filename = fname
            self.showImage()
            self.dirty = False
            self.sizeLabel.setText("%d x %d" % (image.width(), image.height()))
            message = "Loaded %s" % os.path.basename(fname)
        self.updateStatus(message)

    def fileSave(self):
        if self.image.isNull():
            return
        if self.filename is None:
            self.fileSaveAs()
        else:
            if self.image.save(self.filename, None):
                self.updateStatus("Saved as %s" % self.filename)
                self.dirty = False
            else:
                self.updateStatus("Failed to save %s" % self.filename)

    def fileSaveAs(self):
        if self.image.isNull():
            return
        fname = self.filename if self.filename is not None else "."
        formats = ["*.%s" % format.lower() for format in QImageWriter.supportedImageFormats()]
        fname = QFileDialog.getSaveFileName(self, "%s - Save Image" % QApplication.applicationName(), fname,
                                            "Image files (%s)" % " ".join(formats))
        if fname:
            if "." not in fname:
                fname += ".png"
            self.addRecentFile(fname)
            self.filename = fname
            self.fileSave()

    def editInvert(self, on):
        if self.image.isNull():
            return
        self.image.invertPixels()
        self.showImage()
        self.dirty = True
        self.updateStatus("Inverted" if on else "Uninverted")

    def editSwapRedAndBlue(self, on):
        if self.image.isNull():
            return
        self.image = self.image.rgbSwapped()
        self.showImage()
        self.dirty = True
        self.updateStatus(("Swapped Red and Blue"
                           if on else "Unswapped Red and Blue"))

    def editMirrorHorizontal(self, on):
        if self.image.isNull():
            return
        self.image = self.image.mirrored(True, False)
        self.showImage()
        self.mirroredhorizontally = not self.mirroredhorizontally
        self.dirty = True
        self.updateStatus(("Mirrored Horizontally"
                           if on else "Unmirrored Horizontally"))

    def editMirrorVertical(self, on):
        if self.image.isNull():
            return
        self.image = self.image.mirrored(False, True)
        self.showImage()
        self.mirroredvertically = not self.mirroredvertically
        self.dirty = True
        self.updateStatus(("Mirrored Vertically"
                           if on else "Unmirrored Vertically"))

    def editUnMirror(self, on):
        if self.image.isNull():
            return
        if self.mirroredhorizontally:
            self.editMirrorHorizontal(False)
        if self.mirroredvertically:
            self.editMirrorVertical(False)

    def editZoom(self):
        if self.image.isNull():
            return
        percent, ok = QInputDialog.getInt(self, "%s - Zoom" % QApplication.applicationName(), "Percent:",
                                          self.zoomSpinBox.value(), 1, 400)
        if ok:
            self.zoomSpinBox.setValue(percent)

    def showImage(self, percent=None):
        if self.image.isNull():
            return
        if percent is None:
            percent = self.zoomSpinBox.value()
        factor = percent / 100.0
        width = self.image.width() * factor
        height = self.image.height() * factor
        image = self.image.scaled(width, height, Qt.KeepAspectRatio)
        self.imageLabel.setPixmap(QPixmap.fromImage(image))

    def helpAbout(self):
        QMessageBox.about(self, "About Image Changer", """<b>Image Changer</b> v {0}
                <p>Copyright &copy; 2008 Qtrac Ltd. 
                All rights reserved.
                <p>This application can be used to perform
                simple image manipulations.
                <p>Python {1} - Qt {2} - PyQt {3} on {4}""".format(__version__, platform.python_version(),
                                                                   QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

        # def helpHelp(self):
        #     form = helpform.HelpForm("index.html", self)
        #     form.show()


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("Qtrac Ltd.")
    app.setOrganizationDomain("qtrac.eu")
    app.setApplicationName("Image Changer")
    app.setWindowIcon(QIcon(":/icon.png"))
    form = MainWindow()
    form.show()
    app.exec_()


main()
