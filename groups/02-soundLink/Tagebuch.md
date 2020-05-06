# SoundLink Meeting Notes

## 24.04.2020 - Meeting with Prof. Tschudin

Attendees:
* Caroline Steiblin
* Renato Farruggio
* Prof. Tschudin

Goal:
* Align on new implementation plan

Comments:
* Switch to QR Code
* Primarily transport layer

### Done so far:
* Initial implementation of zxing to transmit & receive datagram
* Front camera activated

### Next step:
* Show QR code & camera at same time
* Asking user permissions to access camera
* Be able to have two phones facing each other able to transmit & receive - fully implement transmit & receive
* Control size of packets

### Open issues:
* Two Android phones for Caroline

### Group coordination:
* Group 12 - Need to be able to communicate number of packets and size

## 24.04.2020 - Meeting with logSync group

Attendees:
* Caroline Steiblin
* Renato Farruggio
* Alexander Oxley
* Carlos Tejera

Goal:
* Align on coordination

Comments:
* Need to clarify packets & log types

## 17.04.2020 - Meeting with Kotlin group

Attendees:
* Caroline Steiblin
* Renato Farruggio
* Sanja Popovic
* Nour Hany
* Travis Rivera Petit

Goal:
* Align on coordination plan

Comments:
* We need to communicate technical specs. (frequencies)
* Kotlin group to create own app
* We use a socket with sender and receiver, receiver always running

Methods:
* transmit(CBOR)
* receive() --> CBOR

Private messages - feed involvement

Sending out pre-defined packets compliant with CBOR/PCAP

Next steps:
* Work on transmit & receive methods

Clarifications:
* How to deal with feed (private messages)

Next alignment meeting: 
* 22.04. at 14.00

## 13.04.2020

Attendees:
* Caroline Steiblin
* Renato Farruggio

Goal:
* Go through updated documentation & plan for update

Comments:
* Android Studio implementation runs without error, but sending/receieving on different frequencies, so not yet functional
* Need compatibility to Android Surf City?
* Created a git repo for code - https://github.com/RenatoFarruggio/quietmodem

## 12.04.2020

Attendees:
* Caroline Steiblin
* Renato Farruggio

Goal:
* Expectations for status presentation
* Set plan for implementation

ToDos:
* Update ReadMe to outline our outputs and clearly define what we are doing for other groups
* Plan out collaboration with other groups
* Solve errors in Android Studio

Comments:
* Current plan: Android implementation of Quiet
* Will need to build mini transport layer
* If idea for Android Studio implementation does not work, then revert to extending old project - for this let's wait and discuss with the TAs

Next Steps:
* Follow-up call on 13.04.to go over update

## 23.03.2020

Attendees:
* Caroline Steiblin
* Renato Farruggio
* Prof. Tschudin

Goal: 
* Short distance communication via sound from phone to phone
* Letters and numbers over frequency or tone (0-9, a-z, punctuation), around 50 characters to encode
* Link to other group - Kotlin group to write us an app?
* Overview of other projects (how could we extend it?)

Previous projects:
* Try to extend to Android - Quiet already has some functionality here

Coordination with other groups:
* Compatibility with 4 (Nikodem, Guni, Joey), 12 (Alexander Oxley, Carlos Tejera, Pascal Kunz)
* Be compatible with 5,6,8,9
* Kotlin - 10 (Sanja, Nour, Travis)

Requirements:
* TBD
* Continuous documentation of actions
* See in April with the midterm evaluation
* Create something functional for integration

Comments:
* Packet size limitations - check technology allowances
* Need to build mini stack to check functionality for tests - mini transport layer
* Avoid IP
* Smartphone aspect interesting
* With ideas contact Carlos (TA) and/or Prof. Tschudin
* Can we go further than previous groups' work - longer distance than just 5cm?

Next Steps:
* Android functionality - research this (before contacting Kotlin group) / prototype
* Read through past project & see if we can extend
