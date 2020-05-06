# Pseudocode for FreedomDrop - Connection Establishment w/ Bluetooth

## Discoverability and Connectability
For privacy and security concerns, all Bluetooth devices have two options that determine whether
or not the device responds to device inquiries and connection attempts
1. Inquiry Scan option controls the former,
2. Page Scan option controls the latter
The default setting is: Discoverability OFF - Connectability ON, meaning
a device scans for connection attempts, but not for discovery attempts.

## Bluetooth Transport Protocols
Bluetooth contains many transport protocols, most of them are special-purpose and can be categorized by 'guarantees' and 'semantics'
* Guarantees describe how hard a protocol tries to deliver a packet sent ()
* Semantics: either packet or stream-based

The 4 most important protocols are:
1. Radio Frequency Communications (RFCOMM)
  * "RFCOMM is a general-purpose transport protocol that happens to work well for emulating serial port"
  * Reliable, stream based protocol (i.e. TCP of Bluetooth)
  * Designed to emulate RS-232 serial ports
  * Allows only 30 Ports on a machine
  * In certain systems, it's the only supported protocol
2. Logical Link Control and Adaption Protocol (L2CAP)
  * Varying levels of reliability, packet based protocol (i.e. (possibly reliable) UDP of Bluetooth)
  * Technically allows up to 32,767 Protocol Service Multiplexers (PSM) a.k.a. ports
  * Enforces packet order
  * Can be set to be as reliable as UDP or TCP
3. Asynchronous Connection-oriented Logical protocol (ACL)
  * RFCOMM connections are transported within L2CAP connections
    * L2CAP connections are encapsulated within ACL connections
  * ACL is similar to IP, a fundamental protocol that is rarely used directly for transporting data
4. Synchronous Connection-Oriented protocol (SCO)
  * Best effort, package based, strange beast
  * Only used to transmit voice-quality audio (exactly 64kB/s)
  * SCO connection will always be given priority for the 64kB/s
  * No Bluetooth device is allowed to have more than 3 simultaneous SCO connection
  * SCL data packets aren't usually transported transparently

* We will use RFCOMM since we need the reliable, stream-based quality

## Ports
Just like in IP, some ports in Bluetooth are already reserved for standardized services
* L2CAP reserves port 1-1023
  1. 1 is reserved for the Service Discovery Protocol
  3. 3 is used to multiplex RFCOMM connections onto L2CAP
* RFCOMM does not have any reserved ports/channels

## Service Discovery Protocol (SDP)
To avoid the usual problem in Network Programming of figuring out on which port the server listens, Bluetooth introduces SDP
* Every Bluetooth device maintains an SDP Server listening on a well-known port number
* When a server application starts, it registers a description of itself with a port on the SDP server on the local device.
  * Instead of assigning a port number at design time, we assign a unique ID (Service ID)
  * This descriptions is called a Service Record or SDP Record and consists of a list of attribute/value pairs
  * Important attributes are port, Service ID and Service ID Class List
  * The Service ID is a 128-bit Universally Unique Identifiers (UUID)
* On startup, server applications get dynamically assigned port numbers
* When a remote client application tries to connect it provides a description of the service it is looking for and the SDP server responds with a listing of all the services that match
* Common SDP Attributes are:
  * Service Class ID List
  * Service ID
  * Service Name
  * Service Description
  * Protocol Descriptor List
  * Profile Descriptor List
  * Service Record Handle


## The general steps
The user who initiates the exchange from here on will be called 'master' and his peer will be referred to as 'slave'. This is not because of an SM-innuendo but to emulate Bluetooth-talk
1. We discover all devices in proximity of the master
2. We show them to the master and let him choose whom to establish a connection with

# Pseudocode
```python
import sys
import bluetooth

def chooseSlave(devicesList):
  counter = 1
  for addr, name in nearbyDevices:
    print(f"[counter] {addr}:{name}")
    counter += 1
  slaveNum = input("Choose the slave by typing their number [x] >>")
  slaveNum = devicesList[name]
  return(slaveNum)

def establishConnection(deviceNum):
  ...

def transferData():
  ...

ourBTAddress = ...

if len(sys.argv) < 2:
  print(f"Usage: {sys.argv[0]} <isMaster> isMaster sets us as the active peer/ master and can be 0 or 1")
else:
  isMaster = int(sys.argv[1])


#TODO: Print our own BT address

nearbyDevices = bluetooth.discover_devices(lookup_names=True)  #Assumption: disover_devices() returns a dict
print(f"The scan has discovered {len(nearbyDevices)} devices")


if isMaster:
  #TODO: Create Client/Active socket
  #Create socket
  slaveAddress = chooseSlave(nearbyDevices)
  print(f"Connecting to slave @{slaveAddress}")
  establishConnection(device num)
else:
  #TODO: Create Server/Passive socket
  #Create socket
  #Bind socket
  #Listen on socket


#At this point, we're either the client or server and thus either connected to the peer or listening on our port
#TODO: Continue
```
