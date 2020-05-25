# Introduction to Internet and Security Gruppe 06 - longFi

## Content

* [Introduction](#introduction)
* [Code](#code)
* [Members](#members)

## Introduction

With this new created files the goal is to send missing packets from one user to another by using the code of the group 12 - logSync.
To use this code, it has to be inside the src folder of the logSync group.



## Code

The code to send and receive ethernet packets can be found in this folder: [src](https://github.com/cn-uofbasel/BACnet/tree/master/groups/Demo%20B/src/longFi/src)

---

#### Requirements

To run the code there are a few requirements. First of all, like mentioned in the introduction, the files have to be combined with the files of the logSync group.
Our code is based on the "scapy" libraries. 
To install the libraries on Python3 run this command:

```
sudo pip3 install scapy
```

Also the user has to know on which interface the network is. To check all the interfaces you can write differnet commands depending on the operating system:

##### Mac

```
networksetup -listallhardwareports
```

##### Linux 

```
nmcli device status
```

##### Windows

```
netsh interface ipv4 show interfaces
```

Another way is to check the interfaces on the start screen of Wireshark.

---

#### Run the code

Main.py uses the etherConnection.py code to send and receive the packets. Inside etherConnect.py there are two classes. 

* HasPackets(): This class has all the packets and sends the missing packets to the NeedsPackets() class.
* NeedsPackets(): Receives all of the missing packets, which were sent by the HasPackets() class.


Both classes use sendEther.py and receiveEther.py to send or receive raw ethernet packets.


To run the code one user has to have all packets and the other user is missing packets.

Simply use the following command for the user who has all packets:

```
sudo python3 main.py --hasPackets <interface name>
```

For the user who needs the packets, run:

```
sudo python3 main.py --needsPackets <interface name>
```

## Members

* **Faris Ahmetasevic** - Email: *faris.ahmetasevic@stud.unibas.ch*
* **Marco Banholzer** - Email: *marco.banholzer@stud.unibas.ch*
* **Nderim Shatri** - Email: *nderim.shatri@stud.unibas.ch*
