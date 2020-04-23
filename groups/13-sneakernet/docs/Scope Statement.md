# Specification Book
* Project title: Sneakernet for the BACnet
* Developers: Leonhard Badenberg, Patrik Bütler, Luka Obser


## 1. Visions and Goals 

## 2. Stakeholders

/S10/ Developers
/S20/ Professor and assistants
/S30/ Users of final product
/S40/ Group #10

## 3. General Conditions and Context

## 4. Functional Requirements

## Attachment A: Use-cases

### Use Case 1:
* Name: Export
* Agents: Member of BACNet with an USB
* Preconditions: Have a working database of BACNet
* Common process:
    * Connect USB, start sneakernet
    * Choose "Export"
    * Choose amount of messages to be copied to the USB
* Postcondition success: Messages are all properly stored on the USB and can be viewed via Use Case #3.
* Postcondition failure: Failure message if anything goes wrong, EX. not enough storage

### Use Case 2:
* Name: Import
* Agents: Any person that owns a USB that has been exported to
* Preconditions: A log is available on the USB.
* Common process:
    * Connect USB to any machine.
    * In the sneakernet program choose "Import".
    * Enter the path for the log to be imported (as someone can have multiple ones on his machine)
* Postcondition success: Merge was successful. However the merge logic decides if the messages are valid and no duplicates.
* Postcondition failure: Either the user is no member yet (Use Case #3). Error while merging EX. corrupt data.

### Use Case 3:
* Name: New User
* Agents: Any person that owns a USB that has been exported to
* Preconditions: USB requires important meta data that allows you the be a new user
* Common process:
    * Connect USB on any device, start sneakernet from USB.
    * Choose "New User" or "Neuer Nutzer" and confirm your name.
    * Enter your name
* Postcondition success: User is now a member of BACNet

### Use Case 4:
* Name: View stick's metadata 
* Agents: Any person that owns a USB that has been exported to
* Preconditions: Have a working log on the USB
* Common process:
    * Connect USB, start sneakernet
    * Choose "View Log". The complete log available on the USB device should be presented
* Postcondition success: Log is complete

### Use Case 5:
* Name: Empty stick
* Agents: Any person that owns a USB that has been exported to
* Preconditions: A log should be present on the USB
* Common process:
    * Connect USB, start sneakernet
    * Choose "Delete Log". The complete or partial log will be deleted
* Postcondition success: Log is deleted
