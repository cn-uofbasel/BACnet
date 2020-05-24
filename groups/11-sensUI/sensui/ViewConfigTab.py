from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLineEdit, QCheckBox, QComboBox, QPushButton
from PyQt5.QtWidgets import QListView, QListWidget, QListWidgetItem, QAbstractItemView
from PyQt5.QtCore import QVariant, Qt
from PyQt5 import uic
import os

from sensui.View import View
from sensui.SensorManager import SensorManager


class ViewConfigTab(QWidget):

    YAXIS_FIELD_ACTIVE = "Active"
    YAXIS_FIELD_MEASUREMENT_SIZE = "MeasurementSize"
    YAXIS_FIELD_LABEL = "Label"
    YAXIS_FIELD_SENSORS = "Sensors"

    FILENAME_CONFIG_VIEWS = "views"

    def __init__(self, views, nodes, callbackOpenView, callbackModified=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "ViewConfigTab.ui"), self)

        self.__callbackOpenView = callbackOpenView
        self.__callbackModified = callbackModified

        self.__views = views
        self.__nodes = nodes
        self.__viewConfigSelectedId = None
        self.__measurementSizesLabels = {}
        self.__initViewConfigTab()

        self.updateList()


    '''
        ViewConfig-Tab Methods
    '''
    def __initViewConfigTab(self):
        # View Config
        self.uiName = self.findChild(QLineEdit, "lineEditViewsSettingsNameValue")
        self.uiList = self.findChild(QListWidget, "listWidgetViewsOverviewControlsViews")
        self.uiSave = self.findChild(QPushButton, "pushButtonViewsSettingsSave")
        self.uiNew = self.findChild(QPushButton, "pushButtonViewsOverviewControlsNew")
        self.uiDelete = self.findChild(QPushButton, "pushButtonViewsOverviewControlsDelete")
        self.uiOpen = self.findChild(QPushButton, "pushButtonViewsOverviewControlsOpen")

        self.uiYAxes = [{}, {}]
        self.uiYAxes[View.YAXIS_LEFT][ViewConfigTab.YAXIS_FIELD_ACTIVE] = \
            self.findChild(QCheckBox, "checkBoxViewsSettingsYAxisFirstControlsActive")
        self.uiYAxes[View.YAXIS_LEFT][ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE] = \
            self.findChild(QComboBox, "comboBoxViewsSettingsYAxisFirstControlsMeasurementSize")
        self.uiYAxes[View.YAXIS_LEFT][ViewConfigTab.YAXIS_FIELD_LABEL] = \
            self.findChild(QLineEdit, "lineEditViewsSettingsYAxisFirstControlsAxisLabel")
        self.uiYAxes[View.YAXIS_LEFT][ViewConfigTab.YAXIS_FIELD_SENSORS] = \
            self.findChild(QListView, "listWidgetViewsSettingsYAxisFirstSensors")

        self.uiYAxes[View.YAXIS_RIGHT][ViewConfigTab.YAXIS_FIELD_ACTIVE] = \
            self.findChild(QCheckBox, "checkBoxViewsSettingsYAxisSecondControlsActive")
        self.uiYAxes[View.YAXIS_RIGHT][ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE] = \
            self.findChild(QComboBox, "comboBoxViewsSettingsYAxisSecondControlsMeasurementSize")
        self.uiYAxes[View.YAXIS_RIGHT][ViewConfigTab.YAXIS_FIELD_LABEL] = \
            self.findChild(QLineEdit, "lineEditViewsSettingsYAxisSecondControlsAxisLabel")
        self.uiYAxes[View.YAXIS_RIGHT][ViewConfigTab.YAXIS_FIELD_SENSORS] = \
            self.findChild(QListView, "listWidgetViewsSettingsYAxisSecondSensors")

        self.uiYAxes[View.YAXIS_LEFT][ViewConfigTab.YAXIS_FIELD_ACTIVE].toggled.connect(
            lambda: self.toggleYAxisControls(self.uiYAxes[View.YAXIS_LEFT]))
        self.uiYAxes[View.YAXIS_RIGHT][ViewConfigTab.YAXIS_FIELD_ACTIVE].toggled.connect(
            lambda: self.toggleYAxisControls(self.uiYAxes[View.YAXIS_RIGHT]))

        self.uiYAxes[View.YAXIS_LEFT][ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE].currentIndexChanged.connect(
            lambda: self.yAxisSelectionChanged(View.YAXIS_LEFT))
        self.uiYAxes[View.YAXIS_RIGHT][ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE].currentIndexChanged.connect(
            lambda: self.yAxisSelectionChanged(View.YAXIS_RIGHT))
        self.__yAxisFillMeasurementSizes(SensorManager.sensorTypes)

        self.uiYAxes[View.YAXIS_LEFT][ViewConfigTab.YAXIS_FIELD_SENSORS].setSelectionMode(
            QAbstractItemView.MultiSelection)
        self.uiYAxes[View.YAXIS_RIGHT][ViewConfigTab.YAXIS_FIELD_SENSORS].setSelectionMode(
            QAbstractItemView.MultiSelection)

        # Signals
        self.uiList.itemSelectionChanged.connect(self.__listItemSelectedHandler)
        self.uiNew.clicked.connect(self.createNew)
        self.uiSave.clicked.connect(self.__saveCurrentSelected)
        self.uiDelete.clicked.connect(self.__deleteCurrentSelectedView)
        self.uiOpen.clicked.connect(self.__openCurrentSelectedView)

        self.toggleControls(False)

    def __yAxisFillMeasurementSizes(self, measurementSizes):
        for id, quantity in measurementSizes.items():
            var = QVariant(id)
            label = f"{quantity.name} ({quantity.unit})"
            self.__measurementSizesLabels[id] = label
            self.uiYAxes[View.YAXIS_LEFT][ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE].addItem(label, var)
            self.uiYAxes[View.YAXIS_RIGHT][ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE].addItem(label, var)



    def toggleControls(self, enabled):
        if enabled is None:
            return

        self.uiName.setEnabled(enabled)
        self.uiSave.setEnabled(enabled)

        self.toggleYAxisControls(self.uiYAxes[View.YAXIS_LEFT], enabled, True)
        self.toggleYAxisControls(self.uiYAxes[View.YAXIS_RIGHT], enabled, True)

    def toggleYAxisControls(self, yAxis, enabled=None, toggleAll=False):
        if yAxis is None or yAxis is None:
            return

        if toggleAll and enabled is not None:
            yAxis[ViewConfigTab.YAXIS_FIELD_ACTIVE].setEnabled(enabled)

        # Only enable Axis-Controls if the Active-Checkbox is checked
        if enabled is not False:
            enableSensorControl = yAxis[ViewConfigTab.YAXIS_FIELD_ACTIVE].isChecked()
        else:
            enableSensorControl = False

        yAxis[ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE].setEnabled(enableSensorControl)
        yAxis[ViewConfigTab.YAXIS_FIELD_LABEL].setEnabled(enableSensorControl)
        yAxis[ViewConfigTab.YAXIS_FIELD_SENSORS].setEnabled(enableSensorControl)

    def __displayCurrentSelected(self):
        self.display(self.currentSelectedView())

    def display(self, view):
        if view is None:
            self.toggleControls(False)
            return

        if view.name is not None:
            self.uiName.setText(view.name)

        for yAxisId in View.YAXES:
            yAxis = self.uiYAxes[yAxisId]
            yAxisConfig = view.getYAxis(yAxisId)
            self.__yAxisDisplay(yAxis, yAxisConfig)

        self.toggleControls(True)

    def __yAxisDisplay(self, yAxis, yAxisConfig):
        if yAxis is None or yAxisConfig is None:
            return

        if yAxisConfig.active is True:
            yAxis[ViewConfigTab.YAXIS_FIELD_ACTIVE].setChecked(True)
        else:
            yAxis[ViewConfigTab.YAXIS_FIELD_ACTIVE].setChecked(False)

        if yAxisConfig.label is not None:
            yAxis[ViewConfigTab.YAXIS_FIELD_LABEL].setText(yAxisConfig.label)
        else:
            yAxis[ViewConfigTab.YAXIS_FIELD_LABEL].setText("")

        if yAxisConfig.measurementSize is not None:
            label = self.__measurementSizesLabels[yAxisConfig.measurementSize]
            yAxis[ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE].setCurrentText(label)
        else:
            yAxis[ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE].setCurrentIndex(-1)

        if yAxisConfig.sensors is not None:
            for row in range(yAxis[ViewConfigTab.YAXIS_FIELD_SENSORS].count()):
                item = yAxis[ViewConfigTab.YAXIS_FIELD_SENSORS].item(row)
                nodeId, sensorId = item.data(Qt.UserRole)
                if nodeId in yAxisConfig.sensors and sensorId in yAxisConfig.sensors[nodeId]:
                    item.setSelected(True)
                else:
                    item.setSelected(False)


        #self.yAxisSelectSensors(yAxis, yAxisConfig.sensors)

    def __saveCurrentSelected(self):
        view = self.currentSelectedView()
        if view is None:
            return False

        view.name = self.uiName.text()

        for yAxisId in View.YAXES:
            yAxis = view.getYAxis(yAxisId)
            if yAxis is None:
                continue
            yAxis.label = self.uiYAxes[yAxisId][ViewConfigTab.YAXIS_FIELD_LABEL].text()
            yAxis.active = self.uiYAxes[yAxisId][ViewConfigTab.YAXIS_FIELD_ACTIVE].isChecked()
            yAxis.measurementSize = self.uiYAxes[yAxisId][ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE].currentData()

            yAxis.clearSensors()
            selection = self.uiYAxes[yAxisId][ViewConfigTab.YAXIS_FIELD_SENSORS].selectedItems()
            for selected in selection:
                nodeId, sensorId = selected.data(Qt.UserRole)
                yAxis.setSensor(nodeId, sensorId)
            view.setYAxis(yAxis)

        # Update Name on List
        items = self.uiList.selectedItems()
        if len(items) == 1:
            items[0].setText(view.name)

        self.__views.replace(view)

        if self.__callbackModified:
            self.__callbackModified()

        return True

    def __showInList(self, item, listRef, select=False):
        if item is None:
            return
        element = QListWidgetItem(item.name)
        element.setData(Qt.UserRole, QVariant(item.id))
        listRef.addItem(element)
        if select:
            listRef.setCurrentItem(element)

    def __listItemSelectedHandler(self):
        items = self.uiList.selectedItems()
        if len(items) == 1 and items[0] is not None:
            id = items[0].data(Qt.UserRole)
            if self.__views.containsId(id):
                self.__viewConfigSelectedId = id
            else:
                self.__viewConfigSelectedId = None
            self.__displayCurrentSelected()

    def updateList(self):

        self.uiList.clear()
        self.__views.forAll(self.__showInList, self.uiList, select=True)

    def add(self, view):
        if view is None:
            return

        self.__views.add(view)
        self.__showInList(view, self.uiList, select=True)

    def isViewSelected(self):
        return self.__views.containsId(self.__viewConfigSelectedId)

    def currentSelectedView(self):
        if not self.isViewSelected():
            return None

        return self.__views.get(self.__viewConfigSelectedId)

    def __openCurrentSelectedView(self):
        self.__callbackOpenView(self.currentSelectedView())


    def __deleteCurrentSelectedView(self):
        item = self.uiList.takeItem(self.uiList.currentRow())
        self.delete(item.data(Qt.UserRole))

    def delete(self, viewId):
        self.__views.delete(viewId)


    def createNew(self):
        self.add(View(name="Neue Ansicht"))

    def yAxisSelectionChanged(self, yAxisId):
        sensorId = self.uiYAxes[yAxisId][ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE].currentData(Qt.UserRole)
        if sensorId not in SensorManager.sensorTypes:
            return
        self.yAxisSelectSensors(self.uiYAxes[yAxisId], SensorManager.sensorTypes[sensorId].sType)

    def yAxisSelectSensors(self, yAxis, sensorType):
        if yAxis is None:
            return
        yAxis[ViewConfigTab.YAXIS_FIELD_SENSORS].clear()
        if sensorType is None:
            return
        nodes = self.__nodes.getBySensorType(sensorType)
        for node in nodes.values():
            for sensorId in node.getSensorsByType(sensorType):
                sensor = SensorManager.sensorTypes[sensorId]
                element = QListWidgetItem(f"{node.name}:{sensor.name}")
                element.setData(Qt.UserRole, QVariant((node.id, sensor.id)))
                yAxis[ViewConfigTab.YAXIS_FIELD_SENSORS].addItem(element)
