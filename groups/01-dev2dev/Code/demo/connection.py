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
import subprocess

nearbyDevices = ""
socket = ""
masterSocket = ""
slaveSocket = ""
clientSocket = ""


def establishConnection(isMaster):
    """This function initiates a connection if called by masteror  powers up a server otherwise"""

    global masterSocket
    global slaveSocket
    uuid = "741f2065-c26a-45fc-b944-6b2bc018a6e8"
    #port = 0


    if isMaster == 1:
        print("<Scanning...Please hold...>")
        nearbyDevices = discover_devices(lookup_names=True, flush_cache=True)
        while len(nearbyDevices) == 0:
            print("<Scanning...Please hold...>")
            nearbyDevices = discover_devices(lookup_names=True, flush_cache=True)
        print(f"<The scan has discovered {len(nearbyDevices)} (discoverable) devices nearby>")
        for addr, name in nearbyDevices:
            print(f"{addr}:{name}")
        addr = chooseSlave(nearbyDevices)
        #        serverName = lookup_name(serverAddress)

        # addr = '28:F0:76:68:C5:21'
        service_matches = find_service(uuid=uuid, address=addr)

        if len(service_matches) == 0:
            print("Couldn't find the SampleServer service.")
            sys.exit(0)

        first_match = service_matches[0]
        port = first_match["port"]
        name = first_match["name"]
        host = first_match["host"].decode("utf-8")
        try:
            masterSocket = BluetoothSocket(RFCOMM)
            # print(f"<Now connecting to {serverName}:{serverAddress}>")
        except Exception:
            print("<Error creating a master socket>")
            print(Exception)
            return (False, masterSocket)
        try:
            masterSocket.connect((host, port))
        except Exception as e:
            print("<Error connecting master socket>")
            print(e)
            return (False, masterSocket)
        # socket.send(...)
        # disconnect(socket) This should be in another function
        #       print(f"{serverName} accepted our connection")
        return (True, masterSocket)
    else:
        # SLAVE
        backlog = 3
        try:
            slaveSocket = BluetoothSocket(RFCOMM)
        except Exception as e:
            print("<Failed creating a Bluetooth socket>")
            print(e)
            return (False, slaveSocket, masterSocket)
        print("<Succesfully created a socket>")
        try:
            slaveSocket.bind(("", PORT_ANY))
        except Exception as e:
            print(f"<Failed binding the socket to port {port}>")
            print(e)
            return (False, slaveSocket, masterSocket)
        try:
            slaveSocket.listen(backlog)
        except Exception as e:
            print("<Failed listening on the slave socket>")
            print(e)
            return (False, slaveSocket, masterSocket)
    port = slaveSocket.getsockname()[1]

    advertise_service(slaveSocket, "FreedomDrop", service_id=uuid,
                      service_classes=[uuid, SERIAL_PORT_CLASS],
                      profiles=[SERIAL_PORT_PROFILE],
                      # protocols=[bluetooth.OBEX_UUID]
                      )
    print("Waiting for connection on RFCOMM channel", port)
    print("<Scanning...Please hold...>")
    try:
        masterSocket, masterInfo = slaveSocket.accept()
    except Exception as e:
        print("<Error accepting a slave socket>")
        print(e)
        return (False, slaveSocket, masterSocket)

    print(f"Accepted connection from {masterInfo}")
    # data = clientSocket.recv(...)
    # print(f"received: {data}")
    # disconnect(clientSocket,serverSocket)  This shoudl be in another function
    return (True, slaveSocket, masterSocket)


def chooseSlave(devicesList):
    """This function is called by a master after device discovery to choose whom to connect to"""

    counter = 1
    nameList = list()
    for addr, name in devicesList:
        print(f"[{counter}] {addr}:{name}")
        nameList.append(name)
        counter += 1
    slaveNum = int(input("Choose the slave by typing their number [x] >>"))
    while slaveNum == 0:
        nearbyDevices = discover_devices(lookup_names=True, flush_cache=True)
        devicesList = nearbyDevices
    counter = 1
    slaveAddress = ""
    for addr, name in devicesList:
        if counter == slaveNum:
            slaveAddress = addr.decode("utf-8")
            break
    # print(slaveAddress)
    return (slaveAddress)


def disconnect(*sockets):
    """This function is called by both master and server to close the sockets and thus disconnect"""

    for socket in sockets:
        socket.close()
