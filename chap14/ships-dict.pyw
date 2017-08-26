#!/usr/bin/env python3

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from chap14 import ships
import re
MAC = True
try:
    from PyQt5.QtGui import qt_mac_set_native_menubar
except ImportError:
    MAC = False


class MainForm(QDialog):
    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)

        listLabel = QLabel("&List")
        self.listWidget = QListWidget()
        listLabel.setBuddy(self.listWidget)

        tableLabel = QLabel("&Table")
        self.tableWidget = QTableWidget()
        tableLabel.setBuddy(self.tableWidget)

        treeLabel = QLabel("Tre&e")
        self.treeWidget = QTreeWidget()
        treeLabel.setBuddy(self.treeWidget)

        addShipButton = QPushButton("&Add Ship")
        removeShipButton = QPushButton("&Remove Ship")
        quitButton = QPushButton("&Quit")
        if not MAC:
            addShipButton.setFocusPolicy(Qt.NoFocus)
            removeShipButton.setFocusPolicy(Qt.NoFocus)
            quitButton.setFocusPolicy(Qt.NoFocus)

        splitter = QSplitter(Qt.Horizontal)
        vbox = QVBoxLayout()
        vbox.addWidget(listLabel)
        vbox.addWidget(self.listWidget)
        widget = QWidget()
        widget.setLayout(vbox)
        splitter.addWidget(widget)
        vbox = QVBoxLayout()
        vbox.addWidget(tableLabel)
        vbox.addWidget(self.tableWidget)
        widget = QWidget()
        widget.setLayout(vbox)
        splitter.addWidget(widget)
        vbox = QVBoxLayout()
        vbox.addWidget(treeLabel)
        vbox.addWidget(self.treeWidget)
        widget = QWidget()
        widget.setLayout(vbox)
        splitter.addWidget(widget)
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(addShipButton)
        buttonLayout.addWidget(removeShipButton)
        buttonLayout.addStretch()
        buttonLayout.addWidget(quitButton)
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

        self.tableWidget.itemChanged[QTableWidgetItem].connect(self.tableItemChanged)
        addShipButton.clicked.connect(self.addShip)
        removeShipButton.clicked.connect(self.removeShip)
        quitButton.clicked.connect(self.accept)

        self.ships = ships.ShipContainer("ships.dat")
        self.setWindowTitle("Ships (dict)")
        QTimer.singleShot(0, self.initialLoad)

    def initialLoad(self):
        if not QFile.exists(self.ships.filename):
            for ship in ships.generateFakeShips():
                self.ships.addShip(ship)
            self.ships.dirty = False
        else:
            try:
                self.ships.load()
            except IOError as e:
                QMessageBox.warning(self, "Ships - Error",
                                    "Failed to load: {0}".format(e))
        self.populateList()
        self.populateTable()
        self.tableWidget.sortItems(0)
        self.populateTree()

    def reject(self):
        self.accept()

    def accept(self):
        if (self.ships.dirty and
                    QMessageBox.question(self, "Ships - Save?",
                                         "Save unsaved changes?",
                                         QMessageBox.Yes | QMessageBox.No) ==
                    QMessageBox.Yes):
            try:
                self.ships.save()
            except IOError as e:
                QMessageBox.warning(self, "Ships - Error",
                                    "Failed to save: {0}".format(e))
        QDialog.accept(self)

    def populateList(self, selectedShip=None):
        selected = None
        self.listWidget.clear()
        for ship in self.ships.inOrder():
            item = QListWidgetItem("{0} of {1}/{2} ({3:,})".format(ship.name, ship.owner, ship.country, int(ship.teu)))
            self.listWidget.addItem(item)
            if selectedShip is not None and selectedShip == id(ship):
                selected = item
        if selected is not None:
            selected.setSelected(True)
            self.listWidget.setCurrentItem(selected)

    def populateTable(self, selectedShip=None):
        selected = None
        self.tableWidget.clear()
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.setRowCount(len(self.ships))
        headers = ["Name", "Owner", "Country", "Description", "TEU"]
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        for row, ship in enumerate(self.ships):
            item = QTableWidgetItem(ship.name)
            item.setData(Qt.UserRole, id(ship))
            if selectedShip is not None and selectedShip == id(ship):
                selected = item
            self.tableWidget.setItem(row, ships.NAME, item)
            self.tableWidget.setItem(row, ships.OWNER, QTableWidgetItem(ship.owner))
            self.tableWidget.setItem(row, ships.COUNTRY, QTableWidgetItem(ship.country))
            self.tableWidget.setItem(row, ships.DESCRIPTION, QTableWidgetItem(ship.description))
            item = QTableWidgetItem("{0:>8}".format(ship.teu))
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tableWidget.setItem(row, ships.TEU, item)
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.resizeColumnsToContents()
        if selected is not None:
            selected.setSelected(True)
            self.tableWidget.setCurrentItem(selected)

    def populateTree(self, selectedShip=None):
        selected = None
        self.treeWidget.clear()
        self.treeWidget.setColumnCount(2)
        self.treeWidget.setHeaderLabels(["Country/Owner/Name", "TEU"])
        self.treeWidget.setItemsExpandable(True)
        parentFromCountry = {}
        parentFromCountryOwner = {}
        for ship in self.ships.inCountryOwnerOrder():
            ancestor = parentFromCountry.get(ship.country)
            if ancestor is None:
                ancestor = QTreeWidgetItem(self.treeWidget, [ship.country])
                parentFromCountry[ship.country] = ancestor
            countryowner = ship.country + "/" + ship.owner
            parent = parentFromCountryOwner.get(countryowner)
            if parent is None:
                parent = QTreeWidgetItem(ancestor, [ship.owner])
                parentFromCountryOwner[countryowner] = parent
            item = QTreeWidgetItem(parent, [ship.name, "{0}".format(ship.teu)])
            item.setTextAlignment(1, Qt.AlignRight | Qt.AlignVCenter)
            if selectedShip is not None and selectedShip == id(ship):
                selected = item
            self.treeWidget.expandItem(parent)
            self.treeWidget.expandItem(ancestor)
        self.treeWidget.resizeColumnToContents(0)
        self.treeWidget.resizeColumnToContents(1)
        if selected is not None:
            selected.setSelected(True)
            self.treeWidget.setCurrentItem(selected)
        print(parentFromCountry)
        print(parentFromCountryOwner)

    def addShip(self):
        ship = ships.Ship("Unknown", "Unknown", "Unknown")
        self.ships.addShip(ship)
        self.populateList(id(ship))
        self.populateTree(id(ship))
        self.populateTable(id(ship))
        self.tableWidget.setFocus()
        self.tableWidget.editItem(self.tableWidget.currentItem())

    def tableItemChanged(self, item):
        ship = self.currentTableShip()
        if ship is None:
            return
        column = self.tableWidget.currentColumn()
        if column == ships.NAME:
            ship.name = item.text().strip()
        elif column == ships.OWNER:
            ship.owner = item.text().strip()
        elif column == ships.COUNTRY:
            ship.country = item.text().strip()
        elif column == ships.DESCRIPTION:
            ship.description = item.text().strip()
        elif column == ships.TEU:
            ship.teu = item.text()
        self.ships.dirty = True
        self.populateList(id(ship))
        self.populateTree(id(ship))

    def currentTableShip(self):
        item = self.tableWidget.item(self.tableWidget.currentRow(), 0)
        if item is None:
            return None
        return self.ships.ship(item.data(Qt.UserRole))

    def removeShip(self):
        ship = self.currentTableShip()
        if ship is None:
            return
        if (QMessageBox.question(self, "Ships - Remove",
                                 "Remove {0} of {1}/{2}?".format(ship.name, ship.owner, ship.country),
                                 QMessageBox.Yes | QMessageBox.No) ==
                QMessageBox.No):
            return
        self.ships.removeShip(ship)
        self.populateList()
        self.populateTree()
        self.populateTable()


