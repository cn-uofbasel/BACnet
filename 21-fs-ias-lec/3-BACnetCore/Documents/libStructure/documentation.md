# Technical Documentation of the BACNet-Core Library

The BACNet-Core is a Python Library/Software that includes all functionality to make use of the BACNet Network.
This library enables a developer to include BACNet functionality in their applications.

The main goal was to create an easy to use, modular and standardized codebase so that others can easily expand or change the library
as they need it to be.

## Structure Overview

We separated the BACNet Core into two submodules: Core and Replication

**Core:** Holds all parts of the software regarding the whole logic of BACNet: The "Node" class is the main class and serves as a blackboard (Blackboard-Architecture) for all  the other parts of the Core. There are further components such as:
    - A Feed abstraction for Masterfeeds and normal Feeds
    - A Storage Controller that holds most of the logic and a Database Handler that enables access to a DB where the BACNet Data is managed
    - A COM-Link that is the mediator between the Replication Module and the Core. It manages the synchronisation of Databases between Nodes.

**Replication**: Consists of a Channel class which is a subclass of multiprocessing. It holds methods to receive and send data as well as control messages. (Details in the corresponding section).


## The Core

As in the previous Versions of BACNet, all the Data the BACNet uses and works on is stored in a Database, but this time the Database also holds the keys of the feeds as well as
a table for policies.

### Synchronization

For the BACNet to work, Nodes need to exchange Data and Information. Therefore, the Databases need to be synchronized according to the policies and rules each Node can apply individually. One can for example decide which Feeds you want to hold or if you want to serve as a distributor for others requests and Data.

**Separation of Complexity**

The Synchronization is handled by the "Com-Link" Instance in the Core. It holds all the communication logic and just uses the Channels to send and receive Metadata or Data. A Channel and a COM-Link share 2 Buffers to exchange Information.
Due to the fact, that there can exist different types of Networks, we made the decision to have network specific logic inside the Channel-Implementation. The Com-Link and the whole Core only have 4 basic message types to deal with:

1. A
2. B
3. C
4. D

**External Communication Protocol**

The CommunicationProtocol for the channels among themselves looks like this:
1. A
2. B
3. C
4. D

**Channel-Behaviour**: Depends on the Network type, but basically messages from the output buffer are sent out and received ones are written into the input buffer for the Com-Link.
**COM-Link-Behaviour**: 

MANUAL:     If you choose the Manual Mode, you need to use the methods of the COM-Link directly to ask for data, send data and communicate with the peers
AUTOSYNC:   In a predefined time interval and when using send()/receive() in feeds, the COM-Link directly writes/reads data from/into the I/O Buffer it shares with its channels.

Independently of this, there is the automatic process of incoming Control/Request messages, we intend to use a subprocess bound to the COM-Link to read the according Buffer out and act on it.


### Data and Feeds

Everything is stored in the Database. As an effect, Feed instances are just wrappers to send according requests and make them available to users. This leads to easy usage of feeds, since you can pass references of them to different parts of your program. This allows for easy separation of concern and flexibility.


## API

### For Applications

As shown in sampleusage.py

### For Replication Module Developers

You need to make sure that you create a Subclass of "Channel" and implement all methods of the abtract class. The Constructor should have the ability to take the
thread safe buffers, and the main method should read/write to/from the buffers