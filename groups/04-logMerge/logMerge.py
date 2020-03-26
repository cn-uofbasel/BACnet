import socket
import string
import threading

partnerID = []
dataSource = []
dataToSend = threading.Thread(target=sendData)
dataToReceive = threading.Thread(target=receiveData)


def sendData(data: bytes):
    pass

def receiveData(dataToSend: bytes):
    pass

def knownPeer(peerID: str):
    pass

def compareData(srcData: bytes, tarData: bytes):
    pass

