# Documentation of the BACNet-Core Library

The BACNet-Core is a Python Library/Software that includes all functionality to make use of the BACNet Network.
This library enables a developer to include BACNet functionality in their applications.

The main goal was to create an easy to use, modular and standartized codebase so that others can easily expand or change the library
as they need it to be.

## Structure Overview

We separated the BACNet Core into two submodules: Core and Replication

**Core:** holds all Parts of the Software regarding the whole logic of BACNet: The "Node" class is the main class and serves as a blackboard (Blackboard-Architecture) for all  the other parts of thge Core. Therefor it contains an eventbus, that every subcomponent subscribes to. There are further components such as:
    - A Feed abstraction for Masterfeeds and normal Feeds
    - A Storage Controller that holds most of the logic and has a Storage connector as subclass that enables access to a DB where the BACNet Data is managed
    - A COM-Link that is the mediator between the Replication Module and the Core. It manages the synchronisation of Databeses between Nodes.

**Replication**: Consists of a Channel class which is subclass of multiprocessing.Process it holds methods to receive and send data as well as controlmessages. (Details in the corresponding section).


## The Core

As in the previous Versions of BACNet, all the Data the BACNet uses and works on is stored in a Database, but this time the Database also holds the keys of the feeds as well as
a Table for policies for example if the COM-Link will serve as 

### Synchronization

For the BACNet to work, Nodes need to exchange Data and Information. Therefor the Databases needs to be synchronized according to the policies and rules each Node can apply individually. One can for example descide which Feeds you want to hold or if you want to serve as a distrubutor for others requests and Data.

**Separation of Complexity**

The Synchronization is handled by the "Com-Link" Instance in the Core. It holds all the communication logic and just uses the Channels to send and receive Metadata or Data. A Channel and a COM-Link share 2 Buffers to exchange Information.
Due to the fact, that there can exist different types of Networks we made the decision to have network specific logic inside tghe Channel-Implementation. The Com-Link and the Whole Core only have 4 basic Messagetypes to deal with:

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

**Channel-Behaviour**: Depends on the Network type, but basically messages from the outputbuffer are sent and received ones are written to into the Inputbuffer for the Com-Link.
**COM-Link-Behaviour**: It subscribes to the bus:.

MANUAL:     If you choose the Manual Mode, you need to use the Methods of the COM-Link directly to ask for data, send data and communicate with the peers
AUTOSYNC:   In a predefined timeinterval and when using send()/receive() in feeds, the COM-Link directly writes/reads data from/into the I/O Buffer it shares with its channels.

Independently from this there is the automatic process of incoming Control/Requestmessages, we intend to use a subprocess bound to the COM-Link to read the according Buffer out and acting on it.


### Data and Feeds

Everything is stored in the Database and every Data needs to be requested via the eventbus. As an effect Feed instances are just wrappers to send according requests and make them useravailable. This leads to easy usage of feeds, since you can pass references of them to different parts of your program. This alllows for easy separation of concern and flexibility.


## API

### For Applications

As shown in sampleusage.py

### For Replication Module Developers

You need to make sure that you create a Subclass of "Channel" and implement all methods of the abtract class. The Constructor should have the ability to take the
Threadsafe Buffers and the main method should read/write to/from the buffers