import pyqtgraph as pg

from View import View
from DateAxisItem import DateAxisItem
from SensorManager import SensorManager

class ViewWidget (pg.PlotWidget):
    PEN_LEFT = 'w'
    PEN_RIGHT= 'b'

    def __init__(self, view):
        super().__init__()
        self.__view = view
        '''
            data = [
                0:Left Y-Axis
                1:Right Y-Axis
                {
                    nodeId: {
                        sensorId: [
                            [t], [v]
                        ]
                    }
                }
            ]
        '''
        self.__data = [{}, {}]
        self.__yAxes = [None, None]
        self.__yAxisPrimary = None
        self.__yAxisSecondary = None

        self.__open = False
        self.__redraw = False

        self.__plotMethods = [self.__plotToLeftYAxis, self.__plotToRightYAxis]
        self.__initAxes(view.getYAxis(View.YAXIS_LEFT), view.getYAxis(View.YAXIS_RIGHT))
        self.__yAxisLeftName = None
        self.__yAxisRightName = None

        #self.plot(ViewWidget.hour, ViewWidget.temperature)

    def __initYAxes(self):
        self.__yAxes[View.YAXIS_LEFT] = self.plotItem


        self.__yAxes[View.YAXIS_RIGHT] = pg.ViewBox()
        self.__yAxes[View.YAXIS_LEFT].scene().addItem(self.__yAxes[View.YAXIS_RIGHT])
        self.__yAxes[View.YAXIS_LEFT].getAxis('right').linkToView(self.__yAxes[View.YAXIS_RIGHT])
        self.__yAxes[View.YAXIS_RIGHT].setXLink(self.__yAxes[View.YAXIS_LEFT])
        self.__yAxes[View.YAXIS_LEFT].vb.sigResized.connect(self.__adjustSecondaryAxis)


    def __initAxes(self, yAxisLeft, yAxisRight):

        xAxis = DateAxisItem(orientation="bottom")
        xAxis.attachToPlotItem(self.getPlotItem())
        self.setLabel('bottom', 'Zeit', color='red', size=30)

        self.__initYAxes()
        legend = pg.LegendItem(offset=[80, 30])
        legend.setParentItem(self.__yAxes[View.YAXIS_LEFT])

        if yAxisLeft is not None and yAxisLeft.active is True:
            if yAxisLeft.measurementSize is not None:
                unit = SensorManager.getUnit(yAxisLeft.measurementSize)
            label = f"{yAxisLeft.label} / ({unit or ''})"
            self.__yAxisLeftName = yAxisLeft.label

            legend.addItem(pg.PlotDataItem(pen=ViewWidget.PEN_LEFT), yAxisLeft.label)

            self.__yAxes[View.YAXIS_LEFT].setLabel('left', label, color='red', size=30)
            self.__yAxes[View.YAXIS_LEFT].showAxis('left')
        else:
            self.__yAxes[View.YAXIS_LEFT].hideAxis('left')

        if yAxisRight is not None and yAxisRight.active is True:
            if yAxisRight.measurementSize is not None:
                unit = SensorManager.getUnit(yAxisRight.measurementSize)
            label = f"{yAxisRight.label} / ({unit or ''})"

            legend.addItem(pg.PlotDataItem(pen=ViewWidget.PEN_RIGHT), yAxisRight.label)

            self.__yAxisRightName = yAxisRight.label
            self.__yAxes[View.YAXIS_LEFT].setLabel('right', label, color='red', size=30)
            self.__yAxes[View.YAXIS_LEFT].showAxis('right')

    def __adjustSecondaryAxis(self):
        self.__yAxes[View.YAXIS_RIGHT].setGeometry(self.__yAxes[View.YAXIS_LEFT].vb.sceneBoundingRect())
        self.__yAxes[View.YAXIS_RIGHT].linkedViewChanged(
            self.__yAxes[View.YAXIS_LEFT].vb, self.__yAxes[View.YAXIS_RIGHT].XAxis)

    def __plotToLeftYAxis(self, data):
        self.__yAxes[View.YAXIS_LEFT].plot(data[0], data[1], pen="w", name=self.__yAxisLeftName)
        return

    def __plotToRightYAxis(self, data):
        curve = pg.PlotCurveItem(data[0], data[1], pen='b', name=self.__yAxisRightName)
        self.__yAxes[View.YAXIS_RIGHT].addItem(curve)
        return

    def setData(self, yAxisId, nodeId, sensorId, data):
        if nodeId not in self.__data[yAxisId]:
            self.__data[yAxisId][nodeId] = {sensorId: data}
        elif sensorId not in self.__data[yAxisId][nodeId]:
            self.__data[yAxisId][nodeId][sensorId] = data
        else:
            self.__data[yAxisId][nodeId][sensorId] = data
        self.requestRedraw()

    def addData(self, yAxisId, nodeId, sensorId, t, v):
        if nodeId not in self.__data[yAxisId]:
            self.__data[yAxisId][nodeId] = {sensorId: [t, v]}
        elif sensorId not in self.__data[yAxisId][nodeId]:
            self.__data[yAxisId][nodeId][sensorId] = [t, v]
        else:
            self.__data[yAxisId][nodeId][sensorId][0].append(t)
            self.__data[yAxisId][nodeId][sensorId][1].append(v)
        self.requestRedraw()

    def setOpen(self, visible):
        self.__open = visible is True

    def isOpen(self):
        return self.__open

    def requestRedraw(self):
        self.__redraw = True

    def drawData(self):
        if self.__redraw and self.__open:
            for yAxis in View.YAXES:
                for sensors in self.__data[yAxis].values():
                    for data in sensors.values():
                        self.__plotMethods[yAxis](data)
            self.__redraw = False
