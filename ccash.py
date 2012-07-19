#!/usr/bin/env python

import sys
import collections

from PyQt4 import QtCore
from PyQt4 import QtGui

import cfile


class TypesDockWidget(QtGui.QWidget):
    typesDeleted = QtCore.pyqtSignal(list)

    def __init__(self):
        super(TypesDockWidget, self).__init__()

        self.table = None

        # Types table
        self.table = QtGui.QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Name", "Regex"])
        self.table.setAlternatingRowColors(True)

        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        a = QtGui.QAction("&New", self)
        self.addAction(a)
        a.triggered.connect(self._addNewEmptyType)
        a = QtGui.QAction("&Delete", self)
        self.addAction(a)
        a.triggered.connect(self._deleteSelectedRows)

        # Button
        hbox = QtGui.QHBoxLayout()
        b = QtGui.QPushButton("New")
        b.clicked.connect(self._addNewEmptyType)
        b.setToolTip("Create a new entry type")
        hbox.addWidget(b)
        hbox.addStretch()

        # Main layout
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(QtGui.QLabel("Types"))
        vbox.addWidget(self.table)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def _appendRow(self, typename, regex):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setVerticalHeaderItem(row, QtGui.QTableWidgetItem())
        self.table.setItem(row, 0, QtGui.QTableWidgetItem(typename))
        self.table.setItem(row, 1, QtGui.QTableWidgetItem(regex))

    def _addNewEmptyType(self):
        self._appendRow("", "")

    def _deleteSelectedRows(self):
        selected_rows = [wi.row() for wi in self.table.selectedItems()]

        removed_typenames = []

        while selected_rows:
            # Note that we take off the end of the list. If we removed
            # indices from the beginning of the list, we'd have to
            # decrement higher indices as those rows would shift up.
            row = selected_rows.pop()

            removed_typenames.append(str(self.table.item(row, 0).text()))

            self.table.removeRow(row)

        if removed_typenames:
            self.typesDeleted.emit(removed_typenames)

    @property
    def types(self):
        ret = collections.OrderedDict()

        for row in xrange(self.table.rowCount()):
            name = str(self.table.item(row, 0).text()).strip()
            regex = str(self.table.item(row, 1).text()).strip()

            if name:
                ret[name] = regex

        return ret

    def populate(self, types):
        self.table.clear()

        for name, regex in types.iteritems():
            self._appendRow(name, regex)


class TypesDockController(QtCore.QObject):
    typesDeleted = QtCore.pyqtSignal(list)

    def __init__(self):
        super(TypesDockController, self).__init__()

        self.dock = QtGui.QDockWidget()
        self.dock.setWidget(TypesDockWidget())
        self.dock.widget().typesDeleted.connect(self.typesDeleted.emit)

    @property
    def types(self):
        return self.dock.widget().types

    def populate(self, types):
        self.dock.widget().populate(types)


class TableController(QtCore.QObject):
    def __init__(self):
        super(TableController, self).__init__()

        self.table = QtGui.QTableWidget()

    def _columnIndexForLabel(self, label):
        col_titles = [str(self.table.horizontalHeaderItem(col).text()) for col in xrange(self.table.columnCount())]
        return col_titles.index(label)

    def populate(self, entries):
        while self.table.columnCount() > 0:
            self.table.removeColumn(0)
        while self.table.rowCount() > 0:
            self.table.removeRow(0)

        if entries:
            for idx, attr in enumerate(entries[0].ATTRIBUTES):
                self.table.insertColumn(idx)
                self.table.setHorizontalHeaderItem(idx, QtGui.QTableWidgetItem(attr))

        for e in entries:
            row = self.table.rowCount()
            self.table.insertRow(row)
            #TODO: ...
#           self.table.setItem(row, 0, QtGui.QTableWidgetItem(typename))
#           self.table.setItem(row, 1, QtGui.QTableWidgetItem(regex))


class MainWin(QtGui.QMainWindow):
    newFile = QtCore.pyqtSignal()
    openFile = QtCore.pyqtSignal()
    closeFile = QtCore.pyqtSignal()
    saveFile = QtCore.pyqtSignal()
    saveFileAs = QtCore.pyqtSignal()
    addEntries = QtCore.pyqtSignal()

    def __init__(self, table, dock):
        super(MainWin, self).__init__()

        # Main table
        self.setCentralWidget(table)

        # Dock
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

        # Menus
        m = self.menuBar().addMenu("&File")
        a = m.addAction("&New")
        a.triggered.connect(self.newFile.emit)
        a = m.addAction("&Open")
        a.triggered.connect(self.openFile.emit)
        a = m.addAction("&Close")
        a.triggered.connect(self.closeFile.emit)
        m.addSeparator()
        a = m.addAction("&Save")
        a.triggered.connect(self.saveFile.emit)
        a = m.addAction("Save &As...")
        a.triggered.connect(self.saveFileAs.emit)
        m.addSeparator()
        a = m.addAction("E&xit")
        a.triggered.connect(self.close)

        m = self.menuBar().addMenu("&Edit")
        a = m.addAction("&Add Entries")
        a.triggered.connect(self.addEntries.emit)

        m = self.menuBar().addMenu("&View")
        a = m.addAction("&Types")
        a.triggered.connect(dock.show)

        # Window stuff
        self.setWindowTitle("CCash")
        self.resize(800, 600)
        self.show()


class MainCont(object):
    def __init__(self):
        # Main table controller
        self.table_cont = TableController()

        # Types dock controller
        self.types_cont = TypesDockController()
        self.types_cont.typesDeleted.connect(self._typesDeleted)

        # Main window signals
        self._win = MainWin(self.table_cont.table, self.types_cont.dock)
        self._win.newFile.connect(self._newFile)
        self._win.openFile.connect(self._openFile)
        self._win.closeFile.connect(self._closeFile)
        self._win.saveFile.connect(self._saveFile)
        self._win.saveFileAs.connect(self._saveFileAs)
        self._win.addEntries.connect(self._addEntries)

    def _resetUI(self):
        self.table_cont.populate([])
        self.types_cont.populate({})

    def _typesDeleted(self, typenames):
        #TODO: unset entry types that had their type deleted
        pass

    def load(self, path):
        types, entries = cfile.loadFromFile(path)

        self._resetUI()

        self.table_cont.populate(entries)
        self.types_cont.populate(types)

    def _confirmIfChanges(self):
        #TODO: prompt if the user has made changes
        return True

    def _newFile(self):
        if not self._confirmIfChanges():
            return

        self._resetUI()

    def _openFile(self):
        if not self._confirmIfChanges():
            return

        #TODO: get the path
        #TODO: if cancel, return

        self.load(path)

    def _closeFile(self):
        if not self._confirmIfChanges():
            return

        self._resetUI()

    def _saveFile(self):
        #TODO: ...
        pass

    def _saveFileAs(self):
        #TODO: ...
        pass

    def _addEntries(self):
        #TODO: ...
        pass


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    cont = MainCont()

    if len(sys.argv) > 1:
        cont.load(sys.argv[1])

    sys.exit(app.exec_())
