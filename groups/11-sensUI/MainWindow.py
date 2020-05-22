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

    YAXIS_FIELD_ACTIVE = "Active"
    YAXIS_FIELD_MEASUREMENT_SIZE = "MeasurementSize"
    YAXIS_FIELD_LABEL = "Label"
    YAXIS_FIELD_SENSORS = "Sensors"

    FILENAME_CONFIG_NODES = "nodes"
    FILENAME_CONFIG_VIEWS = "views"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("/home/marc/docs/study/20FS/IaS/BACnet/groups/11-sensUI/MainWindow.ui", self)

        self.timeUnits = {"Sekunden": 1, "Minuten": 60, "Stunden": 3600, "Tage":86400}
        self.measurementSizes = {"T": "Temperatur", "P": "Luftdruck", "rH": "Relative Luftfeuchtigkeit", "J": "Helligkeit"}

        jsonpickle.set_encoder_options('simplejson', sort_keys=True, indent=4)
        jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)
        jsonpickle.set_preferred_backend("simplejson")

        self.__nodes = self.__loadConfigFromFile(MainWindow.FILENAME_CONFIG_NODES, {})
        self.__views = self.__loadConfigFromFile(MainWindow.FILENAME_CONFIG_VIEWS, {})
        self.__tabs = {}
        for view in self.__views.values():
            print(view)
        self.__nodeConfigSelectedId = None
        self.__viewConfigSelectedId = None

        self.uiMainTabWidget = self.findChild(QTabWidget, "tabWidget")

        self.__initNodeConfigTab()
        self.__initViewConfigTab()

        self.nodeConfigUpdateList()
        self.viewConfigUpdateList()

        viewConfigTab = ViewConfigTab(self.viewOpen, callbackStore=self.__saveConfigToFile, callbackLoad=self.__loadConfigFromFile)
        self.uiMainTabWidget.addTab(viewConfigTab, "Konfiguration")

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
        ViewConfig-Tab Methods
    '''
    def __initViewConfigTab(self):
        # View Config
        self.uiViewConfigName = self.findChild(QLineEdit, "lineEditViewsSettingsNameValue")
        self.uiViewConfigList = self.findChild(QListWidget, "listWidgetViewsOverviewControlsViews")
        self.uiViewConfigSave = self.findChild(QPushButton, "pushButtonViewsSettingsSave")
        self.uiViewConfigNew = self.findChild(QPushButton, "pushButtonViewsOverviewControlsNew")
        self.uiViewConfigDelete = self.findChild(QPushButton, "pushButtonViewsOverviewControlsDelete")
        self.uiViewConfigOpen = self.findChild(QPushButton, "pushButtonViewsOverviewControlsOpen")

        self.uiViewConfigYAxes = [{}, {}]
        self.uiViewConfigYAxes[View.YAXIS_LEFT][MainWindow.YAXIS_FIELD_ACTIVE] = \
            self.findChild(QCheckBox, "checkBoxViewsSettingsYAxisFirstControlsActive")
        self.uiViewConfigYAxes[View.YAXIS_LEFT][MainWindow.YAXIS_FIELD_MEASUREMENT_SIZE] = \
            self.findChild(QComboBox, "comboBoxViewsSettingsYAxisFirstControlsMeasurementSize")
        self.uiViewConfigYAxes[View.YAXIS_LEFT][MainWindow.YAXIS_FIELD_LABEL] = \
            self.findChild(QLineEdit, "lineEditViewsSettingsYAxisFirstControlsAxisLabel")
        self.uiViewConfigYAxes[View.YAXIS_LEFT][MainWindow.YAXIS_FIELD_SENSORS] = \
            self.findChild(QListView, "listViewViewsSettingsYAxisFirstSensors")

        self.uiViewConfigYAxes[View.YAXIS_RIGHT][MainWindow.YAXIS_FIELD_ACTIVE] = \
            self.findChild(QCheckBox, "checkBoxViewsSettingsYAxisSecondControlsActive")
        self.uiViewConfigYAxes[View.YAXIS_RIGHT][MainWindow.YAXIS_FIELD_MEASUREMENT_SIZE] = \
            self.findChild(QComboBox, "comboBoxViewsSettingsYAxisSecondControlsMeasurementSize")
        self.uiViewConfigYAxes[View.YAXIS_RIGHT][MainWindow.YAXIS_FIELD_LABEL] = \
            self.findChild(QLineEdit, "lineEditViewsSettingsYAxisSecondControlsAxisLabel")
        self.uiViewConfigYAxes[View.YAXIS_RIGHT][MainWindow.YAXIS_FIELD_SENSORS] = \
            self.findChild(QListView, "listViewViewsSettingsYAxisSecondSensors")

        self.uiViewConfigYAxes[View.YAXIS_LEFT][MainWindow.YAXIS_FIELD_ACTIVE].toggled.connect(
            lambda: self.viewConfigToggleYAxisControls(self.uiViewConfigYAxes[View.YAXIS_LEFT]))
        self.uiViewConfigYAxes[View.YAXIS_RIGHT][MainWindow.YAXIS_FIELD_ACTIVE].toggled.connect(
            lambda: self.viewConfigToggleYAxisControls(self.uiViewConfigYAxes[View.YAXIS_RIGHT]))

        #self.viewYAxis[View.YAXIS_LEFT][MainWindow.YAXIS_FIELD_MEASUREMENT_SIZE].addItems(self.measurementSizes)
        #self.viewYAxis[View.YAXIS_RIGHT][MainWindow.YAXIS_FIELD_MEASUREMENT_SIZE].addItems(self.measurementSizes)
        self.__viewConfigYAxisFillMeasurementSizes(self.measurementSizes)

        # Signals
        self.uiViewConfigList.itemSelectionChanged.connect(self.__viewConfigListSelectedHandler)
        self.uiViewConfigNew.clicked.connect(self.viewConfigCreateNew)
        self.uiViewConfigSave.clicked.connect(self.__viewConfigSaveCurrentSelected)
        self.uiViewConfigDelete.clicked.connect(self.__viewConfigDeleteCurrentSelectedView)
        self.uiViewConfigOpen.clicked.connect(self.__viewConfigOpenCurrentSelectedView)

        self.viewConfigToggleControls(False)

    def __viewConfigYAxisFillMeasurementSizes(self, measurementSizes):
        for id, label in measurementSizes.items():
            var = QVariant(id)
            self.uiViewConfigYAxes[View.YAXIS_LEFT][MainWindow.YAXIS_FIELD_MEASUREMENT_SIZE].addItem(label, var)
            self.uiViewConfigYAxes[View.YAXIS_RIGHT][MainWindow.YAXIS_FIELD_MEASUREMENT_SIZE].addItem(label, var)
        #Qt.UserRole,



    def viewConfigToggleControls(self, enabled):
        if enabled is None:
            return

        self.uiViewConfigName.setEnabled(enabled)
        self.uiViewConfigSave.setEnabled(enabled)

        self.viewConfigToggleYAxisControls(self.uiViewConfigYAxes[View.YAXIS_LEFT], enabled, True)
        self.viewConfigToggleYAxisControls(self.uiViewConfigYAxes[View.YAXIS_RIGHT], enabled, True)

    def viewConfigToggleYAxisControls(self, yAxis, enabled=None, toggleAll=False):
        if yAxis is None or yAxis is None:
            return

        if toggleAll and enabled is not None:
            yAxis[MainWindow.YAXIS_FIELD_ACTIVE].setEnabled(enabled)

        # Only enable Axis-Controls if the Active-Checkbox is checked
        if enabled is not False:
            enableSensorControl = yAxis[MainWindow.YAXIS_FIELD_ACTIVE].isChecked()
        else:
            enableSensorControl = False

        yAxis[MainWindow.YAXIS_FIELD_MEASUREMENT_SIZE].setEnabled(enableSensorControl)
        yAxis[MainWindow.YAXIS_FIELD_LABEL].setEnabled(enableSensorControl)
        yAxis[MainWindow.YAXIS_FIELD_SENSORS].setEnabled(enableSensorControl)

    def __viewConfigDisplayCurrentSelected(self):
        self.viewConfigDisplay(self.viewConfigCurrentSelectedView())

    def viewConfigDisplay(self, view):
        if view is None:
            self.viewConfigToggleControls(False)
            return

        if view.name is not None:
            self.uiViewConfigName.setText(view.name)

        for yAxisId in View.YAXES:
            yAxis = self.uiViewConfigYAxes[yAxisId]
            yAxisConfig = view.getYAxis(yAxisId)
            self.viewConfigYAxisDisplay(yAxis, yAxisConfig)

        self.viewConfigToggleControls(True)

    def viewConfigYAxisDisplay(self, yAxis, yAxisConfig):
        if yAxis is None or yAxisConfig is None:
            return

        if yAxisConfig.active is True:
            yAxis[MainWindow.YAXIS_FIELD_ACTIVE].setChecked(True)
        else:
            yAxis[MainWindow.YAXIS_FIELD_ACTIVE].setChecked(False)

        if yAxisConfig.label is not None:
            yAxis[MainWindow.YAXIS_FIELD_LABEL].setText(yAxisConfig.label)
        else:
            yAxis[MainWindow.YAXIS_FIELD_LABEL].setText("")

        if yAxisConfig.measurementSize is not None:
            yAxis[MainWindow.YAXIS_FIELD_MEASUREMENT_SIZE].setCurrentText(yAxisConfig.measurementSize)
        else:
            yAxis[MainWindow.YAXIS_FIELD_MEASUREMENT_SIZE].setCurrentIndex(-1)

        self.viewConfigYAxisSelectSensors(yAxis, yAxisConfig.sensors)

    def viewConfigSave(self):
        self.__saveConfigToFile(self.__views, MainWindow.FILENAME_CONFIG_VIEWS)

    def __viewConfigSaveCurrentSelected(self):
        view = self.viewConfigCurrentSelectedView()
        if view is None:
            return False

        view.name = self.uiViewConfigName.text()

        for yAxisId in View.YAXES:
            yAxis = view.getYAxis(yAxisId)
            if yAxis is None:
                continue
            yAxis.label = self.uiViewConfigYAxes[yAxisId][MainWindow.YAXIS_FIELD_LABEL].text()
            yAxis.active = self.uiViewConfigYAxes[yAxisId][MainWindow.YAXIS_FIELD_ACTIVE].isChecked()
            yAxis.measurementSize = self.uiViewConfigYAxes[yAxisId][MainWindow.YAXIS_FIELD_MEASUREMENT_SIZE].currentData()
            # TODO: Save sensor selection
            view.setYAxis(yAxis)

        # Update Name on List
        items = self.uiViewConfigList.selectedItems()
        if len(items) == 1:
            items[0].setText(view.name)

        if view is not None:
            self.__views[self.__viewConfigSelectedId] = view
        self.viewConfigSave()

        return True

    def __viewConfigShowInList(self, view):
        if view is None:
            return
        item = QListWidgetItem(view.name)
        item.setData(Qt.UserRole, QVariant(view.id))
        self.uiViewConfigList.addItem(item)
        self.uiViewConfigList.setCurrentItem(item)

    def __viewConfigListSelectedHandler(self):
        items = self.uiViewConfigList.selectedItems()
        if len(items) == 1 and items[0] is not None:
            id = items[0].data(Qt.UserRole)
            if id is not None and id in self.__views:
                self.__viewConfigSelectedId = id
            else:
                self.__viewConfigSelectedId = None
            self.__viewConfigDisplayCurrentSelected()

    def viewConfigUpdateList(self):
        if self.__views is None:
            return

        self.uiViewConfigList.clear()
        for view in self.__views.values():
            self.__viewConfigShowInList(view)

    def viewConfigAdd(self, view):
        if view is None:
            return

        self.__views[view.id] = view
        self.__viewConfigShowInList(view)

    def viewConfigIsViewSelected(self):
        if self.__viewConfigSelectedId is None or self.__viewConfigSelectedId not in self.__views:
            return False

        return True

    def viewConfigCurrentSelectedView(self):
        if not self.viewConfigIsViewSelected():
            return None

        return self.__views[self.__viewConfigSelectedId]

    def __viewConfigOpenCurrentSelectedView(self):
        view = self.viewConfigCurrentSelectedView()
        self.viewOpen(view)


    def __viewConfigDeleteCurrentSelectedView(self):
        item = self.uiViewConfigList.takeItem(self.uiViewConfigList.currentRow())
        self.viewConfigDelete(item.data(Qt.UserRole))

    def viewConfigDelete(self, viewId):
        if viewId is None or viewId not in self.__views:
            return

        del self.__views[viewId]

        return viewId


    def viewConfigCreateNew(self):
        self.viewConfigAdd(View(name="Neue Ansicht"))

    def viewConfigYAxisSelectSensors(self, yAxis, sensors):

        return

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
