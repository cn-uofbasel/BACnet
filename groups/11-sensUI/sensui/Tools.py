

class Tools:
    class Quantity:

        def __init__(self, id, name, symbol, unit):
            self.id = id
            self.name = name
            self.symbol = symbol
            self.unit = unit

    measurementSizes = {
        "T_celcius": Quantity("T_celcius", "Temperatur", "T", "°C"),
        "P_bar": Quantity("P_bar", "Druck", "P", "bar"),
        "rH": Quantity("rH", "Luftfeuchtigkeit", "rH", "%"),
        "J_lumen": Quantity("J", "Lichtstrom", "J", "lm")
    }