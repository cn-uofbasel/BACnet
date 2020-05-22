
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLineEdit, QCheckBox, QComboBox, QPushButton
from PyQt5.QtWidgets import QListView, QListWidget, QListWidgetItem, QTabWidget
from PyQt5.QtCore import QVariant, Qt
from PyQt5 import uic
import pyqtgraph as pg

from View import View

class ViewConfigTab(QWidget):

    YAXIS_FIELD_ACTIVE = "Active"
    YAXIS_FIELD_MEASUREMENT_SIZE = "MeasurementSize"
    YAXIS_FIELD_LABEL = "Label"
    YAXIS_FIELD_SENSORS = "Sensors"

    FILENAME_CONFIG_NODES = "nodes"
    FILENAME_CONFIG_VIEWS = "views"

    def __init__(self, callbackOpenView, callbackStore=None, callbackLoad=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("/home/marc/docs/study/20FS/IaS/BACnet/groups/11-sensUI/ViewConfigTab.ui", self)

        self.measurementSizes = {"T": "Temperatur", "P": "Luftdruck", "rH": "Relative Luftfeuchtigkeit", "J": "Helligkeit"}

        self.__callbackOpenView = callbackOpenView
        self.__callbackStore = callbackStore
        self.__callbackLoad = callbackLoad

        if self.__callbackLoad is not None:
            self.__views = self.__callbackLoad(ViewConfigTab.FILENAME_CONFIG_VIEWS, {})
        else:
            self.__views = {}
        self.__viewConfigSelectedId = None
        self.__initViewConfigTab()

        self.viewConfigUpdateList()


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
        self.uiViewConfigYAxes[View.YAXIS_LEFT][ViewConfigTab.YAXIS_FIELD_ACTIVE] = \
            self.findChild(QCheckBox, "checkBoxViewsSettingsYAxisFirstControlsActive")
        self.uiViewConfigYAxes[View.YAXIS_LEFT][ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE] = \
            self.findChild(QComboBox, "comboBoxViewsSettingsYAxisFirstControlsMeasurementSize")
        self.uiViewConfigYAxes[View.YAXIS_LEFT][ViewConfigTab.YAXIS_FIELD_LABEL] = \
            self.findChild(QLineEdit, "lineEditViewsSettingsYAxisFirstControlsAxisLabel")
        self.uiViewConfigYAxes[View.YAXIS_LEFT][ViewConfigTab.YAXIS_FIELD_SENSORS] = \
            self.findChild(QListView, "listViewViewsSettingsYAxisFirstSensors")

        self.uiViewConfigYAxes[View.YAXIS_RIGHT][ViewConfigTab.YAXIS_FIELD_ACTIVE] = \
            self.findChild(QCheckBox, "checkBoxViewsSettingsYAxisSecondControlsActive")
        self.uiViewConfigYAxes[View.YAXIS_RIGHT][ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE] = \
            self.findChild(QComboBox, "comboBoxViewsSettingsYAxisSecondControlsMeasurementSize")
        self.uiViewConfigYAxes[View.YAXIS_RIGHT][ViewConfigTab.YAXIS_FIELD_LABEL] = \
            self.findChild(QLineEdit, "lineEditViewsSettingsYAxisSecondControlsAxisLabel")
        self.uiViewConfigYAxes[View.YAXIS_RIGHT][ViewConfigTab.YAXIS_FIELD_SENSORS] = \
            self.findChild(QListView, "listViewViewsSettingsYAxisSecondSensors")

        self.uiViewConfigYAxes[View.YAXIS_LEFT][ViewConfigTab.YAXIS_FIELD_ACTIVE].toggled.connect(
            lambda: self.viewConfigToggleYAxisControls(self.uiViewConfigYAxes[View.YAXIS_LEFT]))
        self.uiViewConfigYAxes[View.YAXIS_RIGHT][ViewConfigTab.YAXIS_FIELD_ACTIVE].toggled.connect(
            lambda: self.viewConfigToggleYAxisControls(self.uiViewConfigYAxes[View.YAXIS_RIGHT]))

        #self.viewYAxis[View.YAXIS_LEFT][ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE].addItems(self.measurementSizes)
        #self.viewYAxis[View.YAXIS_RIGHT][ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE].addItems(self.measurementSizes)
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
            self.uiViewConfigYAxes[View.YAXIS_LEFT][ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE].addItem(label, var)
            self.uiViewConfigYAxes[View.YAXIS_RIGHT][ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE].addItem(label, var)
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
            yAxis[ViewConfigTab.YAXIS_FIELD_ACTIVE].setEnabled(enabled)

        # Only enable Axis-Controls if the Active-Checkbox is checked
        if enabled is not False:
            enableSensorControl = yAxis[ViewConfigTab.YAXIS_FIELD_ACTIVE].isChecked()
        else:
            enableSensorControl = False

        yAxis[ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE].setEnabled(enableSensorControl)
        yAxis[ViewConfigTab.YAXIS_FIELD_LABEL].setEnabled(enableSensorControl)
        yAxis[ViewConfigTab.YAXIS_FIELD_SENSORS].setEnabled(enableSensorControl)

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

        self.viewConfigYAxisSelectSensors(yAxis, yAxisConfig.sensors)

    def viewConfigSave(self):
        if self.__callbackStore is not None:
            self.__callbackStore(self.__views, ViewConfigTab.FILENAME_CONFIG_VIEWS)

    def __viewConfigSaveCurrentSelected(self):
        view = self.viewConfigCurrentSelectedView()
        if view is None:
            return False

        view.name = self.uiViewConfigName.text()

        for yAxisId in View.YAXES:
            yAxis = view.getYAxis(yAxisId)
            if yAxis is None:
                continue
            yAxis.label = self.uiViewConfigYAxes[yAxisId][ViewConfigTab.YAXIS_FIELD_LABEL].text()
            yAxis.active = self.uiViewConfigYAxes[yAxisId][ViewConfigTab.YAXIS_FIELD_ACTIVE].isChecked()
            yAxis.measurementSize = self.uiViewConfigYAxes[yAxisId][ViewConfigTab.YAXIS_FIELD_MEASUREMENT_SIZE].currentData()
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
        self.__callbackOpenView(self.viewConfigCurrentSelectedView())


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