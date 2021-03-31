from machine import I2C, ADC, RTC
from network import WLAN
import bme280 as bme280
import time
import sys
import pycom
import _thread


class SenseLink:
    """
    Class object that receives optional pin arguments for the SDA-pin (Serial Data), the SCL-pin (Serial Clock) and the
    pin for the photometry module. The defaults are SDA = Pin3, SCL = Pin4, Phot = Pin20 on the Pycom Extension Board v3.1.
    """
    def __init__(self, sda="P3", scl="P4", als="P20", ssid="", pw="", frequency=5, debug=0, feed_layer=None):
        self.feed_layer = feed_layer
        self.fid = self.feed_layer.get_sensor_feed_fid()
        self.cfid = self.feed_layer.get_control_feed_fid()
        self.rtc = RTC()
        self.debug = debug
        self.lastsent = 0
        self.switch = True
        self.wlan = WLAN(mode=WLAN.STA)
        self.connectWlan(ssid=ssid, pw=pw)
        self.subscribe_state = self.feed_layer.subscribe_control_feed(self.callback)
        self.frequency = frequency
        self.__debug("Sensor Feed ID is: " + str(self.fid))
        self.__debug("Control Feed ID is: " + str(self.cfid))
        try:
            self.bme280 = bme280.BME280(i2c=I2C(pins=(sda, scl)))
        except:
            self.__exitError("BME280 not recognized. Please check the connections.", loop=True, col=1)
        self.l_pin = ADC().channel(pin=als)

    def getFid(self):
        return self.fid

    def getCfid(self):
        return self.cfid

    def switchState(self):
        return self.switch

    def callback(self, event):
        self.__debug("Event received: {}".format(event))
        self.setFrequency(int(event))

    def setFrequency(self, val):
        self.__debug("Frequency changed to {}".format(val))
        self.frequency = val
    
    def getFrequency(self):
        return self.frequency

    def createEvent(self):
        self.vals = self.__getValues()
        event = "['{}', '{:.2f}', '{:.2f}', '{:.2f}', '{:.2f}']".format(self.vals[0], self.vals[1], self.vals[2], self.vals[3], self.vals[4])
        self.__debug("Creating event: " + event)
        return event
    
    def connectWlan(self, ssid, pw, timeout = 5):
        self.wlan.connect(ssid=ssid, auth=(WLAN.WPA2, pw))
        counter = 0
        self.__debug("Connecting to WLAN", newline=False)
        while not self.wlan.isconnected():
            counter = counter + 1
            if (counter == timeout):
                self.__exitError("Unable to connect (timed out).", loop=True, col=0)
                return
            time.sleep(1)
            self.__debug(".", newline=False)
        if self.wlan.isconnected():
            self.__debug(" Connected! ", newline=False)
        counter = 0
        self.rtc.ntp_sync("0.ch.pool.ntp.org")
        self.__debug("Connecting to NTP server ", newline=False)
        while not self.rtc.synced():
            counter = counter + 1
            if (counter == timeout):
                self.__exitError("Unable to connect (timed out).", loop=True, col=0)
                return
            self.__debug(".", newline=False)
            time.sleep(1)
        self.__debug(" Completed!", newline=False)
        self.switch = False
        self.__debug("Connection established and time data received.")

    def __getTimeStamp(self, offset_sec=0, offset_min=0, offset_hour=0, offset_day=0, offset_month=0, offset_year=0):
        if self.wlan.isconnected():
            self.rtc.ntp_sync("0.ch.pool.ntp.org")
            time = self.rtc.now()
            seconds = self.__zfill(str(time[5] + offset_sec), 2)
            minutes = self.__zfill(str(time[4] + offset_min), 2)
            hour = self.__zfill(time[3] + offset_hour, 2)
            day = self.__zfill(time[2] + offset_day, 2)
            month = self.__zfill(time[1] + offset_month, 2)
            year = time[0] - 2000 + offset_year
            return "{}/{}/{} {}:{}:{}".format(day, month, year, hour, minutes, seconds)
        else:
            return "notime"

    def __zfill(self, s, width):
	    return '{:0>{w}}'.format(s, w=width)

    def updateInfo(self):
        while True:
            self.__debug(self.__getTimeStamp() + " Switch state: {}".format(self.switch))
            self.currentpack = self.__getValues()
            time.sleep(1)
        
    def __getValues(self):
        try:
            t, p, h = self.bme280.values
            li = self.l_pin()
            return self.__getTimeStamp(offset_hour=2), t, p, h, li / 4095 * 100
        except:
            self.__exitError("BME280 not recognized. Please check the connections.", loop=True)

    def __exitError(self, str, col, loop=False):
        print('\033[91m' + "Error: " + str + '\x1b[0m')
        pycom.heartbeat(False)
        if col == 0:
            pycom.rgbled(0x7f7f00)
        elif col == 1:
            pycom.rgbled(0x7f0000)
        if loop:
            while True:
                pass
        else:
            sys.exit()
    
    def __debug(self, str, newline=True):
        if newline:
            print('\033[93m' + "SenseLink | Debug: " + str + '\x1b[0m')
        else:
            print('\033[93m' + str + '\x1b[0m', end='')