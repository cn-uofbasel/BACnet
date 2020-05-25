import pyqtgraph as pg
from lib import View


class ViewWidget (pg.PlotWidget):

    hour = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]
    temperature2 = [34, 35, 31, 30, 29, 34, 21, 31, 35, 50]

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

        self.__plotMethods = [self.__plotToLeftYAxis, self.__plotToRightYAxis]
        self.__initAxes(view.getYAxis(View.YAXIS_LEFT), view.getYAxis(View.YAXIS_RIGHT))

        #self.plot(ViewWidget.hour, ViewWidget.temperature)

    def __initYAxes(self):
        self.__yAxes[View.YAXIS_LEFT] = self.plotItem

        self.__yAxes[View.YAXIS_RIGHT] = pg.ViewBox()
        self.__yAxes[View.YAXIS_LEFT].scene().addItem(self.__yAxes[View.YAXIS_RIGHT])
        self.__yAxes[View.YAXIS_LEFT].getAxis('right').linkToView(self.__yAxes[View.YAXIS_RIGHT])
        self.__yAxes[View.YAXIS_RIGHT].setXLink(self.__yAxes[View.YAXIS_LEFT])
        self.__yAxes[View.YAXIS_LEFT].vb.sigResized.connect(self.__adjustSecondaryAxis)


    def __initAxes(self, yAxisLeft, yAxisRight):
        self.setLabel('bottom', 'Zeit', color='red', size=30)

        self.__initYAxes()

        if yAxisLeft is not None and yAxisLeft.active is True:
            self.__yAxes[View.YAXIS_LEFT].setLabel('left', yAxisLeft.label, color='red', size=30)
            self.__yAxes[View.YAXIS_LEFT].showAxis('left')
        else:
            self.__yAxes[View.YAXIS_LEFT].hideAxis('left')

        if yAxisRight is not None and yAxisRight.active is True:
            self.__yAxes[View.YAXIS_LEFT].setLabel('right', yAxisRight.label, color='red', size=30)
            self.__yAxes[View.YAXIS_LEFT].showAxis('right')

    def __adjustSecondaryAxis(self):
        self.__yAxes[View.YAXIS_RIGHT].setGeometry(self.__yAxes[View.YAXIS_LEFT].vb.sceneBoundingRect())
        self.__yAxes[View.YAXIS_RIGHT].linkedViewChanged(
            self.__yAxes[View.YAXIS_LEFT].vb, self.__yAxes[View.YAXIS_RIGHT].XAxis)

    def __plotToLeftYAxis(self, data):
        self.__yAxes[View.YAXIS_LEFT].plot(data[0], data[1])
        return

    def __plotToRightYAxis(self, data):
        curve = pg.PlotCurveItem(data[0], data[1], pen='b')
        curve.sigPlotChanged.connect(lambda: print("Changed"))
        self.__yAxes[View.YAXIS_RIGHT].addItem(curve)
        return

    def setData(self, yAxisId, nodeId, sensorId, data):
        if nodeId not in self.__data[yAxisId]:
            self.__data[yAxisId][nodeId] = {sensorId: data}
        elif sensorId not in self.__data[yAxisId][nodeId]:
            self.__data[yAxisId][nodeId][sensorId] = data
        else:
            self.__data[yAxisId][nodeId][sensorId] = data
        self.drawData()

    def addData(self, yAxisId, nodeId, sensorId, t, v):
        if nodeId not in self.__data[yAxisId]:
            self.__data[yAxisId][nodeId] = {sensorId: [t, v]}
        elif sensorId not in self.__data[yAxisId][nodeId]:
            self.__data[yAxisId][nodeId][sensorId] = [t, v]
        else:
            self.__data[yAxisId][nodeId][sensorId][0].append(t)
            self.__data[yAxisId][nodeId][sensorId][1].append(v)
            print(self.__data[yAxisId][nodeId][sensorId][0])
            print(self.__data[yAxisId][nodeId][sensorId][1])
        self.drawData()

    def drawData(self):
        for yAxis in View.YAXES:
            for sensors in self.__data[yAxis].values():
                for data in sensors.values():
                    self.__plotMethods[yAxis](data)
