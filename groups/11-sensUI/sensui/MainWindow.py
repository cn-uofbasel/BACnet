from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QTabWidget
from PyQt5 import uic
import pyqtgraph as pg
import sys
import os
import jsonpickle

from sensui.View import View
from sensui.NodeManager import NodeManager
from sensui.ViewManager import ViewManager
from sensui.ViewConfigTab import ViewConfigTab
from sensui.NodeConfigTab import NodeConfigTab

class MainWindow(QMainWindow):

    FILENAME_CONFIG_VIEWS = "views"
    FILENAME_CONFIG_NODES = "nodes"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "MainWindow.ui"), self)

        jsonpickle.set_encoder_options('simplejson', sort_keys=True, indent=4)
        jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)
        jsonpickle.set_preferred_backend("simplejson")

        self.__tabs = {}

        self.uiMainTabWidget = self.findChild(QTabWidget, "tabWidget")

        nodes = self.__loadConfigFromFile(MainWindow.FILENAME_CONFIG_NODES, {})
        self.nodes = NodeManager(nodes)
        views = self.__loadConfigFromFile(MainWindow.FILENAME_CONFIG_VIEWS, {})
        self.views = ViewManager(views)

        nodeConfigTab = NodeConfigTab(self.nodes, callbackModified=self.callbackModifiedNodes)
        self.uiMainTabWidget.addTab(nodeConfigTab, "Konfiguration")

        viewConfigTab = ViewConfigTab(self.views, self.nodes, self.viewOpen, callbackModified=self.callbackModifiedViews)
        self.uiMainTabWidget.addTab(viewConfigTab, "Ansichten")

    def callbackModifiedNodes(self):
        self.__saveConfigToFile(self.nodes.getAll(), MainWindow.FILENAME_CONFIG_NODES)

    def callbackModifiedViews(self):
        self.__saveConfigToFile(self.views.getAll(), MainWindow.FILENAME_CONFIG_VIEWS)

    '''
        View Methods
    '''
    def __createViewTab(self, view):
        if view is None:
            return None

        hour = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]
        temperature2 = [34, 35, 31, 30, 29, 34, 21, 31, 35, 50]

        graphWidget = pg.PlotWidget()

        yAxisLeft = view.getYAxis(View.YAXIS_LEFT)
        if yAxisLeft is not None and yAxisLeft.active is True:
            graphWidget.setLabel('left', yAxisLeft.label, color='red', size=30)
        yAxisRight = view.getYAxis(View.YAXIS_RIGHT)
        if yAxisRight is not None and yAxisRight.active is True:
            graphWidget.setLabel('right', yAxisRight.label, color='red', size=30)
        graphWidget.setLabel('bottom', 'Zeit', color='red', size=30)
        graphWidget.plot(hour, temperature)
        return graphWidget

    def viewOpen(self, view):
        if view is None:
            return

        if view.id in self.__tabs:
            tab = self.__tabs[view.id]
            index = self.uiMainTabWidget.indexOf(tab)
        else:
            tab = self.__createViewTab(view)
            if tab is None:
                return
            self.__tabs[view.id] = tab
            index = -1

        if index >= 0:
            self.uiMainTabWidget.setCurrentIndex(index)
        else:
            self.uiMainTabWidget.addTab(tab, view.name)
            self.uiMainTabWidget.setCurrentWidget(tab)


    '''
        General Methods
    '''

    def __saveConfigToFile(self, config, filename):
        if config is None or not isinstance(filename, str):
            return False
        with open (filename + ".json", "w") as f:
            f.write(jsonpickle.encode(config))

    def __loadConfigFromFile(self, filename, default=None):
        if not isinstance(filename, str) or not os.path.isfile(filename + ".json"):
            return default
        with open (filename + ".json", "r") as f:
            config = jsonpickle.decode(f.read())

        return config


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
