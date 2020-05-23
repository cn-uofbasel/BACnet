from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel, QLineEdit, QDoubleSpinBox, QCheckBox, QComboBox, QPushButton
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView, QHBoxLayout, QFrame, QGridLayout
from PyQt5.QtCore import QVariant, Qt
from PyQt5 import uic
import os

from sensui.Node import Node
from sensui.Tools import Tools


class NodeConfigTab(QWidget):

    def __init__(self, nodes, callbackModified=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "NodeConfigTab.ui"), self)

        self.__callbackModified = callbackModified

        self.timeUnits = {"Sekunden": 1, "Minuten": 60, "Stunden": 3600, "Tage":86400}

        self.__sensorSelectCheckboxes = {}

        self.__nodes = nodes

        self.__nodeConfigSelectedId = None
        self.__initNodeConfigTab()
        self.updateList()

    '''
        NodeConfig-Tab Methods
    '''
    def __initNodeConfigTab(self):
        # Node Config
        self.uiName = self.findChild(QLineEdit, "lineEditConfigNodeName")
        self.uiId = self.findChild(QLabel, "labelConfigNodeId")

        self.uiSave = self.findChild(QPushButton, "pushButtonConfigNodeSave")
        self.uiUpdate = self.findChild(QPushButton, "pushButtonConfigNodeUpdate")
        self.uiList = self.findChild(QListWidget, "listWidgetConfigNodeList")

        self.uiSensorContainer = self.findChild(QFrame, "frameSensors")

        self.uiPosition = {
            Node.POSITION_LATITUDE: self.findChild(QDoubleSpinBox, "doubleSpinBoxConfigNodePositionLatitude"),
            Node.POSITION_LONGITUDE: self.findChild(QDoubleSpinBox, "doubleSpinBoxConfigNodePositionLongitude"),
            Node.POSITION_ELEVATION: self.findChild(QDoubleSpinBox, "doubleSpinBoxConfigNodePositionAltitude")
        }

        self.uiInterval = self.findChild(QDoubleSpinBox, "doubleSpinBoxConfigNodeInterval")
        self.nodeIntervalTimeUnit = self.findChild(QComboBox, "comboBoxConfigNodeIntervalTimeUnit")

        self.uiList.setSelectionMode(QAbstractItemView.SingleSelection)
        self.uiList.itemSelectionChanged.connect(self.__listItemSelectedHandler)
        self.uiSave.clicked.connect(self.__saveCurrentSelected)

        self.uiSensorContainer.setLayout(QGridLayout())

        self.__fillTimeComboBox()
        self.__buildSensorSelection()

        self.toggleControls(False)

    def __buildSensorSelection(self):
        layout = self.uiSensorContainer.layout()
        row = 0
        col = 0
        for id, sensorType in Tools.sensorTypes.items():
            checkbox = QCheckBox(f"{sensorType.name} ({sensorType.unit})")
            self.__sensorSelectCheckboxes[id] = checkbox
            layout.addWidget(checkbox, row, col)
            if col < 1:
                col += 1
            else:
                col = 0
                row += 1


    def isViewSelected(self):
        if self.__nodeConfigSelectedId is None or self.__nodeConfigSelectedId not in self.__nodes:
            return False

        return True

    def currentSelectedNode(self):
        if not self.isViewSelected():
            return None

        return self.__nodes[self.__nodeConfigSelectedId]

    def __listItemSelectedHandler(self):
        items = self.uiList.selectedItems()
        if len(items) == 1 and items[0] is not None:
            id = items[0].data(Qt.UserRole)
            if id is not None and id in self.__nodes:
                self.__nodeConfigSelectedId = str(id)
            else:
                self.__nodeConfigSelectedId = None
            self.__displayCurrentSelected()

    def __showInList(self, node):
        if node is None:
            return
        item = QListWidgetItem(node.name)
        item.setData(Qt.UserRole, QVariant(str(node.id)))
        self.uiList.addItem(item)

    def updateList(self):
        if self.__nodes is None:
            return

        self.uiList.clear()
        for node in self.__nodes.values():
            self.__showInList(node)

    def add(self, node):
        if node is None:
            return

        self.__nodes[str(node.id)] = node
        self.__showInList(node)

    def __selectedIntervalTime(self):
        timeUnit = self.nodeIntervalTimeUnit.currentText()
        interval = self.uiInterval.value()
        if timeUnit in self.timeUnits and int(interval) == interval:
            timeMuliplier = self.timeUnits[timeUnit]
            return interval * timeMuliplier
        return None

    def __saveCurrentSelected(self):
        node = self.currentSelectedNode()

        if node is None:
            return False

        node.name = self.uiName.text()

        interval = self.__selectedIntervalTime()
        if interval is not None:
            node.interval = interval

        for p in Node.POSITION:
            node.position[p] = self.uiPosition[p].value()

        for id, checkbox in self.__sensorSelectCheckboxes.items():
            node.setSensor(id, checkbox.isChecked())

        # Update Name on List
        items = self.uiList.selectedItems()
        if len(items) == 1:
            items[0].setText(node.name)

        self.__nodes[self.__nodeConfigSelectedId] = node

        if self.__callbackModified:
            self.__callbackModified()

        return True

    def toggleControls(self, enabled):
        if enabled is None:
            return

        self.uiName.setEnabled(enabled)

        self.uiSave.setEnabled(enabled)
        self.uiUpdate.setEnabled(enabled)

        self.uiInterval.setEnabled(enabled)
        self.nodeIntervalTimeUnit.setEnabled(enabled)

        for field in self.uiPosition.values():
            field.setEnabled(enabled)

        for field in self.__sensorSelectCheckboxes.values():
            field.setEnabled(enabled)

    def __fillTimeComboBox(self):
        self.nodeIntervalTimeUnit.addItems(self.timeUnits.keys())
        self.nodeIntervalTimeUnit.setCurrentIndex(0)

    def __displayCurrentSelected(self):
        self.display(self.currentSelectedNode())


    def display(self, node):
        if node is None or node.id is None:
            self.toggleControls(False)
            return

        self.uiId.setText(str(node.id))

        if node.name is not None:
            self.uiName.setText(node.name)

        if node.position is not None:
            for p in Node.POSITION:
                if node.position[p] is not None:
                    self.uiPosition[p].setValue(node.position[p])

        if node.interval is not None:
            self.uiInterval.setValue(node.interval)
            self.nodeIntervalTimeUnit.setCurrentIndex(0)

        nodeSensors = node.getSensors()
        for id, checkbox in self.__sensorSelectCheckboxes.items():
            if id in nodeSensors:
                checkbox.setChecked(nodeSensors[id])
            else:
                checkbox.setChecked(False)

        self.toggleControls(True)