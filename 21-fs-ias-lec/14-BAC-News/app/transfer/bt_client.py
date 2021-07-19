import os
import re
import socket
import subprocess
import sys
import threading
from logic.file_handler import get_newest_datetime, zip_articles, unzip_articles, DIR_TRANSFER
from datetime import datetime
import platform

class bt_client:

    def __init__(self):
        self.server_mac_address = None
        self.port = 4
        self.socket = None
        self.running = False
        self.connect_success = False    # did client manaage to connect with server and receive the data?
        self.recv_success = False   # did client receive all data successfully?

    def start_client(self, server_mac_address): # address client wants to connect to (only MAC-address, port is fix)
        #####address = input("Enter the xx:xx:xx:xx:xx:xx address of the device you'd like to get your articles from: ")
        print("trying to connect...")

        self.server_mac_address = server_mac_address
        self.socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)

        # try to connect to server
        i = 0
        while i < 3: # try connecting 3 times
            try:
                self.socket.connect((self.server_mac_address, self.port))
                self.connect_success = True
                i = 3
            except:
                i = i + 1
                pass
        if self.connect_success is False: # client couldn't connect with server
            return
        self.running = True
        try:
            date_time = get_newest_datetime()
            if date_time is None:
                self.socket.send("None".encode())
            else: 
                self.socket.send(get_newest_datetime().isoformat().encode())
            data = self.socket.recv(1024)
            if data == "???!no_new_data_for_you!???".encode():
                print("no new articles for you")
                return
            if not os.path.exists(DIR_TRANSFER):
                os.makedirs(DIR_TRANSFER)
            f = open(DIR_TRANSFER + "/received_articles.zip", 'wb')
            f.write(data)
        except:
            print("something went wrong")
            self.socket.close()
            self.running = False
            return

        try:
            data = self.socket.recv(1024)
            while not data == "!?L=C)(JZB?)K)=FJ(W".encode():
                f.write(data)
                data = self.socket.recv(1024)
            f.close()
            self.socket.close() # everything received, can close now
            self.running = False
            unzip_articles(DIR_TRANSFER + "/received_articles.zip")

        except:
            print("there was a problem while receiving articles...closing connection")
            f.close()
            self.socket.close()
        
        self.recv_success = True    # client received all data successfully

    def set_address(self, address):
        self.address = address

    def stop_server(self):
        if self.running:
            if self.socket != None:
                self.socket.close()
                self.running = False
        print("closed connection")