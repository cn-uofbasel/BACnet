from machine import I2C, ADC, RTC
import bme280 as bme280
import time
import socket
from network import LoRa, WLAN
import select
import sys
import _thread          

class LoraSense:
    """
    Class object that receives optional pin arguments for the SDA-pin (Serial Data), the SCL-pin (Serial Clock) and the
    pin for the photometry module. The defaults are SDA = Pin3, SCL = Pin4, Phot = Pin20 on the Pycom Extension Board v3.1.
    """
    def __init__(self, sda="P3", scl="P4", als="P20", frequency=1, mode=0, debug=0):
        if not (mode == 0 or mode == 1):
            self.__exitError("Please initialize this module in either mode 0 or mode 1.")
        self.mode = mode
        self.rtc = RTC()
        self.debug = debug
        self.wlan = WLAN(mode=WLAN.STA)
        self.UDPactive = False
        self.loraActive = False
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
        self.lorasocket = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        self.lorasocket.setblocking(False)
        self.loraActive = True

    def setupWLAN(self, ssid, pw, timeout=60):
        self.wlan.connect(ssid=ssid, auth=(WLAN.WPA2, pw))
        counter = 0
        print("Connecting to WLAN", end = '')
        while not self.wlan.isconnected():
            counter = counter + 1
            if (counter == timeout):
                print("Unable to connect (timed out).")
                return
            time.sleep(1)
            print(".", end = '')
        if self.wlan.isconnected():
            print(" Connected!")
        counter = 0
        self.rtc.ntp_sync("0.ch.pool.ntp.org")
        print("Connecting to NTP server ", end = '')
        while not self.rtc.synced():
            counter = counter + 1
            if (counter == timeout):
                print("Unable to connect (timed out).")
                return
            print(".", end = '')
            time.sleep(1)
        print(" Completed!")

    def setupUDP(self, IP, port):
        self.__debug("DEBUG: STARTING UDP -> IP: {}  Port: {}$".format(IP, port))
        if not self.wlan.isconnected():
            self.__exitError("Please establish a WLAN connection first.")
        if (self.mode == 0):
            print("UDP can only be set up in mode 1.")
        elif (self.mode == 1):
            self.UDPaddress = (IP, port)
            print("Establishing a UDP connection.. to {}".format(self.UDPaddress[0]))
            self.UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.UDPsocket.connect(self.UDPaddress)
            self.UDPsocket.sendto("Establish".encode("utf-8"), self.UDPaddress)
            self.UDPactive = True
        else:
            print("LoRa mode must be either 0 or 1.s")

    def setSendFreq(self, sec):
        self.frequency = sec

    def startCommunication(self):
        if self.mode == 0:
            self.__commInMode0()
        elif self.mode == 1:
            self.__commInMode1()

    def __createSocketList(self):
        if (self.loraActive and self.UDPactive):
            return [self.lorasocket, self.UDPsocket]
        elif (self.loraActive and not self.UDPactive):
            return [self.lorasocket]
        elif (not self.loraActive and self.UDPactive):
            return [self.UDPsocket]
        else:
            self.__exitError("Please establish a LoRa or a UDP connection before starting communication.")
                
    def __commInMode0(self):
        self.sockets = self.__createSocketList()
        self.__debug("Communication in mode 0 initiated. Sockets = {}".format(self.sockets))
        while True:
            readIn, writeOut, excep = select.select(self.sockets, self.sockets, [])
            for insocket in readIn:
                if insocket == self.lorasocket:
                    info = insocket.recv(52)
                    print(info)
                    self.__processInfo(info)
                elif insocket == self.UDPsocket:
                    info = insocket.recv(52)
                    print(info)
                    insocket.send(info)
            for outsocket in writeOut:
                if outsocket == self.lorasocket:
                    print(self.__getValues())
                    self.lorasocket.send(self.__getValues())
                    time.sleep(self.frequency)
                    

    def __commInMode1(self):
        self.sockets = self.__createSocketList()
        self.__debug("Communication in mode 1 initiated. Sockets = {}".format(self.sockets))
        while True:
            readIn, writeOut, excep = select.select(self.sockets, self.sockets, [])
            for insocket in readIn:
                if insocket == self.lorasocket:
                    info = insocket.recv(52)
                    insocket.send(info)
                    self.__sendUDP(info)
                elif insocket == self.UDPsocket:
                    info = insocket.recv(52)
                    self.lorasocket.send(info)
                    
                

    def __getTimeStamp(self, offset_sec=0, offset_min=0, offset_hour=0, offset_day=0, offset_month=0, offset_year=0):
        self.rtc.ntp_sync("0.ch.pool.ntp.org")
        time = self.rtc.now()
        seconds = self.__zfill(str(time[5] + offset_sec),2)
        minutes = self.__zfill(str(time[4] + offset_min),2)
        hour = self.__zfill(time[3] + offset_hour,2)
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
            if (self.debug == 1):
                print(self.__getTimeStamp(offset_hour=2) + msg)
            return self.__getTimeStamp(offset_hour=2) + msg
        else:
            if (self.debug == 1):
                print(msg)
            return msg

    def __sendLoRa(self):
        self.__getTimeStamp(offset_hour=2)
        self.lorasocket.send(self.__getValues())

    def __sendInfo(self):
        while True:
            self.__sendLoRa()
            time.sleep(self.frequency)

    def __getInfo(self):
        try:
            while True:
                info = self.lorasocket.recv(52)
                if self.UDPactive:
                    self.__sendUDP(info)
                if self.debug == 1: print(info)
                time.sleep(1)
        except UnicodeError:
            pass
            
    def __processInfo(self, info):
        try:
            info = info.decode("utf-8").split("|")
            if (info[0] == "freq"):
                self.frequency = int(info[1])
                print("New frequency set: {}".format(int(info[1])))
        except UnicodeError:
            pass

    def showIP(self):
        if self.wlan.isconnected():
            print("IP: {}".format(self.wlan.ifconfig()[0]))
        else:
            print("You need to establish an internet connection first.")

    def __sendUDP(self, msg):
        self.UDPsocket.sendto(msg, self.UDPaddress)

    def __getUDP(self):
        while True:
            data, ip = self.UDPsocket.recvfrom(1024)
            if data:
                print("Data: " + data.decode())

    def __exitError(self, str):
        print('\033[91m' + "Error: " + str + '\x1b[0m')
        sys.exit()
    
    def __debug(self, str):
        if self.debug == 1:
            print('\033[93m' + "Debug: " + str + '\x1b[0m')