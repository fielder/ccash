from PyQt4 import QtCore
from PyQt4 import QtGui

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class _ChartWin(QtGui.QMainWindow):
    def __init__(self, canvas_class, entries, parent=None):
        super(_ChartWin, self).__init__(parent=parent)

        self._figure = matplotlib.figure.Figure()
        self._canvas = canvas_class(self._figure)

        self.setCentralWidget(self._canvas)

        self._entries = entries

    def refresh(self):
        self._canvas.draw()


class _ChartCanvas_ContributionPie(FigureCanvas):
    DESCRIPTION = "contribution pie chart"
    TOOLBAR_ICON_PATH = ""
    #TODO: ...


class _ChartCanvas_FundsOverTime(FigureCanvas):
    DESCRIPTION = "funds over time"
    TOOLBAR_ICON_PATH = ""
    #TODO: ...


class _ChartCanvas_SpendRateOverTime(FigureCanvas):
    DESCRIPTION = "spend rate over time"
    TOOLBAR_ICON_PATH = ""
    #TODO: ...


class _ChartCanvas_ContributionOverTime(FigureCanvas):
    DESCRIPTION = "contribution over time"
    TOOLBAR_ICON_PATH = ""
    #TODO: ...


# find all chart types in here so the main interface can show all
# available charts without hard-coding anything
_chart_classes = {}
for obj_name in dir():
    if obj_name.startswith("_ChartCanvas_"):
        obj = globals()[obj_name]
        _chart_classes[obj.DESCRIPTION] = obj


def chartTypes():
    return _chart_classes.keys()


def newChartWindow(chart_type, entries, parent):
    win = _ChartWin(_chart_classes[chart_type], entries, parent=parent)
    win.show()
    return win
