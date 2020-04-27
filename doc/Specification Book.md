


Use Case 1:
Name: Export
Agents: Member of BACNet with an USB
Preconditions: Connect USB, start sneakernet
Common process:
Step 1: Choose "Export" and the amount of messages to be copied to the USB
Postcondition success: Messages are all properly stored on the USB and can be viewed via Use Case #3.
Postcondition failure: Failure message if anything goes wrong, EX. not enough storage

Use Case 2:
Name: Import
Agents: Any person that owns a USB that has been exported to
Preconditions: Exporting was successful.
Common process:
Step 1: Connect USB to any machine. In the sneakernet program choose "Import".
Postcondition success: Merge was successful. However the merge logic decides if the messages are valid and no duplicates.
Postcondition failure: Either the user is no member yet (Use Case #3). Error while merging EX. corrupt data.

Use Case 3:
Name: New User
Agents: Any person that owns a USB that has been exported to
Preconditions: Connect USB on any device, start sneakernet from USB
Common process:
Step 1: Choose "New User" or "Neuer Nutzer" and confirm your name.
Postcondition success: User is now a member of BACNet

Use Case 4:
Name: View Log
Agents: Any person that owns a USB that has been exported to
Preconditions: Connect USB, start sneakernet
Common process:
Step 1: Choose "View Log". The complete log available on the USB device should be presented
Postcondition success: Log is complete

