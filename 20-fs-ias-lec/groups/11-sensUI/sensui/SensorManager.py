

class SensorManager:
    class Sensor:

        def __init__(self, id, name, sType, unit):
            self.id = id
            self.name = name
            self.sType = sType
            self.unit = unit

    sensorTypes = {
        "T_celcius": Sensor("T_celcius", "Temperatur", "T", "°C"),
        "P_hPa": Sensor("P_hPa", "Luftdruck", "P", "hPa"),
        "rH": Sensor("rH", "Luftfeuchtigkeit", "rH", "%"),
        "J_lumen": Sensor("J_lumen", "Lichtstrom", "J", "%")
    }

    INDEX_TIMESTAMP = 0
    INDEX_VALUE = 1

    def __init__(self, callbackDataUpdated, callbackNodesUpdated):
        self.__callbackDataUpdated = callbackDataUpdated
        self.__callbackNodesUpdated = callbackNodesUpdated
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
            self.__values[nodeId] = {sensorId: [[timestamp], [value]]}
            self.__callbackNodesUpdated(nodeId)
        elif sensorId not in self.__values[nodeId]:
            self.__values[nodeId][sensorId] = [[timestamp], [value]]
        else:
            self.__values[nodeId][sensorId][SensorManager.INDEX_TIMESTAMP].append(timestamp)
            self.__values[nodeId][sensorId][SensorManager.INDEX_VALUE].append(value)

        # TODO: Fire event
        self.__callbackDataUpdated(nodeId, sensorId)

    def dataReference(self, nodeId, sensorId):

        if nodeId not in self.__values:
            data = [[], []]
            self.__values[nodeId] = {sensorId: data}
        elif sensorId not in self.__values[nodeId]:
            data = [[], []]
            self.__values[nodeId][sensorId] = data
        else:
            data = self.__values[nodeId][sensorId]
        return data


    def getData(self, nodeId, sensorId):
        if nodeId not in self.__values or sensorId not in self.__values[nodeId]:
            return None

        return self.__values[nodeId][sensorId]
