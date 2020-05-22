from builtins import enumerate

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QPushButton
from PyQt5.QtWidgets import QListView, QListWidget, QListWidgetItem, QTabWidget, QAbstractItemView
from PyQt5.QtCore import QVariant, Qt
from PyQt5 import uic
import pyqtgraph as pg
import sys
import os
import jsonpickle

from Node import Node
from View import View
from ViewConfigTab import ViewConfigTab

class MainWindow(QMainWindow):

    FILENAME_CONFIG_NODES = "nodes"
    FILENAME_CONFIG_VIEWS = "views"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("/home/marc/docs/study/20FS/IaS/BACnet/groups/11-sensUI/MainWindow.ui", self)

        self.timeUnits = {"Sekunden": 1, "Minuten": 60, "Stunden": 3600, "Tage":86400}

        jsonpickle.set_encoder_options('simplejson', sort_keys=True, indent=4)
        jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)
        jsonpickle.set_preferred_backend("simplejson")

        self.__nodes = self.__loadConfigFromFile(MainWindow.FILENAME_CONFIG_NODES, {})
        self.__tabs = {}

        self.__nodeConfigSelectedId = None

        self.uiMainTabWidget = self.findChild(QTabWidget, "tabWidget")

        self.__initNodeConfigTab()

        self.nodeConfigUpdateList()

        viewConfigTab = ViewConfigTab(self.viewOpen, callbackStore=self.__saveConfigToFile, callbackLoad=self.__loadConfigFromFile)
        self.uiMainTabWidget.addTab(viewConfigTab, "Ansichten")

    '''
        NodeConfig-Tab Methods
    '''
    def __initNodeConfigTab(self):
        # Node Config
        self.uiNodeConfigName = self.findChild(QLineEdit, "lineEditConfigNodeName")
        self.uiNodeConfigId = self.findChild(QLabel, "labelConfigNodeId")

        self.uiNodeConfigSave = self.findChild(QPushButton, "pushButtonConfigNodeSave")
        self.uiNodeConfigUpdate = self.findChild(QPushButton, "pushButtonConfigNodeUpdate")
        self.uiNodeConfigList = self.findChild(QListWidget, "listWidgetConfigNodeList")

        self.uiNodeConfigPosition = {
            Node.POSITION_LATITUDE: self.findChild(QDoubleSpinBox, "doubleSpinBoxConfigNodePositionLatitude"),
            Node.POSITION_LONGITUDE: self.findChild(QDoubleSpinBox, "doubleSpinBoxConfigNodePositionLongitude"),
            Node.POSITION_ELEVATION: self.findChild(QDoubleSpinBox, "doubleSpinBoxConfigNodePositionAltitude")
        }

        self.uiNodeConfigInterval = self.findChild(QDoubleSpinBox, "doubleSpinBoxConfigNodeInterval")
        self.nodeIntervalTimeUnit = self.findChild(QComboBox, "comboBoxConfigNodeIntervalTimeUnit")

        self.uiNodeConfigSensorsSelect = {
            Node.SENSOR_TEMPERATURE: self.findChild(QCheckBox, "checkBoxConfigNodeSensorTemperature"),
            Node.SENSOR_PRESSURE: self.findChild(QCheckBox, "checkBoxConfigNodeSensorAirPressure"),
            Node.SENSOR_HUMIDITY: self.findChild(QCheckBox,"checkBoxConfigNodeSensorRelativeHumidity"),
            Node.SENSOR_BRIGHTNESS: self.findChild(QCheckBox, "checkBoxConfigNodeSensorBrightness")
        }

        self.uiNodeConfigList.setSelectionMode(QAbstractItemView.SingleSelection)
        self.uiNodeConfigList.itemSelectionChanged.connect(self.__nodeConfigListSelectedHandler)
        self.uiNodeConfigSave.clicked.connect(self.__nodeConfigSaveCurrentSelected)

        self.__nodeConfigFillTimeComboBox()

        self.nodeConfigToggleControls(False)

    def nodeConfigIsViewSelected(self):
        if self.__nodeConfigSelectedId is None or self.__nodeConfigSelectedId not in self.__nodes:
            return False

        return True

    def nodeConfigCurrentSelectedNode(self):
        if not self.nodeConfigIsViewSelected():
            return None

        return self.__nodes[self.__nodeConfigSelectedId]

    def nodeConfigSave(self):
        self.__saveConfigToFile(self.__nodes, MainWindow.FILENAME_CONFIG_NODES)

    def __nodeConfigListSelectedHandler(self):
        items = self.uiNodeConfigList.selectedItems()
        if len(items) == 1 and items[0] is not None:
            id = items[0].data(Qt.UserRole)
            if id is not None and id in self.__nodes:
                self.__nodeConfigSelectedId = str(id)
            else:
                self.__nodeConfigSelectedId = None
            self.__nodeConfigDisplayCurrentSelected()

    def __nodeConfigShowInList(self, node):
        if node is None:
            return
        item = QListWidgetItem(node.name)
        item.setData(Qt.UserRole, QVariant(str(node.id)))
        self.uiNodeConfigList.addItem(item)

    def nodeConfigUpdateList(self):
        if self.__nodes is None:
            return

        self.uiNodeConfigList.clear()
        for node in self.__nodes.values():
            self.__nodeConfigShowInList(node)

    def nodeConfigAdd(self, node):
        if node is None:
            return

        self.__nodes[str(node.id)] = node
        self.__nodeConfigShowInList(node)

    def __nodeConfigSelectedIntervalTime(self):
        timeUnit = self.nodeIntervalTimeUnit.currentText()
        interval = self.uiNodeConfigInterval.value()
        if timeUnit in self.timeUnits and int(interval) == interval:
            timeMuliplier = self.timeUnits[timeUnit]
            return interval * timeMuliplier
        return None

    def __nodeConfigSaveCurrentSelected(self):
        node = self.nodeConfigCurrentSelectedNode()

        if node is None:
            return False

        node.name = self.uiNodeConfigName.text()

        interval = self.__nodeConfigSelectedIntervalTime()
        if interval is not None:
            node.interval = interval

        for p in Node.POSITION:
            node.position[p] = self.uiNodeConfigPosition[p].value()

        for s in Node.SENSORS:
            node.sensors[s] = self.uiNodeConfigSensorsSelect[s].isChecked()

        # Update Name on List
        items = self.uiNodeConfigList.selectedItems()
        if len(items) == 1:
            items[0].setText(node.name)

        self.__nodes[self.__nodeConfigSelectedId] = node
        self.nodeConfigSave()

        return True

    def nodeConfigToggleControls(self, enabled):
        if enabled is None:
            return

        self.uiNodeConfigName.setEnabled(enabled)

        self.uiNodeConfigSave.setEnabled(enabled)
        self.uiNodeConfigUpdate.setEnabled(enabled)

        self.uiNodeConfigInterval.setEnabled(enabled)
        self.nodeIntervalTimeUnit.setEnabled(enabled)

        for field in self.uiNodeConfigPosition.values():
            field.setEnabled(enabled)

        for field in self.uiNodeConfigSensorsSelect.values():
            field.setEnabled(enabled)

    def __nodeConfigFillTimeComboBox(self):
        self.nodeIntervalTimeUnit.addItems(self.timeUnits.keys())
        self.nodeIntervalTimeUnit.setCurrentIndex(0)

    def __nodeConfigDisplayCurrentSelected(self):
        self.nodeConfigDisplay(self.nodeConfigCurrentSelectedNode())


    def nodeConfigDisplay(self, node):
        if node is None or node.id is None:
            self.nodeConfigToggleControls(False)
            return

        self.uiNodeConfigId.setText(str(node.id))

        if node.name is not None:
            self.uiNodeConfigName.setText(node.name)

        if node.position is not None:
            for p in Node.POSITION:
                if node.position[p] is not None:
                    self.uiNodeConfigPosition[p].setValue(node.position[p])

        if node.interval is not None:
            self.uiNodeConfigInterval.setValue(node.interval)
            self.nodeIntervalTimeUnit.setCurrentIndex(0)

        if node.sensors is not None:
            for s in Node.SENSORS:
                if node.sensors[s] is not None:
                    self.uiNodeConfigSensorsSelect[s].setChecked(node.sensors[s])

        self.nodeConfigToggleControls(True)

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

    # Demo Data
    def showDemoData(self):
        tabWidget = self.findChild(QTabWidget, "tabWidget")

        hour = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]
        temperature2 = [34, 35, 31, 30, 29, 34, 21, 31, 35, 50]

        self.graphWidget1 = pg.PlotWidget()
        self.graphWidget1.setLabel('left', 'Temperatur (°C)', color='red', size=30)
        self.graphWidget1.setLabel('bottom', 'Zeit', color='red', size=30)
        self.graphWidget1.plot(hour, temperature)
        tabWidget.addTab(self.graphWidget1, "Page 1")

        self.graphWidget2 = pg.PlotWidget()
        self.graphWidget2.setLabel('left', 'Temperatur (°C)', color='red', size=30)
        self.graphWidget2.setLabel('bottom', 'Zeit', color='red', size=30)
        self.graphWidget2.plot(hour, temperature)
        self.graphWidget2.plot(hour, temperature2)
        tabWidget.addTab(self.graphWidget2, "Page 2")

    def showDemoData2(self):

        node1 = Node(1)
        node1.name = "Name -1"
        node1.interval = 500
        node1.position[Node.POSITION_ELEVATION] = 600
        node1.sensors[Node.SENSOR_TEMPERATURE] = True

        node2 = Node(2)
        node2.name = "Name 2"
        node2.interval = 400
        node2.position[Node.POSITION_ELEVATION] = 300
        node2.position[Node.POSITION_LONGITUDE] = 34.01
        node2.sensors[Node.SENSOR_BRIGHTNESS] = True
        node2.sensors[Node.SENSOR_HUMIDITY] = True

        self.nodeConfigAdd(node1)
        self.nodeConfigAdd(node2)
        #self.nodeConfigDisplay(node1)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    #window.showDemoData2()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
