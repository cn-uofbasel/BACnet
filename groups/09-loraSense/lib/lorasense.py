from machine import I2C, ADC, RTC
import bme280 as bme280
import time
import socket
from network import LoRa, WLAN
import _thread

class LoraSense:

    """
    Class object that receives optional pin arguments for the SDA-pin (Serial Data), the SCL-pin (Serial Clock) and the
    pin for the photometry module. The defaults are SDA = Pin3, SCL = Pin4, Phot = Pin20 on the Pycom Extension Board v3.1.
    """
    def __init__(self, sda="P3", scl="P4", als="P20", frequency=1, mode=0):
        self.mode = mode
        self.rtc = RTC()
        self.test = 1
        self.wlan = WLAN(mode=WLAN.STA)
        if (mode == 0):
            adc = ADC()
            self.bme280 = bme280.BME280(i2c=I2C(pins=(sda, scl)))
            self.l_pin = adc.channel(pin=als)
            self.frequency = frequency
        
    """
    This procedure sets up the LoRa-connection.
    """
    def setupLoRa(self, mode=LoRa.LORA, region=LoRa.EU868, tx_power=14, sf=7):
        self.lora = LoRa(mode=mode, region=region)
        self.lora.init(mode=mode, tx_power=tx_power, sf=sf)
        self.socket = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        self.socket.setblocking(False)

    def setupWLAN(self, ssid, pw):
        self.wlan.connect(ssid=ssid, auth=(WLAN.WPA2, pw))
        print("Connecting", end = '')
        while not self.wlan.isconnected():
            time.sleep(1)
            print(".", end = '')
        if self.wlan.isconnected():
            print("Connected!")
        self.rtc.ntp_sync("0.ch.pool.ntp.org")
        time.sleep(1)

    def setupUDP(self, IP, port):
        self.IP = IP
        self.port = port
        self.UDPsock = socket.socker(socket.AF_INET, socket.SOCK_DGRAM)

    def setSendFreq(self, sec):
        self.frequency = sec

    def startGetInfo(self):
        _thread.start_new_thread(self.__getInfo())

    def startSendInfo(self):
        _thread.start_new_thread(self.__sendInfo())

    def startUDP(self):
        _thread.start_new_thread(self.__communicateUDP())

    def __getTimeStamp(self, offset_sec=0, offset_min=0, offset_hour=0, offset_day=0, offset_month=0, offset_year=0):
        self.rtc.ntp_sync("0.ch.pool.ntp.org")
        time = self.rtc.now()
        seconds = self.__zfill(str(time[5] + offset_sec),2)
        minutes = time[4] + offset_min
        hour = time[3] + offset_hour
        day = time[2] + offset_day
        month = time[1] + offset_month
        year = time[0] - 2000 + offset_year
        return "{}/{}/{}|{}:{}:{}|".format(day, month, year, hour, minutes, seconds)

    def __zfill(self, s, width):
	return '{:0>{w}}'.format(s, w=width)

    def __getValues(self):
        t, p, h = self.bme280.values
        li = self.l_pin()
        msg = '{:.02f}|{:.02f}|{:.02f}|{:.02f}'.format(t, p, h, li / 4095 * 100)
        if self.wlan.isconnected():
            print(self.__getTimeStamp(offset_hour=2) + msg)
            return self.__getTimeStamp(offset_hour=2) + msg
        else:
            return msg

    def __sendLoRa(self):
        self.__getTimeStamp(offset_hour=2)
        self.socket.send(self.__getValues())

    def __sendInfo(self):
        while True:
            self.__sendLoRa()
            time.sleep(self.frequency)

    def __getInfo(self):
        while True:
            info = self.socket.recv(52).decode("utf-8")
            print(self.socket.recv(52).decode("utf-8"))
            time.sleep(1)
            
    def __processInfo(self, info):
        info = info.split("|")
        if (info[0] == "freq"):
            self.frequency = int(info[1])
            print("New frequency set: {}".format(int(info[1])))

    def __communicateUDP(self):
        while True:
            data, addr = self.UDPsock.recvfrom(52)
            