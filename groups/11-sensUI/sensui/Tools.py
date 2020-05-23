

class Tools:
    class Sensor:

        def __init__(self, id, name, symbol, unit):
            self.id = id
            self.name = name
            self.symbol = symbol
            self.unit = unit

    sensorTypes = {
        "T_celcius": Sensor("T_celcius", "Temperatur", "T", "°C"),
        "P_bar": Sensor("P_bar", "Druck", "P", "bar"),
        "rH": Sensor("rH", "Luftfeuchtigkeit", "rH", "%"),
        "J_lumen": Sensor("J", "Lichtstrom", "J", "lm")
    }