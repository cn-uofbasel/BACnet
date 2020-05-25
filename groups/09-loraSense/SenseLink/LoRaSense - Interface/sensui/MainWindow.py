import sys
import os
import ast
import jsonpickle
import datetime

#PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QTabWidget, QTabBar
from PyQt5 import uic
from PyQt5 import QtCore

# Own Modules
from NodeManager import NodeManager
from ViewManager import ViewManager
from ViewConfigTab import ViewConfigTab
from NodeConfigTab import NodeConfigTab
from SensorManager import SensorManager
from ViewWidget import ViewWidget

# LoRaLink
import lora_feed_layer as LFL

# Demo Imports
import threading
import random

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

        self.sensorManager = SensorManager(self.views.callbackUpdate, self.nodes.addId)

        nodeConfigTab = NodeConfigTab(self.nodes, callbackModified=self.callbackModifiedNodes)
        self.nodes.setCallbackNodeAdded(nodeConfigTab.add)
        self.uiMainTabWidget.addTab(nodeConfigTab, "Konfiguration")
        self.uiMainTabWidget.tabBar().setTabButton(0, QTabBar.RightSide, None)

        viewConfigTab = ViewConfigTab(self.views, self.nodes, self.showView, callbackModified=self.callbackModifiedViews)
        self.uiMainTabWidget.addTab(viewConfigTab, "Ansichten")
        self.uiMainTabWidget.tabBar().setTabButton(1, QTabBar.RightSide, None)

        self.link = LFL.Lora_Feed_Layer()
        self.link.subscribe_sensor_feed(self.parseSensorFeedEvent)

        self.__updateTimer = QtCore.QTimer(self)
        self.__updateTimer.setInterval(1000)
        self.__updateTimer.timeout.connect(self.views.updateWidgets)
        self.__updateTimer.start()


    def stopTimer(self):
        self.readTimer.cancel()

    def callbackModifiedNodes(self):
        self.__saveConfigToFile(self.nodes.getAll(), MainWindow.FILENAME_CONFIG_NODES)

    def callbackModifiedViews(self):
        self.__saveConfigToFile(self.views.getAll(), MainWindow.FILENAME_CONFIG_VIEWS)

    def addSensorDataSet(self, nodeId, timestamp, t, p, h, b):
        # T=1 P=2 rH=3 J=%
        # d/m/Y
        time = timestamp.timestamp()
        self.sensorManager.addData(nodeId, "T_celcius", float(t), time)
        self.sensorManager.addData(nodeId, "P_bar", float(p), time)
        self.sensorManager.addData(nodeId, "rH", float(h), time)
        self.sensorManager.addData(nodeId, "J_lumen", float(b), time)

    def parseSensorFeedEventNoId(self, feedEvent):
        data = ast.literal_eval(feedEvent)
        if len(data) != 5:
            return
        self.addSensorDataSet(
            data[0], datetime.datetime.strptime(data[1], '%m/%d/%Y %H:%M:%S'), data[2], data[3], data[4], data[5])

    def parseSensorFeedEvent(self, feedEvent):
        data = ast.literal_eval(feedEvent)
        if len(data) != 6:
            return
        self.addSensorDataSet(
            data[0], datetime.datetime.strptime(data[1], '%m/%d/%Y %H:%M:%S'), data[2], data[3], data[4], data[5])

    def readSensorFeed(self):
        sensorFid = self.link.get_sensor_feed_fid()
        feedLength = self.link.get_feed_length(sensorFid)
        feedEvent = self.link.get_event_content(sensorFid, feedLength - 1)
        self.parseSensorFeedEvent(feedEvent)

    def periodicRead(self, interval):
        self.readSensorFeed()
        self.readTimer = threading.Timer(interval, self.periodicRead, args=[interval])
        self.readTimer.start()

    '''
        View Methods
    '''

    def showView(self, view):
        if view is None:
            return

        widget = self.views.open(view.id)

        for yAxis in view.getYAxes():
            if not yAxis.active:
                continue
            for nodeId, sensorId in yAxis.sensors.items():
                widget.setData(yAxis.id, nodeId, sensorId, self.sensorManager.dataReference(nodeId, sensorId))

        index = self.uiMainTabWidget.indexOf(widget)
        if index >= 0:
            self.uiMainTabWidget.setCurrentIndex(index)
        else:
            self.uiMainTabWidget.addTab(widget, view.name)
            self.uiMainTabWidget.setCurrentWidget(widget)
        widget.setOpen(True)

    def closeView(self, tabIndex):
        if tabIndex > 1:
            widget = self.uiMainTabWidget.widget(tabIndex)
            if isinstance(widget, ViewWidget):
                widget.setOpen(False)
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

demoTimer = None

def demo(window):
    global demoTimer
    window.parseSensorFeedEvent(
        f"['1','{datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')}','{random.random() * 50 - 10}','{random.randrange(10000) + 95000}','{random.random() * 30 + 30}','{random.random() * 100}']")
    demoTimer = threading.Timer(5, demo, args=[window])
    demoTimer.start()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    demo(window)
    window.show()
    app.exec_()
    #window.stopTimer()
    demoTimer.cancel()
    sys.exit()


if __name__ == '__main__':
    main()
