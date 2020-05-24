from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QTabWidget, QTabBar
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
from sensui.SensorManager import SensorManager

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
        self.uiMainTabWidget.tabCloseRequested.connect(self.closeView)

        nodes = self.__loadConfigFromFile(MainWindow.FILENAME_CONFIG_NODES, {})
        self.nodes = NodeManager(nodes)
        views = self.__loadConfigFromFile(MainWindow.FILENAME_CONFIG_VIEWS, {})
        self.views = ViewManager(views)
        self.sensorManager = SensorManager(self.views.callbackUpdate)

        nodeConfigTab = NodeConfigTab(self.nodes, callbackModified=self.callbackModifiedNodes)
        self.uiMainTabWidget.addTab(nodeConfigTab, "Konfiguration")
        self.uiMainTabWidget.tabBar().setTabButton(0, QTabBar.RightSide, None)

        viewConfigTab = ViewConfigTab(self.views, self.nodes, self.showView, callbackModified=self.callbackModifiedViews)
        self.uiMainTabWidget.addTab(viewConfigTab, "Ansichten")
        self.uiMainTabWidget.tabBar().setTabButton(1, QTabBar.RightSide, None)

    def callbackModifiedNodes(self):
        self.__saveConfigToFile(self.nodes.getAll(), MainWindow.FILENAME_CONFIG_NODES)

    def callbackModifiedViews(self):
        self.__saveConfigToFile(self.views.getAll(), MainWindow.FILENAME_CONFIG_VIEWS)

    '''
        View Methods
    '''

    def showView(self, view):
        if view is None:
            return

        widget = self.views.open(view.id)
        index = self.uiMainTabWidget.indexOf(widget)

        hour = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]
        temperature2 = [34, 35, 31, 30, 29, 34, 21, 31, 35, 50]

        widget.setData(View.YAXIS_LEFT, "0", "1", [hour, temperature])
        widget.setData(View.YAXIS_RIGHT, "0", "1", [hour, temperature2])

        #widget.addData(View.YAXIS_LEFT, "0", "1", 11, 126)
        print("Changing")
        hour.append(12)
        temperature.append(123)
        temperature2.append(-1)

        #widget.drawData()

        if index >= 0:
            self.uiMainTabWidget.setCurrentIndex(index)
        else:
            self.uiMainTabWidget.addTab(widget, view.name)
            self.uiMainTabWidget.setCurrentWidget(widget)

    def closeView(self, tabIndex):
        if tabIndex > 1:
            self.uiMainTabWidget.removeTab(tabIndex)

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
