"""Main Program Loop

This module contains the program logic for FreedomDrop
"""

import connection
import impexp
import subprocess
from bluetooth import *


#This is the actual starting point for the flow
connectionEstablished = False
dataReceived = False
okReceived = False
log = "test.pcap"
inventory = "logtextfile.txt"
payload = list()
peerPayload = list()
peerInventory = ""
peerInventoryList = "inventoryPeer.txt"
peerPayload = "peerPayload.pcap"


#BEFORE we are connected
localBTAddress = read_local_bdaddr()
print(f"Our local Bluetooth address is {localBTAddress}")

masterSocket = None
slaveSocket = None

if len(sys.argv) < 2:
  print("Usage: {sys.argv[0]} <isMaster> isMaster sets us as the active peer/ master and can be 0 or 1")
  exit()
else:
  isMaster = int(sys.argv[1])
  print("<You are now {title}>".format(title = "initiating the transfer" if isMaster == 1 else "waiting for an initiation"))

while not connectionEstablished:
    """
    The way we use sockets is a bit convoluted. If we were to advertise a serve using SDP,
    we'd have to use two sockets. However otherwise, we can send and receive through the same socket.
    This needs rewriting, should we decide to advertise a service. This would also change our
    execution flow significantly.
    """
    if isMaster == 1:
        #throwawayVar = ""
        connectionEstablished, slaveSocket = connection.establishConnection(isMaster)
        if connectionEstablished is True:
            print("<Connection has been established, master>")
            #connection.createAdHoc()
            #print("<Created Ad Hoc network>")
        else:
            print("<Connection could not be hosted. Trying again now...>")

    else:
        connectionEstablished, slaveSocket, masterSocket = connection.establishConnection(isMaster)
        if connectionEstablished is True:
            print("<Connection has been established, slave>")
            #print("<Ad Hoc network will be created by peer>")
        else:
            print("<Connection could not be established. Trying again now...>")
    #except Exception as exception:
    #print(exception)
    #exit()


#WHILE we are connected
#Here used to be 'Depracted Code Snippet #1'
if isMaster == 1:
    print("<creating local Inventory>")
    impexp.createInventory(log, inventory)
    print("<sending Inventory to Peer>")
    impexp.sendInventory(inventory,slaveSocket)
    print("<waiting to receive Inventory from Peer...>")
    impexp.receivePeerInventory(slaveSocket)
    print("<creating Payload for Peer>")
    impexp.createPayload(log, inventory, peerInventoryList)
    print("<sending Payload to Peer")         
    impexp.sendPayload(slaveSocket)
    print("<waiting to receive Payload form Peer...>")
    impexp.receivePeerPayload(slaveSocket)
    print("<updating log and Inventory with received payload")
    impexp.handlePayload(log, peerPayload, inventory) 
    print("<Your log database has been updated>")

else:
    print("<waiting to receive Inventory from Peer...>")
    impexp.receivePeerInventory(masterSocket)
    print("<creating local Inventory>")
    impexp.createInventory(log, inventory)
    print("<sending Inventory to Peer>")
    impexp.sendInventory(inventory, masterSocket)
    print("<waiting to receive Payload form Peer...>")
    impexp.receivePeerPayload(masterSocket)
    print("<creating Payload for Peer>")
    impexp.createPayload(log, inventory, peerInventoryList)
    print("<sending Payload to Peer")
    impexp.sendPayload(masterSocket)
    print("<updating log and Inventory with received payload")
    impexp.handlePayload(log, peerPayload, inventory) 
    print("<Your log database has been updated>")

if isMaster is True:
    disconnect([masterSocket, slaveSocket])
else:
    disconnect(slaveSocket)
print("<Program terminated>")



"""Deprecated code snipped #1
entriesCount = impexp.file_len("logtextfile.txt") Deprecated
We open a line for reading+writing, pointer is at beginning of file
f = open("logtextfile.txt", "r+")  #Deprecated
for _ in range(1,entriesCount+1,1): #Deprecated
    #readline() reads the entire line and presumably doesn't reset the pointer
    rawEntry = f.readline() #Deprecated
    formattedEntry = impexp.createEntry(rawEntry)  #Deprecated
    try:
        impexp.processEntry(formattedEntry)    #Deprecated
    except ValueError:                         #Deprecated
        print(ValueError)                      #Deprecated
f.close()                                      #Deprecated"""
