# Group 12 logSync

## Members
- Alexander Oxley
- Carlos Tejera

## Idea

Our task is to create an API in which it is possible to synchronize two databases.
The entries/objects are compared to each other to add data that is missing in one of the databases. In addition we have to consider certain filters, because not every user needs the same logs (there is a kind of feed subscriptions). So our API will make sure that the databases are correctly "updated" when they are synchronized with others.

## Requirements

To achieve our goal, we need the filter functions of group 14 (feedCtrl) and of course the data storage functions of group 7 (logStore).


## API

We offer our API to groups such as 2, 5, 6 and 8 as they will need the synchronization.

The function we will provide will look similar to this:
```python
    def syncDB(db1, db2, filter1, filter):
        return db1, db2
```

The exchange of data will obviously run in the background.


## Use


### The database

The databases we synchronize consist of several PCAP files. These files contain all the important information we need to synchronize (respectively to update) the databases. 
The directory with the database is './udpDir' where all the PCAP files have to be for the synchronisation. 


### Synchronisation

To request the synchronisation of your database with another one, you need to request it from another computer. Therefore, you need to enter the code below into Computer A. The communication bases on a UDP connection at the moment.

```python
python3 main.py --server <host> <port>
```

The program waits for Computer B to connect to it. In Computer B you enter:

```python
python3 main.py --client <host> <port>
```

The computers begin to interchange the needed information to finish the synchronisation. Note that the files get extended and not overwritten to avoid too much data traffic.

### Dump:

To make the PCAP files human-readbable and to check if the databases got synchronised correctly, enter:

```python
python3 main.py --dump <directory>
```


## LOG
- Update 29.3.20: Pascal has left the group
- Update 15.4.20: half-way point presentation ready and Idea, Requirements and API set
