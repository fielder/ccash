#!/usr/bin/env python

import sys
import os
import collections

from PyQt4 import QtCore
from PyQt4 import QtGui

import cfile
import centry
import qfx
import charts

#TODO: when an entry's type is edited, check it is valid, or maybe just highlight red if invalid
#TODO: allow columns to be reordered
#TODO: search bar to jump to an entry row
#TODO: when an entry changes, update charts
#TODO: ensure user-modified type names are valid and not duplicated
#TODO: allow all charts to show data from only a range of entries
#TODO: toolbar allowing user to open a chart w/ selected entries
#TODO: right-click context menu on entries to open charts


class TypesDockWidget(QtGui.QWidget):
    typesDeleted = QtCore.pyqtSignal(list)
    typifyAll = QtCore.pyqtSignal()

    def __init__(self):
        super(TypesDockWidget, self).__init__()

        self.table = None

        # Types table
        self.table = QtGui.QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Name", "Regex"])

        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        a = QtGui.QAction("&New", self)
        self.addAction(a)
        a.triggered.connect(self._addNewEmptyType)
        a = QtGui.QAction("&Delete", self)
        self.addAction(a)
        a.triggered.connect(self._deleteSelectedRows)

        # Buttons
        hbox = QtGui.QHBoxLayout()
        b = QtGui.QPushButton("New")
        b.clicked.connect(self._addNewEmptyType)
        b.setToolTip("Create a new entry type")
        hbox.addWidget(b)
        b = QtGui.QPushButton("Apply")
        b.clicked.connect(self.typifyAll.emit)
        b.setToolTip("Apply typing to all entries")
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

    def clear(self):
        while self.table.rowCount() > 0:
            self.table.removeRow(0)

    def addTypes(self, types):
        for name, regex in types.iteritems():
            self._appendRow(name, regex)


class TableController(QtCore.QObject):
    selectionChanged = QtCore.pyqtSignal()

    def __init__(self):
        super(TableController, self).__init__()

        self.table = QtGui.QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self.selectionChanged.emit)

    def _columnTitles(self):
        return [str(self.table.horizontalHeaderItem(col).text()) for col in xrange(self.table.columnCount())]

    def _columnIndexForLabel(self, label):
        return self._columnTitles().index(label)

    def clear(self):
        while self.table.columnCount() > 0:
            self.table.removeColumn(0)
        while self.table.rowCount() > 0:
            self.table.removeRow(0)

    def _ensureColumnsExist(self, col_titles):
        # note that we somewhat hard-code some columns to appear in a
        # certain order here, but only add the columns if the attributes
        # actually exist in the entries
        for title in ["amount", "date", "type", "description", "uid"] + col_titles:
            if title not in self._columnTitles() and title in col_titles:
                col = len(self._columnTitles())
                self.table.insertColumn(col)
                self.table.setHorizontalHeaderItem(col, QtGui.QTableWidgetItem(title))

    def addEntries(self, entries):
        if not entries:
            return

        self._ensureColumnsExist(entries[0].ATTRIBUTES)

        current_uids = [ce.uid for ce in self.entries]

        for e in entries:
            if e.uid in current_uids:
                # ensure we don't add duplicate entries
                continue
            current_uids.append(e.uid)

            row = self.table.rowCount()
            self.table.insertRow(row)

            for attr in e.ATTRIBUTES:
                wi = QtGui.QTableWidgetItem(str(getattr(e, attr)))

                # only the type column is user-modifiable
                if attr != "type":
                    wi.setFlags(wi.flags() & ~QtCore.Qt.ItemIsEditable)

                if e.amount > 0.0:
                    wi.setBackgroundColor(QtGui.QColor(160, 255, 160))

                self.table.setItem(row, self._columnIndexForLabel(attr), wi)

        if "description" in self._columnTitles():
            self.table.resizeColumnToContents(self._columnTitles().index("description"))

    @property
    def entries(self):
        ret = []

        for row in xrange(self.table.rowCount()):
            d = {}
            for attr in centry.CEntry.ATTRIBUTES:
                d[attr] = str(self.table.item(row, self._columnIndexForLabel(attr)).text())

            ret.append(centry.CEntry(d))

        return ret

    @property
    def selected_entries(self):
        rows = set()
        for sr in self.table.selectedRanges():
            rows.update(xrange(sr.topRow(), sr.bottomRow() + 1))

        return [self.entries[row] for row in sorted(rows)]


