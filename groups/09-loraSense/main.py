from lib.loralink import LoraLink

LoraLink(mode=0, debug=1)

"""
import lib.lorasense as lorasense

lorasense = lorasense.LoraSense(mode=1, debug=1)
lorasense.setupLoRa()
lorasense.setupWLAN("SSID", "Password")
lorasense.startLoRaComm()
"""