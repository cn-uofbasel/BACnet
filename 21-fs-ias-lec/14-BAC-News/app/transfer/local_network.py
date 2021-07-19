import os
import re
import socket
import sys
import threading
from logic.file_handler import make_dirs, get_newest_datetime, zip_articles, unzip_articles, DIR_TRANSFER
from datetime import datetime

DEFAULT_PORT = 55111
BUFFER_SIZE = 1024
SERVER_TIMEOUT = 15
CLIENT_TIMEOUT = 10

def get_devices():
    with os.popen('arp -a') as f:
        data = f.read()

    devices = []
    if sys.platform == "win32" or sys.platform == "cygwin":
        for line in data.split('\n'):
            line = line[2:] # split off first two spaces
            #line = ' '.join(line.split())
            parts = line.split()
            
            try:
                if len(parts) >= 3:
                    device = { "name" : "unknown", "ip" : parts[0], "mac" : parts[1] }
                    ip_start = device["ip"].split('.')[0]
                    ip_end = device["ip"].split('.')[-1]
                    if (ip_start != '192' and ip_start != '172' and ip_start != '10') or ip_end == '1' or ip_end == '255' or not parts[0][0].isnumeric():
                        continue
                    devices.append(device)
            except Exception:
                print("Something went wrong reading arp table entry.")
    else:
        for line in data.split('\n'):
            parts = line.split(' ')
            try:
                if len(parts) >= 4:
                    device = { "name" : parts[0], "ip" : re.sub('[()]', '', parts[1]), "mac" : parts[3] }
                    ip_start = device["ip"].split('.')[0]
                    ip_end = device["ip"].split('.')[-1]
                    if (ip_start != '192' and ip_start != '172' and ip_start != '10') or ip_end == '1' or ip_end == '255':
                        continue
                    devices.append(device)
            except Exception:
                print("Something went wrong reading arp table entry.")
        
    return devices

def print_devices(result):
    print("----------------------------------------------------------------------\nIP Address\t\tMAC Address\t\tDevice Name\n----------------------------------------------------------------------")
    for i in result:
        print("{}\t\t{}\t({})".format(i["ip"], i["mac"], i["name"]))

def start_client(ip):

    server_addr = (ip, DEFAULT_PORT)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(CLIENT_TIMEOUT)
    # any client ip and port
    client_addr = ('', 0)
    # bind server address to port
    client_socket.bind(client_addr)
    # connect to server
    print("trying to connect to server: {}".format(server_addr))
    try:
        client_socket.connect(server_addr)
        newest_datetime = get_newest_datetime()
        if not newest_datetime:
            client_socket.send("None".encode())
        else:
            client_socket.send(get_newest_datetime().isoformat().encode())
        try:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                print("User does not have new articles.")
                client_socket.close()
                return
            make_dirs()
            file = open(DIR_TRANSFER + "/received_articles.zip", 'wb')
            file.write(data)
        except Exception:
            print("Failed to create zip file for received data.")
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            print(data)
            if not data:
                break
            file.write(data)
        file.close()
        print("Articles successfully received.")
        unzip_articles(DIR_TRANSFER + "/received_articles.zip")
        client_socket.close()
    except socket.error as exc:
        print("Socket exception: %s" % exc)
        client_socket.close()
    except Exception:
        print("Something went wrong sending newest date_time")

def start_client_threaded(ip):
    thread = threading.Thread(target=start_client(ip))
    thread.start()

def start_server():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # closes server after timeout if no client connected
    server_socket.settimeout(SERVER_TIMEOUT)
    # get default address and bind
    server_addr = (socket.gethostbyname(socket.gethostname()), DEFAULT_PORT)
    server_socket.bind(server_addr)

    # makes socket ready for accepting connections (max 1)
    server_socket.listen(1)
    print("server waiting on socket: {}".format(server_socket.getsockname()))

    try:
        (client_socket, client_addr) = server_socket.accept()
        print("client {} connected".format(client_addr))
        msg = client_socket.recv(4096)
        print("Received time " + msg.decode())
        if msg.decode() == "None":
            date_time = None
        else:
            try:
                date_time = datetime.fromisoformat(msg.decode())
            except Exception:
                print("Received time is not in iso format.")
                server_socket.close()
                return
        #msg.decode() == "0": ### change this to check if it is an actual time
            ### compress correct files to zip and send
        try:
            path = zip_articles(date_time)
            if path == None:
                server_socket.close()
                return
            else:
                file = open(path, 'rb')
        except Exception:
            print("Failed to open or compress files for sending to client.")
            return
        while True:
            data = file.read(BUFFER_SIZE)
            if not data:
                break
            client_socket.send(data)
        file.close()
        print("File sent succesfully: closing server")
        server_socket.close()
            
    except socket.timeout:
        print("No connection to server: closing server.")
        server_socket.close()
    except socket.error as exc:
        print("Socket exception: %s" % exc)
        server_socket.close()
    except Exception:
        print("An error occurred while listening to client.")
        server_socket.close()

def start_server_threaded():
    thread = threading.Thread(target=start_server)
    thread.start()

# test ----------------------------------------------

#if sys.argv[1] == "server":
#    start_server_threaded()
#else:
#    devices = get_devices()
#    print_devices(devices)
#    start_client_threaded('127.0.0.1')

#get_files_from_server(devices[0]["ip"])