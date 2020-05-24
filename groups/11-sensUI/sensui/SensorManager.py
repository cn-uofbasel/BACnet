

class SensorManager:
    class Sensor:

        def __init__(self, id, name, sType, unit):
            self.id = id
            self.name = name
            self.sType = sType
            self.unit = unit

    sensorTypes = {
        "T_celcius": Sensor("T_celcius", "Temperatur", "T", "°C"),
        "P_bar": Sensor("P_bar", "Luftdruck", "P", "bar"),
        "rH": Sensor("rH", "Luftfeuchtigkeit", "rH", "%"),
        "J_lumen": Sensor("J_lumen", "Lichtstrom", "J", "lm")
    }

    INDEX_TIMESTAMP = 0
    INDEX_VALUE = 1

    def __init__(self, callbackDataAdded):
        self.__callbackDataAdded = callbackDataAdded
        '''
            values = {
                nodeId = {
                    sensorId = [
                        [t1, t2, t3],
                        [v1, v2, v3]
                    ]
                }
            }

        '''
        self.__values = {}

    def addData(self, nodeId, sensorId, value, timestamp):
        if value is None or timestamp is None:
            return

        if nodeId not in self.__values:
            self.__values[nodeId] = {sensorId: [[value], [timestamp]]}
        elif sensorId not in self.__values[nodeId]:
            self.__values[nodeId][sensorId] = [[value], [timestamp]]
        else:
            self.__values[nodeId][sensorId][SensorManager.INDEX_TIMESTAMP].append(timestamp)
            self.__values[nodeId][sensorId][SensorManager.INDEX_VALUE].append(value)

        # TODO: Fire event
        self.__callbackDataAdded(nodeId, sensorId, self.__values)

    def getData(self, nodeId, sensorId):
        if nodeId not in self.__values or sensorId not in self.__values[nodeId]:
            return None

        return self.__values[nodeId][sensorId]
