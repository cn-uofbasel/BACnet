

class Tools:
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