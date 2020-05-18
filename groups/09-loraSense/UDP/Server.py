import socket
import sys
from threading import Thread
from time import sleep
import select

def send():
    while True:
        msg = sys.stdin.readline().rstrip('\n')
        if not msg.isspace():
            sock.sendto(bytes(msg.encode("utf-8")), address)


def receive():
    while True:
        data, ip = sock.recvfrom(1024)
        if data:
            print("Data: " + data.decode())


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ip = input("Please enter the IP address: ") 
port = int(input("Please enter the port: "))

address = (ip, port)

sock.connect(address)
sock.sendto("Connected?".encode("utf-8"), address)

data, ip = sock.recvfrom(1024)
print(data.decode())

thread_receive = Thread(target = receive, args = ())
thread_send = Thread(target = send, args = ())

thread_receive.start()
thread_send.start()
