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

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip = str(s.getsockname()[0])
s.close()
print("Your IP is " + ip)
sock.bind((ip, 0))
port = int(sock.getsockname()[1])
print("Your port is " + str(port))

print('waiting for a connection..\n')
(data, address) = sock.recvfrom(1024) #we receive first contact from the client, giving us the ip/port as well.
print('connection from ', address)
print("Data: " + data.decode("utf-8"))
sock.sendto(bytes("Connected!".encode("utf-8")), address)

thread_receive = Thread(target = receive, args = ())
thread_send = Thread(target = send, args = ())

thread_receive.start()
thread_send.start()

# To start this correctly with the LopyClient on the Lopy4 you need following instructions:
# Deactivate your firewall, otherwise packets will not be able to be sent from the Lopy to the host machine.
# Start this Server first. Then you still need to go into the program LopyClient.py and change IP/Port.
# Also look that WLAN instructions match your home WLAN.
# If you have changed these specifications load the program to your Lopy and let it run. It should be able to connect to your computer.
# Now you can send messages from the PC to the Lopy.
# TODO: Make port static, so only the IP needs to be changed by hand for every use.
# TODO: Implement the  Lopy sending Data to the PC.