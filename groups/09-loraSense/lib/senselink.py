from machine import I2C, ADC, RTC
import bme280 as bme280
import time
import select
import sys
from lora_feed_layer import Lora_Feed_Layer
import os
import _thread

class SenseLink:
    """
    Class object that receives optional pin arguments for the SDA-pin (Serial Data), the SCL-pin (Serial Clock) and the
    pin for the photometry module. The defaults are SDA = Pin3, SCL = Pin4, Phot = Pin20 on the Pycom Extension Board v3.1.
    """
    def __init__(self, sda="P3", scl="P4", als="P20", frequency=5, mode=0, debug=0, feed_layer):
        if not (mode == 0 or mode == 1):
            self.__exitError("Please initialize this module in either mode 0 or mode 1.")
        self.feed_layer = feed_layer
        self.fid = self.feed_layer.get_sensor_feed_fid()
        self.cfid = self.feed_layer.get_control_feed_fid()
        self.mode = mode
        self.rtc = RTC()
        self.debug = debug
        self.frequency = frequency
        self.__debug("Sensor Feed ID is: " + str(self.fid))
        self.__debug("Control Feed ID is: " + str(self.cfid))
        if (mode == 0):
            self.bme280 = bme280.BME280(i2c=I2C(pins=(sda, scl)))
            self.l_pin = ADC().channel(pin=als)
            _thread.start_new_thread(self.__sendData, ())

    def callback(self, val):
        self.frequency = val

    def __getTimeStamp(self, offset_sec=0, offset_min=0, offset_hour=0, offset_day=0, offset_month=0, offset_year=0):
        if self.wlan.isconnected():
            self.rtc.ntp_sync("0.ch.pool.ntp.org")
            time = self.rtc.now()
            seconds = self.__zfill(str(time[5] + offset_sec),2)
            minutes = self.__zfill(str(time[4] + offset_min),2)
            hour = self.__zfill(time[3] + offset_hour,2)
            day = self.__zfill(time[2] + offset_day,2)
            month = self.__zfill(time[1] + offset_month,2)
            year = time[0] - 2000 + offset_year
            return "{}/{}/{} {}:{}:{}".format(day, month, year, hour, minutes, seconds)
        else:
            return "notime"

    def __zfill(self, s, width):
	    return '{:0>{w}}'.format(s, w=width)

    def __sendData(self):
        while True:
            self.feed_layer.create_event(fid, "['{}', '{}', '{}', '{}', '{}']".format(self.__getValues()))
            time.sleep(self.frequency)

    def __getValues(self):
        t, p, h = self.bme280.values
        li = self.l_pin()
        return self.__getTimeStamp(offset_hour=2), t, p, h, li / 4095 * 100

    def __exitError(self, str):
        print('\033[91m' + "Error: " + str + '\x1b[0m')
        sys.exit()
    
    def __debug(self, str):
        if self.debug == 1:
            print('\033[93m' + "Debug: " + str + '\x1b[0m')