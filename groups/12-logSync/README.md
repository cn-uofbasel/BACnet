# Group 12 logSync

## Members
- Alexander Oxley
- Carlos Tejera

## Idea

Our task is to create an API in which it is possible to synchronize two databases. 
We create a UDP connection between two devices to compare database entries. 
Thereby it is detected if entries are missing and if the database needs to be updated. 
Furthermore we have to consider certain filters, as not every user needs the same logs. 
When the comparison is done, our interfaces provide the necessary information (log extensions) that the other transport layer groups need to send/transport. 
Our functions will also append the data entries to the database. 
In a nutshell, our API will make sure that the databases are correctly "updated" when they are synchronized with others.

## Requirements

To achieve our goal, we need the filter functions of group 14 (feedCtrl) and of course the data storage functions of group 7 (logStore).


## API

We offer our API to groups such as 2, 5, 6 and 8 as they will need the synchronization.

### Network protocol

Three connections have to be established between two devices.The protocol looks like shown below:


|   |Device A               |   |   |   |Device B   |
|---|-----------------------|---|---|---|-----------|
|1  |- Creates "I HAVE"-list|   |   |   |           |
|2  |- Sends "I HAVE"-list  | - |   |   |           |
|   |                       |   | - |   |
|3  |                       |   |   | - |- Receives "I HAVE"-list|
|4  |                       |   |   |   |- Compares list with own entries|
|5  |                       |   |   |   |- Creates "I WANT"-list|
|6  |                       |   |   | - |- Sends "I WANT"-list|
|   |                       |   | - |   |
|7 |- Receives "I WANT"-list| - |   |   |           |
|8  |- Filters events       |   |   |   |           |
|9  |- Creates EVENT-list   | - |   |   |           |
|   |                       |   | - |   |
|10 |                       |   |   | - |- Receives EVENT-list|
|11 |                       |   |   |   |- Synchronisation|

**Definitions:**

"I HAVE"-list: The list contains the information about all the feeds on Device A (database comparison purpose).

"I WANT"-list: A list, which indicates which extensions are required and from which sequence number (only information).

EVENT-list: List with the actual feed extensions

### Functions

The functions we will provide are:
```python
def get_i_have_list()
```

```python
def get_i_want_list(i_have_list)
```


```python
def get_event_list(i_want_list)
```

```python
def sync_extensions(list_of_extensions, event_list) # list_of_extensions: which feeds do need an extension
```

The last function needs the information of the feeds that do need an extension and the event list to append the extension to the corresponding feed.


## Use


### The database

The databases we synchronize consist of several PCAP files (for now!). These files contain all the important information we need to synchronize (respectively to update) the databases. 
The directory with the database is './udpDir' where all the PCAP files have to be for the synchronisation. 


### UDP Synchronisation

To request the synchronisation of your database with another one, you need to request it from another computer. Therefore, you need to enter the code below into Computer A. The communication bases on a UDP broadcast connection.

```python
python3 main.py --server <port>
```

The program waits for any other computer in the sub-network that needs a synchronisation, since the computer is in broadcasting state. In Computer B you enter:

```python
python3 main.py --client <port>
```

The computers begin to interchange the needed information to finish the synchronisation (P2P). Note that the files get extended and not overwritten to avoid too much data traffic.

### Arbitrary Synchronisation

For the other groups:

If you want to test the synchronisation with your transmission tool, you need to import `transport.py` and use the functions
as shown in the network protocol. Note that the databases are not connected yet and that means that we are still only
synchronising the PCAP files in the `./udpDir/` directory! 

To test, delete the PCAP files in Device B. After the synchronisation, the PCAP files should be back in the directory.

#### Dump:

To make the PCAP files human-readbable and to check if the databases got synchronised correctly, enter:

```python
python3 main.py --dump <directory>
```


## LOG
- Update 29.3.20: Pascal has left the group
- Update 15.4.20: half-way point presentation ready and Idea, Requirements and API set
