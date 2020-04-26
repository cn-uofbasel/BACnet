from network import LoRa
import socket
import time


lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868)
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setblocking(False)
events = lora.events()

i = 0
while True:
    time.sleep(3)
    #print(str(lora.ischannel_free(-100,1000)))
    msg = "gossip:hallo" + str(i)
    s.send(msg.encode('utf-8'))
    i = i + 1
    print(str(i))
    #print(s.recv(64).decode('utf-8'))
    msg_recv = s.recv(64)
    msg_recv = msg_recv.decode("utf-8")
    print(msg_recv)

    if (msg_recv and msg_recv.startswith("rts")):
        msg = "cts"
        s.send(msg.encode('utf-8'))
        print("sending cts")
