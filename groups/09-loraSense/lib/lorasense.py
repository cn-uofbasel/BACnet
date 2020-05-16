from machine import I2C, ADC, RTC
import bme280 as bme280
import time
import socket
from network import LoRa, WLAN

class LoraSense:

    """
    Class object that receives optional pin arguments for the SDA-pin (Serial Data), the SCL-pin (Serial Clock) and the
    pin for the photometry module. The defaults are SDA = Pin3, SCL = Pin4, Phot = Pin20 on the Pycom Extension Board v3.1.
    """
    def __init__(self, sda="P3", scl="P4", phot="P20"):
        self.rtc = RTC()
        adc = ADC()
        self.bme280 = bme280.BME280(i2c=I2C(pins=(sda, scl)))
        self.l_pin = adc.channel(pin=phot)

    """
    This procedure sets up the LoRa-connection.
    """
    def setLoRa(self, mode=LoRa.LORA, region=LoRa.EU868, tx_power=14, sf=7):
        self.lora = LoRa(mode=mode, region=region)
        self.lora.init(mode=mode, tx_power=tx_power, sf=sf)
        self.socket = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        self.socket.setblocking(False)

    def setWLAN(self, ssid, pw):
        self.wlan = WLAN(mode=WLAN.STA)
        self.wlan.connect(ssid=ssid, auth=(WLAN.WPA2, pw))
        print("Connecting", end = '')
        while not self.wlan.isconnected():
            time.sleep(1)
            print(".", end = '')
        if self.wlan.isconnected():
            print("Connected!")
        self.rtc.ntp_sync("0.ch.pool.ntp.org")
        time.sleep(1)
        print('\nRTC Set from NTP to UTC:', self.rtc.now())

    def getTimeStamp(self, offset_sec=0, offset_min=0, offset_hour=0, offset_day=0, offset_month=0, offset_year=0):
        self.rtc.ntp_sync("0.ch.pool.ntp.org")
        time = self.rtc.now()
        seconds = time[5] + offset_sec
        minutes = time[4] + offset_min
        hour = time[3] + offset_hour
        day = time[2] + offset_day
        month = time[1] + offset_month
        year = time[0] - 2000 + offset_year
        return "{}/{}/{}|{}:{}:{}|".format(day, month, year, hour, minutes, seconds)

    def getValues(self):
        t, p, h = self.bme280.values
        li = self.l_pin()
        msg = '{:.02f}|{:.02f}|{:.02f}|{:.02f}'.format(t, p, h, li / 4095 * 100)
        if self.wlan.isconnected():
            print(self.getTimeStamp(offset_hour=2) + msg)
            return self.getTimeStamp(offset_hour=2) + msg
        else:
            return msg

    def sendLoRa(self):
        self.getTimeStamp(offset_hour=2)
        self.socket.send(self.getValues())