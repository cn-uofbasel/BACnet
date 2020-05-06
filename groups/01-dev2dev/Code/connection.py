"""Connection Module

This module contains the function definitions used for
    - the device discovery process
    - establishing a connection
###NOTICE: Bluetooth Discovery can take quite a long time (up to 15 seconds)
           It is important to check if the nearby devices are actually discoverable
           (they are not by default, only during the pairing process and the like)
### NOTICE: Everything is still a work-in-progress functions in this module might later be
            moved to a more appropriate module
### TODO: Add SDP(Service Discovery Protocol) functionality
"""

from bluetooth import *
from impexp import *
import struct
import os
import sys

nearbyDevices = ""
socket = ""
serverSocket = ""
clientSocket = ""

def establishConnection(isMaster):
    """This function initiates a connection if called by masteror  powers up a server otherwise"""

    print("<Scanning...Please hold...>")
    if isMaster:
        nearbyDevices = discover_devices(lookup_names=True,flush_cache=True)
        print(f"<The scan has discovered {len(nearbyDevices)} (discoverable) devices nearby>")
        #for addr, name in nearbyDevices:
        #    print(f"{addr}:{name}")
        serverAddress = chooseSlave(nearbyDevices)
        serverName = lookup_name(serverAddress)
        try:
            socket = BluetoothSocket(RFCOMM)
            #print(f"<Now connecting to {serverName}:{serverAddress}>")
            #socket.connect( (serverAddress,port) )
        except Exception:
            print(Exception)
            return(False)
        #socket.send(...)
        #disconnect(socket) This should be in another function
        return(True)
    else:
        backlog = 1
        serverSocket = BluetoothSocket(RFCOMM)
        serverSocket.bind( ("", port) )
        serverSocket.listen(backlog)
        clientSocket, clientInfo = serverSocket.accept()
        print(f"Accepted connection from {clientInfo}")
        #data = clientSocket.recv(...)
        #print(f"received: {data}")
        #disconnect(clientSocket,serverSocket)  This shoudl be in another function
        return(True)


def chooseSlave(devicesList):
    """This function is called by a master after device discovery to choose whom to connect to"""

    counter = 1
    nameList = list()
    for addr, name in devicesList:
        print(f"[{counter}] {addr}:{name}")
        nameList.append(name)
        counter += 1
    slaveNum = int(input("Choose the slave by typing their number [x] >>"))
    counter = 1
    slaveAddress = ""
    for addr, name in nearbyDevices:
        if counter == slaveNum:
            slaveAddress = addr
            break
    #print(slaveAddress)
    return(slaveAddress)

def createAdHoc():
    cmd = "swift adhoc.swift"
    SSID = "kool"
    password = "cool" #Password is a WEP password
    os.system("swift adhoc.swift" + " " + SSID + " " + password)

def disconnect(*sockets):
    """This function is called by both master and server to close the sockets and thus disconnect"""

    for socket in sockets:
        socket.close()
