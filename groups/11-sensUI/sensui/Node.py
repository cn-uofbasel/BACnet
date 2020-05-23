class Node(object):
    POSITION_LATITUDE = "Latitude"
    POSITION_LONGITUDE = "Longitude"
    POSITION_ELEVATION = "Elevation"
    POSITION = [POSITION_LATITUDE, POSITION_LONGITUDE, POSITION_ELEVATION]

    def __init__(self, nodeId):
        self.id = nodeId
        self.__name = None
        self.interval = 300
        self.position = {
            Node.POSITION_LATITUDE: 47.559113,
            Node.POSITION_LONGITUDE: 7.583425,
            Node.POSITION_ELEVATION: 300.
        }
        self.__sensors = {}

    @property
    def name(self):
        if self.__name is None:
            return self.id
        return self.__name

    @name.setter
    def name(self, name):
        if name is not None:
            self.__name = name

    def setSensor(self, id, active):
        if active:
            self.__sensors[id] = True
        elif id in self.__sensors:
            del self.__sensors[id]

    def getSensors(self):
        return self.__sensors