class MainForm2(QDialog):
    def __init__(self,parent=None):
        super(MainForm2, self).__init__(parent)
        self.model = ships.ShipTableModel("ships.dat")
        tableLabel1 = QLabel("Table &1")
        self.tableView1 = QTableView()
        tableLabel1.setBuddy(self.tableView1)
        self.tableView1.setModel(self.model)
        tableLabel2 = QLabel("Table &2")
        self.tableView2 = QTableView()
        tableLabel2.setBuddy(self.tableView2)
        self.tableView2.setModel(self.model)

        addShipButton = QPushButton("&Add Ship")
        removeShipButton = QPushButton("&Remove Ship")
        quitButton = QPushButton("&Quit")
        if not MAC:
            addShipButton.setFocusPolicy(Qt.NoFocus)
            removeShipButton.setFocusPolicy(Qt.NoFocus)
            quitButton.setFocusPolicy(Qt.NoFocus)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(addShipButton)
        buttonLayout.addWidget(removeShipButton)
        buttonLayout.addStretch()
        buttonLayout.addWidget(quitButton)
        splitter = QSplitter(Qt.Horizontal)
        vbox = QVBoxLayout()
        vbox.addWidget(tableLabel1)
        vbox.addWidget(self.tableView1)
        widget = QWidget()
        widget.setLayout(vbox)
        splitter.addWidget(widget)
        vbox = QVBoxLayout()
        vbox.addWidget(tableLabel2)
        vbox.addWidget(self.tableView2)
        widget = QWidget()
        widget.setLayout(vbox)
        splitter.addWidget(widget)
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

        for tableView in (self.tableView1,self.tableView2):
            header = tableView.horizontalHeader()
            header.sectionClicked[int].connect(self.sortTable)
        addShipButton.clicked.connect(self.addShip)
        removeShipButton.clicked.connect(self.removeShip)
        quitButton.clicked.connect(self.accept)

        self.setWindowTitle("Ships (model)")
        QTimer.singleShot(0,self.initialLoad)

    def initialLoad(self):
        if not QFile.exists(self.model.filename):
            self.model.beginResetModel()
            for ship in ships.generateFakeShips():
                self.model.ships.append(ship)
                self.model.owners.add(str(ship.owner))
                self.model.countries.add(str(ship.country))
            self.model.endResetModel()
            self.model.dirty=False
        else:
            try:
                self.model.load()
            except IOError as e:
                QMessageBox.warning(self,"Ships - Error","Failed to load:{0}".format(e))
        self.model.sortByName()
        self.resizeColumns()

    def resizeColumns(self):
        for tableView in (self.tableView1,self.tableView2):
            for column in (ships.NAME,ships.OWNER,ships.COUNTRY,ships.TEU):
                tableView.resizeColumnToContents(column)

    def reject(self):
        self.accept()

    def accept(self):
        if (self.model.dirty and
                    QMessageBox.question(self, "Ships - Save?",
                                         "Save unsaved changes?",
                                         QMessageBox.Yes | QMessageBox.No) ==
                    QMessageBox.Yes):
            try:
                self.model.save()
            except IOError as e:
                QMessageBox.warning(self, "Ships - Error",
                                    "Failed to save: {0}".format(e))
        QDialog.accept(self)

    def sortTable(self,section):
        if section in (ships.OWNER,ships.COUNTRY):
            self.model.sortByCountryOwner()
        else:
            self.model.sortByName()
        self.resizeColumns()

    def addShip(self):
        row = self.model.rowCount()
        self.model.insertRows(row)
        index = self.model.index(row,0)
        tableView = self.tableView1
        if self.tableView2.hasFocus():
            tableView=self.tableView2
        tableView.setFocus()
        tableView.setCurrentIndex(index)
        tableView.edit(index)

    def removeShip(self):
        tableView=self.tableView1
        if self.tableView2.hasFocus():
            tableView=self.tableView2
        index = tableView.currentIndex()
        if not index.isValid():
            return
        row = index.row()
        name = self.model.data(self.model.index(row,ships.NAME))
        owner = self.model.data(self.model.index(row,ships.OWNER))
        country=self.model.data(self.model.index(row,ships.COUNTRY))
        if (QMessageBox.question(self,"Ships - Remove","Remove {0} of {1}/{2}?".format(name,owner,country),
                                 QMessageBox.Yes|QMessageBox.No)==QMessageBox.No):
            return
        self.model.removeRows(row)
        self.resizeColumns()


