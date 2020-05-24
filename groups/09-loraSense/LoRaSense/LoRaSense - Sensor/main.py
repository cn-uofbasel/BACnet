from lib.loralink import LoraLink
from machine import I2C, ADC, RTC
from network import WLAN
import time

LoraLink(ssid='CasaSalsi', pw='S@lsi1968', debug=1)