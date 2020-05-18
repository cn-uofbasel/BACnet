# Group 12 logSync

## Members
- Alexander Oxley
- Carlos Tejera

## Idea

Our task is to create an API in which it is possible to synchronize two databases. We create a UDP connection between two devices to compare database entries. Thereby it is detected if entries are missing and if the database needs to be updated. Furthermore we have to consider certain filters, as not every user needs the same logs. When the comparison is done, our interfaces provide the necessary information (log extensions) that the other transport layer groups need to send/transport. Our functions will also append the data entries to the database. In a nutshell, our API will make sure that the databases are correctly "updated" when they are synchronized with others.

## Requirements

To achieve our goal, we need the filter functions of group 14 (feedCtrl) and of course the data storage functions of group 7 (logStore).


## API

We offer our API to groups such as 2, 5, 6 and 8 as they will need the synchronization.

The functions we will provide are:
```python
   get_packet_to_send_as_bytes()
```

and

```python
   sync_extensions(files_that_will_get_extended, received_packet_as_bytes)
```

The first function provides a list of log extensions for every file that must get extended. This list is converted to bytes (serialized by cbor2) and actually ready to be sent. The latter function needs the information of the files that get extended and the packet with the log extensions to append the entries.


## Use


### The database

The databases we synchronize consist of several PCAP files (for now!). These files contain all the important information we need to synchronize (respectively to update) the databases. 
The directory with the database is './udpDir' where all the PCAP files have to be for the synchronisation. 


### UDP Synchronisation

To request the synchronisation of your database with another one, you need to request it from another computer. Therefore, you need to enter the code below into Computer A. The communication bases on a UDP connection at the moment.

```python
python3 main.py --server <host> <port>
```

The program waits for Computer B to connect to it. In Computer B you enter:

```python
python3 main.py --client <host> <port>
```

The computers begin to interchange the needed information to finish the synchronisation. Note that the files get extended and not overwritten to avoid too much data traffic.

### Arbitrary Synchronisation (Prototyp)

For the other groups:

If you want to test the synchronisation with your transmission tool, you need to remove the udp synchronisation in `udp_conection.py`. There are two classes: `Client` and `Server`. In both, you have to remove the code part between the #-lines (otherwise it synchronises the directories via UDP). 

Now, do the same steps as above!

Computer A provides the bytes that have to be sent by your transmission tool with `server.get_packet_to_send_as_bytes()` and you can send the data to Computer B. To append the received data use on Computer B `sync.sync_extensions(client.get_compared_files, <the packet you sent in bytes format>)`. It is important to create instances of `Server` and `Client`, since you need the method `get_packet_to_send_as_bytes()` and `get_compared_files()`! Now, the database on Computer B should be synchronised.

### Dump:

To make the PCAP files human-readbable and to check if the databases got synchronised correctly, enter:

```python
python3 main.py --dump <directory>
```


## LOG
- Update 29.3.20: Pascal has left the group
- Update 15.4.20: half-way point presentation ready and Idea, Requirements and API set
