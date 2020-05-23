from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLineEdit, QCheckBox, QComboBox, QPushButton
from PyQt5.QtWidgets import QListView, QListWidget, QListWidgetItem
from PyQt5.QtCore import QVariant, Qt
from PyQt5 import uic
import os

from sensui.View import View
from sensui.Tools import Tools


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
            self.findChild(QListView, "listViewViewsSettingsYAxisFirstSensors")

        self.uiYAxes[View.YAXIS_RIGHT][ViewConfigTab.YAXIS_FIELD_ACTIVE] = \
            self.findChild(QCheckBox, "checkBoxViewsSettingsYAxisSecondControlsActive")
        self.uiYAxes[View.YAXIS_RIGHT][ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE] = \
            self.findChild(QComboBox, "comboBoxViewsSettingsYAxisSecondControlsMeasurementSize")
        self.uiYAxes[View.YAXIS_RIGHT][ViewConfigTab.YAXIS_FIELD_LABEL] = \
            self.findChild(QLineEdit, "lineEditViewsSettingsYAxisSecondControlsAxisLabel")
        self.uiYAxes[View.YAXIS_RIGHT][ViewConfigTab.YAXIS_FIELD_SENSORS] = \
            self.findChild(QListView, "listViewViewsSettingsYAxisSecondSensors")

        self.uiYAxes[View.YAXIS_LEFT][ViewConfigTab.YAXIS_FIELD_ACTIVE].toggled.connect(
            lambda: self.toggleYAxisControls(self.uiYAxes[View.YAXIS_LEFT]))
        self.uiYAxes[View.YAXIS_RIGHT][ViewConfigTab.YAXIS_FIELD_ACTIVE].toggled.connect(
            lambda: self.toggleYAxisControls(self.uiYAxes[View.YAXIS_RIGHT]))

        self.__yAxisFillMeasurementSizes(Tools.sensorTypes)

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
            yAxis[ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE].setCurrentText(yAxisConfig.measurementSize)
        else:
            yAxis[ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE].setCurrentIndex(-1)

        self.yAxisSelectSensors(yAxis, yAxisConfig.sensors)

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
            # TODO: Save sensor selection
            view.setYAxis(yAxis)

        # Update Name on List
        items = self.uiList.selectedItems()
        if len(items) == 1:
            items[0].setText(view.name)

        if view is not None:
            self.__views[self.__viewConfigSelectedId] = view

        if self.__callbackModified:
            self.__callbackModified()

        return True

    def __showInList(self, view):
        if view is None:
            return
        item = QListWidgetItem(view.name)
        item.setData(Qt.UserRole, QVariant(view.id))
        self.uiList.addItem(item)
        self.uiList.setCurrentItem(item)

    def __listItemSelectedHandler(self):
        items = self.uiList.selectedItems()
        if len(items) == 1 and items[0] is not None:
            id = items[0].data(Qt.UserRole)
            if id is not None and id in self.__views:
                self.__viewConfigSelectedId = id
            else:
                self.__viewConfigSelectedId = None
            self.__displayCurrentSelected()

    def updateList(self):
        if self.__views is None:
            return

        self.uiList.clear()
        for view in self.__views.values():
            self.__showInList(view)

    def add(self, view):
        if view is None:
            return

        self.__views[view.id] = view
        self.__showInList(view)

    def isViewSelected(self):
        if self.__viewConfigSelectedId is None or self.__viewConfigSelectedId not in self.__views:
            return False

        return True

    def currentSelectedView(self):
        if not self.isViewSelected():
            return None

        return self.__views[self.__viewConfigSelectedId]

    def __openCurrentSelectedView(self):
        self.__callbackOpenView(self.currentSelectedView())


    def __deleteCurrentSelectedView(self):
        item = self.uiList.takeItem(self.uiList.currentRow())
        self.delete(item.data(Qt.UserRole))

    def delete(self, viewId):
        if viewId is None or viewId not in self.__views:
            return

        del self.__views[viewId]

        return viewId


    def createNew(self):
        self.add(View(name="Neue Ansicht"))

    def yAxisSelectSensors(self, yAxis, sensors):

        return