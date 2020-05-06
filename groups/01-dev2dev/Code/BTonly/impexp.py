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
    - receivePeerPayload()
    - sendOk()                  TODO
    - terminate()               TODO
### NOTICE: Everything is still a work-in-progress functions in this module might later be
moved to a more appropriate module
### TODO: It would probably be good to create a Python method which turns .pcap files
into Python objects which can then be parsed and handled easier (i.e. JSON objects)
"""

import subprocess


def file_len(fname):
    p = subprocess.Popen(['wc', '-l', fname], stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    return int(result.strip().split()[0])

def createEntry(rawEntry):
    #return(entryTuple)
    pass

def processEntry(formattedEntry):
    try:
      if formattedEntry.seq_num == inventory[str(formattedEntry.feed_id)]:
          pass
    except KeyError:
      inventory[str(formattedEntry.feed_id)].append(formattedEntry)

def createInventory(inventoryDict):
    #returns an inventory from the inventory dictionary
    pass

def sendInventory(inventoryDict, socket):
    socket.send(inventoryDict)

def receivePeerInventory(socket):
    #socket is a BluetoothSocket, not an IP socket!!!
    peerInventoryByteSize =
    if peerInventoryByteSize != None:
    peerInventory = socket.receive()
    return(peerInventory)

def createPayload(fromPeerInventoryDict, inventory):
    #how do we create the payload? As a clear text file just like we assume to store them locally?
    pass

def sendPayload(socket):
    pass

def receivePeerPayload(socket):
  dataReceivedFromPeer = "" # receive using socket
  if dataReceivedFromPeer:
    for entry in dataReceivedFromPeer:
      formattedEntry = createEntry(entry)
      processEntry(formattedEntry)
      return True
  else:
    return False

def sendOk():
    pass

def terminate():
    pass
