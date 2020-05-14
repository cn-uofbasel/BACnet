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

##### added after May 7th:
* software needs to store metadata about its users BACnet representations to call group 4s API
    * from this it has to calculate which events aren't relevant in order to avoid waste of storage
    * in order to save this information reliable we need to decode usernames and corresponding present feed_ids and their current seq_nos in a savable way
* this information needs to be updated accordingly and the library of saved events should be reexamined after importing to keep storage as free as possible    

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
    * Chose export operation
    * Choose amount of messages to be copied to the USB drive
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
    * Chose import operation
* Postcondition success: Events on the USB drive are successfully merged into the local representation and events no longer needed deleted from the USB's storage
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
* Postcondition success: USB stick keeps track of the new user and considers that it should export more events the next time it is used 

### Use Case 4:
* Name: View USB drive's metadata 
* Agents: Any person that owns a USB drive that has been exported to
* Preconditions: USB drive has been exported to
* Common process:
    * Connect USB
    * Start sneakernet software from USB drive
    * Choose "Examine Events" operation
* Postcondition success: Metadata about the sticks content is displayed such as a list of users, number of feeds/events and storage occupied

### Use Case 5:
* Name: Empty stick
* Agents: Any person that owns a USB that has been exported to
* Preconditions: Events should be present on the USB
* Common process:
    * Connect USB
    * Start sneakernet software from USB drive
    * Choose the "Delete content" option and choose what data to delete (whole program, stored events, user list)
* Postcondition success: USB drive no longer stores the data selected
