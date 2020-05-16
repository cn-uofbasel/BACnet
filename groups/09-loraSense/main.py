from machine import ADC, RTC
import lib.lorasense as lorasense
import time

lorasense = lorasense.LoraSense()
lorasense.setLoRa()
lorasense.setWLAN("CasaSalsi", "S@lsi1968")

while True:
    lorasense.sendLoRa()
    time.sleep(1)