class Node(object):
    POSITION_LATITUDE = "Latitude"
    POSITION_LONGITUDE = "Longitude"
    POSITION_ELEVATION = "Elevation"
    POSITION = [POSITION_LATITUDE, POSITION_LONGITUDE, POSITION_ELEVATION]

    SENSOR_TEMPERATURE = "Temperature"
    SENSOR_HUMIDITY = "Humidity"
    SENSOR_PRESSURE = "Pressure"
    SENSOR_BRIGHTNESS = "Brightness"
    SENSORS = [SENSOR_TEMPERATURE, SENSOR_PRESSURE, SENSOR_HUMIDITY, SENSOR_BRIGHTNESS]

    def __init__(self, nodeId):
        self.id = nodeId
        self.name = None
        self.interval = 300
        self.position = {
            Node.POSITION_LATITUDE: 47.559113,
            Node.POSITION_LONGITUDE: 7.583425,
            Node.POSITION_ELEVATION: 300.
        }
        self.sensors = {
            Node.SENSOR_TEMPERATURE: False,
            Node.SENSOR_PRESSURE: False,
            Node.SENSOR_HUMIDITY: False,
            Node.SENSOR_BRIGHTNESS: False
        }

    @property
    def name(self):
        if self.__name is None:
            return self.id
        return self.__name

    @name.setter
    def name(self, name):
        if name is not None:
            self.__name = name
