#!/usr/bin/env python

import sys
import collections

from PyQt4 import QtCore
from PyQt4 import QtGui

import cfile


class TypesDockWidget(QtGui.QWidget):
    typesDeleted = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        super(TypesDockWidget, self).__init__(parent=parent)

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


class TypesDockController(object):
    def __init__(self):
        self.dock = QtGui.QDockWidget()

        self.dock.setWidget(TypesDockWidget())
        self.dock.widget().typesDeleted.connect(self._typesDeleted)

    @property
    def types(self):
        return self.dock.widget().types

    def _typesDeleted(self, typenames):
#       print typenames
#       print self.types
        pass


class MainWin(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent=parent)

        self.table = None
        self.dock_cont = None

        # Dock
        self.dock_cont = TypesDockController()
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_cont.dock)

        # Main table
        self.table = QtGui.QTableWidget(2, 2)
        self.setCentralWidget(self.table)

        # Menus
        m = self.menuBar().addMenu("&File")
        a = m.addAction("&New")
        a = m.addAction("&Close")
        m.addSeparator()
        a = m.addAction("&Save")
        a = m.addAction("Save &As...")
        m.addSeparator()
        a = m.addAction("E&xit")
        a.triggered.connect(self.close)

        m = self.menuBar().addMenu("&Edit")

        m = self.menuBar().addMenu("&View")
        a = m.addAction("&Types")
        a.triggered.connect(self.dock_cont.dock.show)

        self.setWindowTitle("CCash")
        self.resize(640, 480)
        self.show()


class MainCont(object):
    def __init__(self):
        self._types = collections.OrderedDict()
        self._entries = []

        self._win = MainWin()

    def load(self, path):
        types, entries = cfile.loadFromFile(path)

        self.close()

        self._types = types
        self._entries = entries

        self._populateGUI()

    def close(self):
        self._types.clear()
        self._entries = []

        self._teardownGUI()

    def _teardownGUI(self):
        pass

    def _populateGUI(self):
        pass


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    cont = MainCont()

    if len(sys.argv) > 1:
        cont.load(sys.argv[1])

    sys.exit(app.exec_())