class MainForm3(QDialog):
    def __init__(self,parent=None):
        super(MainForm3, self).__init__(parent)
        self.model = ships.ShipTableModel("ships.dat")
        tableLabel1 = QLabel("Table &1")
        self.tableView1 = QTableView()
        tableLabel1.setBuddy(self.tableView1)
        self.tableView1.setModel(self.model)
        self.tableView1.setItemDelegate(ships.ShipDelegate(self))
        tableLabel2 = QLabel("Table &2")
        self.tableView2 = QTableView()
        tableLabel2.setBuddy(self.tableView2)
        self.tableView2.setModel(self.model)
        self.tableView2.setItemDelegate(ships.ShipDelegate(self))

        addShipButton = QPushButton("&Add Ship")
        removeShipButton = QPushButton("&Remove Ship")
        exportButton = QPushButton("E&xport...")
        quitButton = QPushButton("&Quit")
        if not MAC:
            addShipButton.setFocusPolicy(Qt.NoFocus)
            removeShipButton.setFocusPolicy(Qt.NoFocus)
            exportButton.setFocusPolicy(Qt.NoFocus)
            quitButton.setFocusPolicy(Qt.NoFocus)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(addShipButton)
        buttonLayout.addWidget(removeShipButton)
        buttonLayout.addWidget(exportButton)
        buttonLayout.addStretch()
        buttonLayout.addWidget(quitButton)
        splitter = QSplitter(Qt.Horizontal)
        vbox = QVBoxLayout()
        vbox.addWidget(tableLabel1)
        vbox.addWidget(self.tableView1)
        widget = QWidget()
        widget.setLayout(vbox)
        splitter.addWidget(widget)
        vbox = QVBoxLayout()
        vbox.addWidget(tableLabel2)
        vbox.addWidget(self.tableView2)
        widget = QWidget()
        widget.setLayout(vbox)
        splitter.addWidget(widget)
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

        for tableView in (self.tableView1, self.tableView2):
            header = tableView.horizontalHeader()
            header.sectionClicked[int].connect(self.sortTable)

        addShipButton.clicked.connect(self.addShip)
        removeShipButton.clicked.connect(self.removeShip)
        exportButton.clicked.connect(self.export)
        quitButton.clicked.connect(self.accept)

        self.setWindowTitle("Ships (delegate)")
        QTimer.singleShot(0, self.initialLoad)

    def initialLoad(self):
        if not QFile.exists(self.model.filename):
            self.model.beginResetModel()
            for ship in ships.generateFakeShips():
                self.model.ships.append(ship)
                self.model.owners.add(str(ship.owner))
                self.model.countries.add(str(ship.country))
            self.model.endResetModel()
            self.model.dirty = False
        else:
            try:
                self.model.load()
            except IOError as e:
                QMessageBox.warning(self, "Ships - Error",
                                    "Failed to load: {0}".format(e))
        self.model.sortByName()
        self.resizeColumns()

    def resizeColumns(self):
        self.tableView1.resizeColumnsToContents()
        self.tableView2.resizeColumnsToContents()

    def reject(self):
        self.accept()

    def accept(self):
        if (self.model.dirty and
                    QMessageBox.question(self, "Ships - Save?",
                                         "Save unsaved changes?",
                                         QMessageBox.Yes | QMessageBox.No) ==
                    QMessageBox.Yes):
            try:
                self.model.save()
            except IOError as e:
                QMessageBox.warning(self, "Ships - Error",
                                    "Failed to save: {0}".format(e))
        QDialog.accept(self)

    def sortTable(self, section):
        if section in (ships.OWNER, ships.COUNTRY):
            self.model.sortByCountryOwner()
        elif section == ships.TEU:
            self.model.sortByTEU()
        else:
            self.model.sortByName()
        self.resizeColumns()

    def addShip(self):
        row = self.model.rowCount()
        self.model.insertRows(row)
        index = self.model.index(row, 0)
        tableView = self.tableView1
        if self.tableView2.hasFocus():
            tableView = self.tableView2
        tableView.setFocus()
        tableView.setCurrentIndex(index)
        tableView.edit(index)

    def removeShip(self):
        tableView = self.tableView1
        if self.tableView2.hasFocus():
            tableView = self.tableView2
        index = tableView.currentIndex()
        if not index.isValid():
            return
        row = index.row()
        name = self.model.data(
            self.model.index(row, ships.NAME))
        owner = self.model.data(
            self.model.index(row, ships.OWNER))
        country = self.model.data(
            self.model.index(row, ships.COUNTRY))
        if (QMessageBox.question(self, "Ships - Remove",
                                 "Remove {0} of {1}/{2}?".format(name, owner, country),
                                 QMessageBox.Yes | QMessageBox.No) ==
                QMessageBox.No):
            return
        self.model.removeRows(row)
        self.resizeColumns()

    def export(self):
        filename = str(QFileDialog.getSaveFileName(self,
                                                   "Ships - Choose Export File", ".", "Export files (*.txt)")[0])
        if not filename:
            return
        # htmlTags = QRegExp(r"<[^>]+>")
        htmlTags = "<[^>]+>"
        # htmlTags.setMinimal(True)
        nonDigits = "[., ]"
        self.model.sortByCountryOwner()
        fh = None
        try:
            fh = QFile(filename)
            if not fh.open(QIODevice.WriteOnly):
                raise IOError(str(fh.errorString()))
            stream = QTextStream(fh)
            stream.setCodec("UTF-8")
            for row in range(self.model.rowCount()):
                name = self.model.data(
                    self.model.index(row, ships.NAME))
                owner = self.model.data(
                    self.model.index(row, ships.OWNER))
                country = self.model.data(
                    self.model.index(row, ships.COUNTRY))
                teu = self.model.data(
                    self.model.index(row, ships.TEU))
                teu = re.sub(nonDigits, "", teu)
                description = self.model.data(
                    (self.model.index(row, ships.DESCRIPTION)))
                description = re.sub(htmlTags, "", description)
                stream << name << "|" << owner << "|" << country \
                << "|" << str(teu) << "|" << description << "\n"
        except EnvironmentError as e:
            QMessageBox.warning(self, "Ships - Error",
                                "Failed to export: {0}".format(e))
        finally:
            if fh:
                fh.close()
        QMessageBox.warning(self, "Ships - Export",
                            "Successfully exported ship to {0}".format(filename))

app = QApplication(sys.argv)
form = MainForm3()
form.show()
app.exec_()
