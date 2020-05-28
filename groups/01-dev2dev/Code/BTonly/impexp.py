#!/usr/bin/env python3
"""Import/Export module

This module contains the function definitions use for:
    - importing the peers Inventory (list of all the logs the peer has) and their
      Payload(all the peers logs relevant for us) as well as
    - exporting our own Inventory and Payload information during the exchange.
Functions contained in this module are:
    - file_len(fname)
    - createEntry()
    - processEntry()
    - createInventory()
    - sendInventory()
    - receivePeerInventory()
    - createPayload()
    - sendPayload()             TODO
    - receivePeerPayload()      TODO, Current implementation depracated
    - sendOk()                  TODO
    - terminate()               TODO
### NOTICE: Everything is still a work-in-progress functions in this module might later be
moved to a more appropriate module
### TODO: It would probably be good to create a Python method which turns .pcap files
into Python objects which can then be parsed and handled easier (i.e. JSON objects)
"""
from bluetooth import *
import lib.pcap as pcap
import cbor2
import hashlib
import subprocess
import difflib
from pathlib import Path
import os
from lib import event

payloadDir = "payload"
peerPayloadDir = "peerPayload"

def file_len(fname):
    """
    Function from Stack Overflow
    Simply returns the amount of lines in the given file fname
    It is possible that the file has to be a .txt
    """
    p = subprocess.Popen(['wc', '-l', fname], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    return int(result.strip().split()[0])


def filesize(fname):
    """
    Simply returns the size of the file fname in bytes
    """
    return (Path(fname).stat().st_size)


def importPCAP(fname):
    """
    Imports the pcap file in the specific format specified int the pcap.PCAP function from the demo files of Professor Tschudin.
    """
    log = pcap.PCAP(fname)
    return log


def importInventory(fname):
    """
    Imports a specifed txt-file.
    """
    inventory = open(fname)
    return inventory


'''
def createEntry(rawEntry):
    #return(entryTuple)
    pass

def processEntry(formattedEntry):
    """
    Please comment
    """
    try:
      if formattedEntry.seq_num == inventory[str(formattedEntry.feed_id)]:
          pass
    except KeyError:
      inventory[str(formattedEntry.feed_id)].append(formattedEntry)
'''


def createInventory(fname, inventoryDict):
    """
    writes the Inventory of all logs that are stored in a pcap file (fname) to the givent inventory file as txt.
    fname - pcap file
    inventroryDict - txt where the inventory should be stored in
    TODO: work with hashes of log.
    """
    log = importPCAP(fname)
    log.open('r')
    inventory = open(inventoryDict, 'w+')
    inventory.write('inventory\n')
    for w in log:
        e = event.EVENT()
        e.from_wire(w)
        seq = e.seq
        inventory.write("%d \n" % seq)
    log.close()
    inventory.close()


def compareInventory(inventoryint, inventoryext):
    """
    Compares two txt-files who are intended as inventories of pcap files that log the different messages.
    At the moment it only compares the indexes
    TODO: work with hashes of log.
    """
    seq_external = set()
    seq_internal = set()
    with open(inventoryint) as internal:
        for line in internal:
            seq = line.rstrip('\n')
            if seq == "inventory":
                continue
            seq_internal.add(int(seq))

    with open(inventoryext) as external:
        for line in external:
            seq = line.rstrip('\n')
            if seq == "inventory":
                continue
            seq_external.add(int(seq))
    print(seq_external)
    print(seq_internal)
    if seq_internal != seq_external:
        seq_diff = seq_internal - seq_external
        return seq_diff
    else:
        print("both logs are up to date!")
        return set()


def sendInventory(inventory, socket):
    """

    """
    # TODO: This code has not yet been tested
    try:
        file = open(inventory)
        SendData = file.read(512)
        while SendData:
            socket.send(SendData.encode('utf-8'))
            SendData = file.read(512)
        file.close()
    except Exception as e:
        print("Error: %s" % e)


def receivePeerInventory(socket):
    # socket is a BluetoothSocket, not an IP socket!!!
    # peerInventoryByteSize =
    # if peerInventoryByteSize != None:
    """
    Please comment
    """
    try:
        while 1:
            receivedInventory = socket.recv(2048)
            peerInventory = receivedInventory.decode('utf-8')
            if peerInventory:
                with open("inventoryPeer.txt", "w") as external:
                    external.write(peerInventory)
                    print("<received Inventory from Peer>")
                return
    except BluetoothError:
        print(f"<Bluetooth error: {BluetoothError}>")
    except Exception as e:
        print("Error: %s" % e)
    return


def createPayload(fname, inventoryint, inventoryext):
    """
    creates payload pcap file with the missing pcap files for the peer.
    """
    # how do we create the payload? As a clear text file just like we assume to store them locally?
    seq_payload = compareInventory(inventoryint, inventoryext)
    if seq_payload == set():
        print('the payload is empty')
        return
    
    log = importPCAP(fname)
    print('created payload file')
    log.open('r')
    for w in log:
        e = event.EVENT()
        e.from_wire(w)
        seq = e.seq
        print(seq)
        if seq in seq_payload:
            payload = importPCAP('payload/'+ str(seq) +'.pcap')
            payload.open('w')
            payload.write(w)
            payload.close()
    log.close()


def handlePayload(fname, inventoryDict):
    """
    takes the Payload of the peer specified for the local log and writes
    """
    log = importPCAP(fname)
    log.open('a')
    for file in os.listdir("peerPayload"):
        payload = importPCAP("peerPayload/" + file)
        payload.open('r')
        for w in payload:
            log.write(w)
        payload.close()
    log.close()
    print("<wrote peerPayload to log>")


def sendPayload(socket):
    """
    Please comment
    """
    # TODO: Implement and test
    try:
        if not os.listdir("payload"):
            socket.send(b"False")
            print("<no payload to sent>")
            return

        # payload exists
        socket.send(b"True")
        for file in os.listdir("payload"):
            payload = importPCAP("payload/" + file)
            payload.open('r')
            i = 0
            for w in payload:
                socket.send(w)
                print("%d" % i)
                i += 1
            payload.close()
        socket.send(b"fin")
    except Exception as e:
        print("Error: %s" % e)


def receivePeerPayload(socket):
    """
    Please comment
    """
    # Current code already deprecated
    # TODO: Implement and test
    payloadInfo = socket.recv(4096)

    if payloadInfo == b"False": 
        print("<no payload expected. logs are up to date.>")
        return 0

    try:
        while 1:
            peerPayloadLines= socket.recv(4096)  # receive using socket
            if peerPayloadLines:
                if peerPayloadLines == b"fin":
                    return 1
                e = event.EVENT()
                e.from_wire(peerPayloadLines)
                seq = e.seq
                peerpayload = importPCAP('peerPayload/'+ str(seq) +'.pcap')
                peerpayload.open('a')
                peerpayload.write(peerPayloadLines)
                peerpayload.close()
                print("<received payload from peer>")

        
    except BluetoothError:
        print(f"<Bluetooth error: {BluetoothError}>")
    except Exception as e:
        print("Error #1: %s" % e)

"""
    if dataReceivedFromPeer:
        for entry in dataReceivedFromPeer:
            formattedEntry = createEntry(entry)
            processEntry(formattedEntry)
        peerPayload = "???"
        return(True,peerPayload)
    else:
        return(False,"")
"""

def cleanUpPayloads():
    for file in os.listdir("peerPayload"):
        os.remove("peerPayload/" + file)
    for file in os.listdir("payload"):
        os.remove("payload/" + file)
    

def sendOk():
    pass


def terminate():
    pass
