from lib.loralink import LoraLink
from machine import I2C, ADC, RTC
from deleter import Deleter
from network import WLAN
import time
import os

LoraLink(ssid='CasaSalsi', pw='S@lsi1968', debug=1)
#Deleter()