class MainWin(QtGui.QMainWindow):
    newFile = QtCore.pyqtSignal()
    openFile = QtCore.pyqtSignal()
    closeFile = QtCore.pyqtSignal()
    saveFile = QtCore.pyqtSignal()
    saveFileAs = QtCore.pyqtSignal()
    addEntries = QtCore.pyqtSignal()

    def __init__(self, table, dock):
        super(MainWin, self).__init__()

        self._sbar_total_entries_label = QtGui.QLabel()
        self._sbar_selected_label = QtGui.QLabel()

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

        # Status bar
        self.statusBar().addPermanentWidget(self._sbar_total_entries_label)
        self.statusBar().addWidget(self._sbar_selected_label)

        # Window stuff
        self.setWindowTitle("CCash")
        self.resize(1024, 600)
        self.show()

    def updateStatusBar(self, all_entries, selected):
        num_ent = len(all_entries)
        self._sbar_total_entries_label.setText("%d entries" % num_ent)

        num_sel = len(selected)
        cost_sel = sum([e.amount for e in selected])
        self._sbar_selected_label.setText("%d selected, $%.2f" % (num_sel, cost_sel))


class MainCont(object):
    def __init__(self):
        # Path to most recently opened or saved file
        self._recent_path = ""

        # Path to most recently *added* file
        self._recent_qfx_path = ""

        # Main table controller
        self.table_cont = TableController()
        self.table_cont.selectionChanged.connect(self.updateStatusBar)

        # Types dock controller
        self._dock = QtGui.QDockWidget()
        self._dock.setWidget(TypesDockWidget())
        self._dock.widget().typesDeleted.connect(self._typesDeleted)
        self._dock.widget().typifyAll.connect(self._typifyAll)

        # Main window signals
        self._win = MainWin(self.table_cont.table, self._dock)
        self._win.newFile.connect(self._newFile)
        self._win.openFile.connect(self._loadFromPath)
        self._win.closeFile.connect(self._closeFile)
        self._win.saveFile.connect(self._saveFile)
        self._win.saveFileAs.connect(self._saveFileAs)
        self._win.addEntries.connect(self._addEntriesFromQFX)

        self._resetUI()

    def _resetUI(self):
        self.table_cont.clear()
        self._dock.widget().clear()

        self.updateStatusBar()

    def _typesDeleted(self, typenames):
        #TODO: unset entry types that had their type deleted
        pass

    def _typifyAll(self):
        #TODO: go through and reset all entry types based on current autotype filters
        pass

    def load(self, path):
        types, entries = cfile.loadFromFile(path)

        self._resetUI()

        self.table_cont.addEntries(entries)
        self._dock.widget().addTypes(types)
        self.updateStatusBar()

        self._recent_path = str(path)

    def save(self, path):
        cfile.writeToFile(path, self._dock.widget().types, self.table_cont.entries)

        self._recent_path = str(path)

    def _confirmIfChanges(self):
        #TODO: prompt if the user has made changes
        return True

    def _newFile(self):
        if not self._confirmIfChanges():
            return

        self._resetUI()

    def _loadFromPath(self):
        if not self._confirmIfChanges():
            return

        path = QtGui.QFileDialog.getOpenFileName(parent=self._win,
                                                 caption="Open File",
                                                 directory=os.path.dirname(self._recent_path),
                                                 filter="CCash (*.ccash)")
        if not path:
            return

        self.load(path)

    def _closeFile(self):
        if not self._confirmIfChanges():
            return

        self._resetUI()

    def _saveFile(self):
        if not self._recent_path:
            self._saveFileAs()
        else:
            self.save(self._recent_path)

    def _saveFileAs(self):
        path = QtGui.QFileDialog.getSaveFileName(parent=self._win,
                                                 caption="Save File",
                                                 directory=os.path.dirname(self._recent_path),
                                                 filter="CCash (*.ccash)")
        if not path:
            return
        path = str(path)

        if os.path.splitext(path)[1] != ".ccash":
            path += ".ccash"

        self.save(path)

    def _addEntriesFromQFX(self):
        path = QtGui.QFileDialog.getOpenFileName(parent=self._win,
                                                 caption="Open File",
                                                 directory=os.path.dirname(self._recent_qfx_path),
                                                 filter="QFX (*.qfx)")
        if not path:
            return

        entries = [centry.CEntryFromQFX(qfx_stmttrn) for qfx_stmttrn in qfx.parseTransactionsFromFile(path)]

        #TODO: autotype the entries

        self.table_cont.addEntries(entries)
        self.updateStatusBar()

        self._recent_qfx_path = str(path)

    def updateStatusBar(self):
        self._win.updateStatusBar(self.table_cont.entries, self.table_cont.selected_entries)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    cont = MainCont()

    if len(sys.argv) > 1:
        cont.load(sys.argv[1])

    sys.exit(app.exec_())
