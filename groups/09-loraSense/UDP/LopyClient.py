import lib.lorasense as lorasense
import socket
import sys
import _thread


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


lorasense = lorasense.LoraSense(mode=1, debug=1)
lorasense.setupLoRa()
lorasense.setupWLAN("AnnaPihl1", "CousCous")
#lorasense.startLoRaComm()


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ip = "192.168.1.123"
port = 52703

print("Connecting to a Server")

address = (ip, port)

sock.connect(address)
sock.sendto("Connected?".encode("utf-8"), address)

data, ip = sock.recvfrom(1024)
print(data.decode())

_thread.start_new_thread(receive, ())
_thread.start_new_thread(send, ())
