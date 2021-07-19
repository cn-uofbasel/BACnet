import os
import re
import socket
import threading
from logic.file_handler import make_dirs, get_newest_datetime, zip_articles, unzip_articles, DIR_TRANSFER
from datetime import datetime

class LANClient:
    def __init__(self):
        self.default_port = 55111
        self.buff_size = 1024
        self.client_timeout = 15
        self.server_addr = (-1, -1)
        self.client_socket = None

    def start_client(self, ip):

        self.server_addr = (ip, self.default_port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.settimeout(self.client_timeout)
        # any client ip and port
        self.client_addr = ('', 0)
        # bind server address to port
        self.client_socket.bind(self.client_addr)
        # connect to server
        try:
            self.client_socket.connect(self.server_addr)
            newest_datetime = get_newest_datetime()
            if not newest_datetime:
                self.client_socket.send("None".encode())
            else:
                self.client_socket.send(get_newest_datetime().isoformat().encode())
            try:
                data = self.client_socket.recv(self.buff_size)
                if not data:
                    print("User does not have new articles.")
                    self.client_socket.close()
                    return 0
                make_dirs()
                file = open(DIR_TRANSFER + "/received_articles.zip", 'wb')
                file.write(data)
            except Exception:
                print("Failed to create zip file for received data.")
                return 0
            while True:
                data = self.client_socket.recv(self.buff_size)
                print(data)
                if not data:
                    break
                file.write(data)
            file.close()
            unzip_articles(DIR_TRANSFER + "/received_articles.zip")
            self.client_socket.close()
            return 1
        except socket.error as exc:
            print("Socket exception: %s" % exc)
            self.client_socket.close()
            return 0
        except Exception:
            print("Something went wrong sending newest date_time")
            return 0

    def start_client_threaded(self, ip):
        thread = threading.Thread(target=self.start_client(ip))
        thread.start()