# Introduction to Internet and Security Gruppe 06 - longFi

## Content

* [Protocols](#protocols)
* [Code](#code)
* [Members](#members)

## Protocols

For every meeting there will be a protocol, which can be found [here](https://github.com/cn-uofbasel/BACnet/tree/master/groups/06-longFi/Protocols).

## Code

The code to send and receive ethernet packets can be found in this folder: [src](https://github.com/cn-uofbasel/BACnet/tree/master/groups/06-longFi/src)

---

#### Requirements

To run the code there are a few requirements. First of all, our code is based on the "scapy" libraries. 
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

To run the packet sender as well as the receiver, simply use the following command:

```
sudo python3 <script name> <interface name>
```

Script names:

* sendEther.py
* receiveEther.py

## Members

* **Faris Ahmetasevic** - Email: *faris.ahmetasevic@stud.unibas.ch*
* **Marco Banholzer** - Email: *marco.banholzer@stud.unibas.ch*
* **Nderim Shatri** - Email: *nderim.shatri@stud.unibas.ch*
