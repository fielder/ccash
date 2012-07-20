#!/usr/bin/env python

import sys
import collections

from PyQt4 import QtCore
from PyQt4 import QtGui

import cfile


class TypesDockWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(TypesDockWidget, self).__init__(parent=parent)

        self.table = None

        # Types table
        self.table = QtGui.QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Name", "Regex"])

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(QtGui.QPushButton("New"))
        hbox.addStretch()

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(QtGui.QLabel("Types"))
        vbox.addWidget(self.table)
        vbox.addLayout(hbox)
        self.setLayout(vbox)


class MainWin(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent=parent)

        self.table = None

        # Dock
        self._dock = QtGui.QDockWidget()
        self._dock.setWidget(TypesDockWidget())
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self._dock)

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
        a.triggered.connect(self._dock.show)

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
