"""Main Program Loop

This module contains the program logic for FreedomDrop
"""

import connection
import impexp
import subprocess
from bluetooth import *


#This is the actual starting point for the flow
port = 1
connectionEstablished = False
dataReceived = False
okReceived = False
inventory = dict()
payload = list()
peerPayload = list()
peerInventory = ""
peerInventoryList = ""

#BEFORE we are connected
localBTAddress = read_local_bdaddr()
print(f"Our local Bluetooth address is {localBTAddress}")


if len(sys.argv) < 2:
  print("Usage: {sys.argv[0]} <isMaster> isMaster sets us as the active peer/ master and can be 0 or 1")
  exit()
else:
  isMaster = int(sys.argv[1])
  print("<You are now {title}>".format(title = "initiating the transfer" if isMaster == 1 else "waiting for an initiation"))

while not connectionEstablished:
  try:
    connectionEstablished = connection.establishConnection(isMaster)
    print("<Connection has been established>")
    if isMaster:
        connection.createAdHoc()
        print("<Created Ad Hoc network>")
    else:
        print("<Ad Hoc network will be created by peer>")
  except Exception as exception:
    print(exception)
    exit()

#WHILE we are connected
entriesCount = impexp.file_len("logtextfile.txt") #Deprecated

#We open a line for reading+writing, pointer is at beginning of file
f = open("logtextfile.txt", "r+")  #Deprecated
for _ in range(1,entriesCount+1,1): #Deprecated
    #readline() reads the entire line and presumably doesn't reset the pointer
    rawEntry = f.readline() #Deprecated
    formattedEntry = impexp.createEntry(rawEntry)  #Deprecated
    try:
        impexp.processEntry(formattedEntry)    #Deprecated
    except ValueError:                         #Deprecated
        print(ValueError)                      #Deprecated
f.close()                                      #Deprecated

if isMaster is True:
    #Master creates inventory and sends it
    #Master then waits for the slave's inventory
    #Master compiles and sends payload
    #Master then waits for slave's payload
    toPeerInventroyList = impexp.createInventory(inventory)
    impexp.sendInventory(toPeerInventoryList)
    fromPeerInventoryList = impexp.receivePeerInventory()
    toPeerPayload = impexp.createPayload(fromPeerInventoryList, inventory);
    impexp.sendPayload(toPeerPayload)
    dataReceived = impexp.receivePeerPayload()
else:
    #Slave receives master inventory and then builds its own
    #Slave then sends its own inventory
    #Slave then waits for Master's payload
    #Slave then sends Master their payload
    fromPeerInventoryList = impexp.receivePeerInventory()
    toPeerInventoryList = impexp.createInventory(inventory)
    impexp.sendInventory(toPeerInventoryList)
    dataReceived = impexp.receivePeerPayload()
    toPeerPayload = impexp.createPayload(fromPeerInventoryList, inventory);
    impexp.sendPayload(toPeerPayload)

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
