from sensui.Manager import Manager
from sensui.View import View
from sensui.ViewWidget import ViewWidget

class ViewManager(Manager):

    def __init__(self, views):
        super().__init__(views)
        self.__widgets = {}
        '''
            sensorLookup = {
                nodeId = {
                    sensorId = [
                        viewId
                    ]
                }
            }
        '''
        self.__sensorLookup = {}

    def addToSensorLookup(self, view):
        for yAxisId in View.YAXES:
            for nodeId, sensorId in view.getYAxis(yAxisId).sensors.items():
                if nodeId not in self.__sensorLookup:
                    self.__sensorLookup[nodeId] = {sensorId: [view.id]}
                elif sensorId not in self.__sensorLookup[nodeId]:
                    self.__sensorLookup[nodeId][sensorId] = [view.id]
                else:
                    self.__sensorLookup[nodeId][sensorId].append(view.id)

    def removeFromSensorLookup(self, view):
        for sensors in self.__sensorLookup.values():
            if view.id in sensors:
                del sensors[view.id]

    def lookupViews(self, nodeId, sensorId):
        if nodeId in self.__sensorLookup:
            if sensorId in self.__sensorLookup[nodeId]:
                return self.__sensorLookup[nodeId][sensorId]

    def open(self, viewId):
        if not self.containsId(viewId):
            return

        if viewId in self.__widgets:
            widget = self.__widgets[viewId]

        else:
            view = self.get(viewId)
            widget = ViewWidget(view)
            self.__widgets[viewId] = widget
            self.addToSensorLookup(view)
        return widget

    def updateWidgets(self):
        for widget in self.__widgets.values():
            widget.drawData()

    def callbackUpdate(self, nodeId, sensorId):
        views = self.lookupViews(nodeId, sensorId)
        if views is None:
            return
        for viewId in views:
            if viewId not in self.__widgets:
                continue
            self.__widgets[viewId].requestRedraw()