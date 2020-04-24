# Specification Book
* Project title: Sneakernet for the BACnet
* Developers: Leonhard Badenberg, Patrik Bütler, Luka Obser


## 1. Goal 
* Creation of software that allows the BACnet to become a sneakernet

## 2. Stakeholders
* Developers
* Professor and assistants
* BACnet users (and developers)

## 3. General Conditions and Context
* Our software is implemented in python
* Structure of BACnet and its event feed is described [here](https://github.com/cn-uofbasel/BACnet/tree/master/doc)
* Software must be functional even without a connection to the internet
* Software is primarily developed for USB drives and PCs
    * Other devices likely might work but there is no guarantee
    * There have been ideas about integrating our software in group 10s mobile application but this was put on hold for now
    
## 4. Functional Requirements
* Software must be convenient to execute
    * This means the user should be able to simply double click a file rather than being forced to use the console
* Software can be started from a USB drive
    * Ideally it would autorun when the USB drive is connected which is in accordance to the previous requirement
* Software is accompanied by a GUI
    * The GUI is simple and has no more than 5 different windows
    * The GUI offers feedback and support to the user by stating what is happening at any given moment
    * The user has complete control over the action they want to perform (at any stage they can cancel the process)
* Software allows the user to possess multiple representations of the BACnet
    * Operations are only to be made on the one log the user specifies (see use cases)
* If the software encounters problems the error messages are to be constructive and clear
* In addition to the ability to examine the events more thoroughly as described in use case 4, the GUI displays information such as the USB drives ability to create a new BACnet representation in its initial window

## Attachment A: Use cases

### Use Case 1:
* Name: Export
* Agents: Member of BACnet 
* Preconditions: 
    * Agents PC contains a local representation of the BACNet
    * Agent possesses a USB drive with our software
* Common process:
    * Connect USB drive to PC
    * Start sneakernet software from USB
    * Specify path to local representation
    * Chose export operation
    * Choose amount of messages to be copied to the USB drive and whether replication of the network should be possible
* Postcondition success: Events are all properly stored on the USB
* Postcondition failure: Error if anything goes wrong, f.ex. not enough storage on the USB drive

### Use Case 2:
* Name: Import
* Agents: Member of BACnet 
* Preconditions: 
    * Agents PC contains a local representation of the BACNet
    * Agent possesses a USB drive with our software and some events 
* Common process:
    * Connect USB drive to PC
    * Start sneakernet software from USB
    * Specify path to local representation
    * Chose import operation
* Postcondition success: Events on the USB drive are successfully merged into the local representation
* Postcondition failure: Error during merging f.ex. corrupt data

### Use Case 3:
* Name: New User
* Agents: Anyone who is permitted to join the BACnet with a PC
* Preconditions: 
    * Agent possesses a USB drive with our software and the ability to replicate the BACnet
* Common process:
    * Connect USB to PC
    * Start sneakernet software from USB drive
    * Choose "New User" or "Neuer Nutzer"
    * Specify path to directory where BACnet representation should be created
* Postcondition success: Agent possesses a local representation of the BACnet

### Use Case 4:
* Name: View USB drive's metadata 
* Agents: Any person that owns a USB drive that has been exported to
* Preconditions: USB drive has been exported to
* Common process:
    * Connect USB
    * Start sneakernet software from USB drive
    * Choose "Examine Events" operation
* Postcondition success: Events are displayed and can be navigated by the user

### Use Case 5:
* Name: Empty stick
* Agents: Any person that owns a USB that has been exported to
* Preconditions: Events should be present on the USB
* Common process:
    * Connect USB
    * Start sneakernet software from USB drive
    * Choose "Delete events" operation
* Postcondition success: USB drive is empty except for our software and possibly drivers
