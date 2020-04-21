# Pseudocode for FreedomDrop

## There are two parts:
### 1. Converting the logs to be sent into packets to be sent and
### 2. receiving the packets
! As of now all descriptions of the processes are very vague and generic. That's because the conditions,
the environment as well as the exact way all FreedomDrop is going to run is not known yet!
The points that are still unknown are:
1. How will the logs be stored on the computer? As a text file or a specific file type in a directory? Or within a database that can only be read/write using special software
2. How exactly will the logs/event be stored and arranged in that software? (if at all)
3. How, if at all, will the two peers communicate about what logs are stored? Will we automatically only send the logs of events that the peer doesn't have or whose logs are not up to date? Or can the sender and the receiver manually choose which logs to send and to receive?
4. Do we only send events from feeds that the peer subscribed to/has or do we send events for feeds the user does not yet have?

## The general steps:
1. Peer1 and Peer2 are going through their logs and send information about what they have to the other side
2. Peer1 and Peer2 see if they have never logs for events or events that the other side doesn't own yet
3. Both Peers encode/pack the the logs to be sent somehow (this is not known/clear yet how)
4. Both Peers send the information over Bluetooth/IP
5. Both Peers decode/unpack the information and process it by adding it to their local database
6. Both Peers send an OK sign signifying that they received the payload (any data at all, really)
7. Connection is automatically terminated?

# Pseudo-code
Assumptions:
  * The logs are stored in 'clear language' in a text file at specific location in the directory, the security part is already fulfilled through the Bluetooth connection and not by us
  * The event logs each take up a line in a clear text file
  * The two peers can communicate about what logs they have/ don't have
  * The peers send each other feeds that the other peer doesn't have yet.
  * The event logs are sent as lines of text which the receiver then writes in a textfile and/or immediately processes

Basic setup in pseudocode: (file_len(fname) from )
```python
import subprocess

bool connectionEstablished = False
bool dataReceived = False
bool okReceived = False
inventory = dict()
payload = list()
peerPayload = list()

def file_len(fname):
    p = subprocess.Popen(['wc', '-l', fname], stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    return int(result.strip().split()[0])

def createEntry(rawEntry):
    ...
    return(entryTuple)

def processEntry(formattedEntry):
    try
      if formattedEntry.seq_num == inventory[str(formattedEntry.feed_id)]
    except KeyError:
      inventory[str(formattedEntry.feed_id)].append(formattedEntry)

def createInventory(inventoryDict): ...
    return inventory

def sendInventory(inventoryDict): ...

def receivePeerInventory() ...

def createPayload(inventoryDict, peerInventory): ...
  #how do we create the payload? As a clear text file just like we assume to store them locally?

def sendPayload(): ...

def receivePeerPayload(peerPayload): ...
  dataReceivedFromPeer = ...
  if dataReceivedFromPeer:
    for entry in dataReceivedFromPeer:
      formattedEntry = createEntry(entry)
      processEntry(formattedEntry)
      return True
  else:
    return False

def sendOk(): ...

def terminate(): ...

```

## Part 1: Converting and sending the logs
These are the general steps in natural language:  
---Connection established. Pre-transfer-----  
1. Go to the file location and open the file  
2. Identify all the logs/events there are locally  
    1. for every feed, record the feed_id and the newest seq_no (as a tuple?). The peer will simultaneously do the same.    

---Connection transfered. Transfer----  

3. Send this information to the peer. The peer will simultaneously do the same

In pseudocode:

```python

while not connectionEstablished:
  try:
    connectionEstablished = establishConnection()
  except Exception as exception:
    print(exception)
    end()

entriesCount = file_len("logtextfile")

f = open("logtextfile", r+)   #We open a line for reading+writing, pointer is at beginning of file
for _ in range(1,entriesCount+1,1):
  rawEntry = f.readline()    #readline() reads the entire line and presumably doesn't reset the pointer
  formattedEntry = createEntry(rawEntry)
  try:
    processEntry(formattedEntry)
  except ValueError:
    print(ValueError)
f.close()

peerInventoryList = receivePeerInventory()
payload = createPayload(peerInventory, peerInventoryList);
dataReceived = receivePeerPayload(peerPayload)

```

## Part 2: Receiving and processing the logs
---Connection established.
4. Based on the information from the peer, we send the events the peer does not have yet
5. We listen for data from the peer
6. If we received data from the peer we process the data and add it to our feeds. We then send an ok
7. If we sent an OK AND received an OK from the peer, we terminate the connection(?)
---Connection terminated. Post-tranfer----

In pseudocode:
```python
while not okReceived and not dataReceived:
  if not okReceived and notDataReceived:
    sendPayload()
  elif not okReceived:
    sendPayload()
    sendOk()
  elif not dataReceived:
    sendInventory(inventoryDict)
    dataReceived = receivePeerPayload(peerPayload)

sendOk()

terminate()
```
