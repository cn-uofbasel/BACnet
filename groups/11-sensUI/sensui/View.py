

class View (object):
    YAXIS_LEFT = 0
    YAXIS_RIGHT = 1
    YAXES = [YAXIS_LEFT, YAXIS_RIGHT]

    class YAxisLayout (object):
        def __init__(self, axisId, label=None, active=False, measurementSize=None):
            self.id = axisId
            self.label = label
            self.active = active
            self.measurementSize = measurementSize
            self.sensors = {}

        def clearSensors(self):
            self.sensors = {}

        def setSensor(self, nodeId, sensorId):
            if nodeId in self.sensors:
                if sensorId in self.sensors[nodeId]:
                    return
                self.sensors[nodeId].append(sensorId)
            else:
                self.sensors[nodeId] = (sensorId)

    def __init__(self, viewId=None, name=None):
        if viewId is None:
            import uuid
            self.id = str(uuid.uuid4())
        else:
            self.id = viewId

        if name is None:
            self.name = str(self.id)
        else:
            self.name = name
        self.active = False
        self.__yAxes = [View.YAxisLayout(View.YAXIS_LEFT), View.YAxisLayout(View.YAXIS_RIGHT)]

    def getYAxis(self, id):
        if id is None:
            return None
        return self.__yAxes[id]

    def setYAxis(self, axis):
        if axis is None:
            return

        self.__yAxes[axis.id] = axis