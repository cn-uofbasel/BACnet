import os
import re
import socket
import threading
import netifaces as ni
from logic.file_handler import make_dirs, get_newest_datetime, zip_articles, unzip_articles, DIR_TRANSFER
from datetime import datetime

class LANServer:

    def __init__(self):
        self.default_port = 55111
        self.buff_size = 1024
        self.server_timeout = 5
        self.running = False
        self.address = (-1, -1)
        self.socket = None
        self.thread_running = False

    def start_server(self):
        x = ni.gateways() 
        y = x['default'][2][1] 
        ip = ni.ifaddresses(y)[ni.AF_INET][0]['addr']
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.server_timeout)
        self.address = (ip, self.default_port)
        self.socket.bind(self.address)
        self.socket.listen(1)
        self.running = True
        self.thread_running = True

        while self.running:
            try:
                (client_socket, client_addr) = self.socket.accept()
                msg = client_socket.recv(4096)

                if msg.decode() == "None":
                    date_time = None
                else:
                    try:
                        date_time = datetime.fromisoformat(msg.decode())
                    except Exception:
                        print("Received time is not in iso format.")
                        client_socket.close()
                        continue
                try:
                    path = zip_articles(date_time)
                    if path == None:
                        client_socket.close()
                        continue
                    else:
                        file = open(path, 'rb')
                except Exception:
                    print("Failed to open or compress files for sending to client.")
                    client_socket.close()
                    continue
                while True:
                    data = file.read(self.buff_size)
                    if not data:
                        break
                    client_socket.send(data)
                file.close()
                client_socket.close()
                continue
                # self.running = False

            except socket.timeout:
                self.socket.listen(1)
            except socket.error as exc:
                print("Socket exception: %s" % exc)
                self.socket.close()
                break
            except Exception:
                print("An error occurred while listening to client.")
                self.socket.close()
                break
        self.thread_running = False

    def start_server_threaded(self):
        self.thread = threading.Thread(target=self.start_server)
        self.thread.start()

    def stop_server(self):
        self.running = False

    def keep_alive(self):
        self.running = True

    def get_IP(self):
        return str(self.address[0])

    def get_port(self):
        return str(self.address[1])

    def is_running(self):
        return self.thread_running