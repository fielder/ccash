#!/bin/env python

import sys

from PyQt4 import QtCore
from PyQt4 import QtGui

#import entries


class MainWin(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent=parent)

        self.setWindowTitle("CCash")
        self.resize(640, 480)
        self.show()


class MainCont(object):
    def __init__(self):
        self._types = []
        self._entries = []

        self._win = MainWin()

    def load(self, path):
#       types, entries = entries.loadFromPath(path)
        pass

    def close(self):
        pass


if __name__ == "__main__":
#   if True:
#       if len(sys.argv) > 1:
#           entries.loadFromPath(sys.argv[1])
#       sys.exit(0)

    app = QtGui.QApplication(sys.argv)
    cont = MainCont()

    if len(sys.argv) > 1:
        cont.load(sys.argv[1])

    sys.exit(app.exec_())
