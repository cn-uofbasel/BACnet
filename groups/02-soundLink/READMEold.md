# I&S Group 2 – soundLink

## Overview

*	[Idea](#idea)
* [Implementation](#implementation)
*	[Compatibility](#compatibility)
* [Coordination](#coordination)
* [Tagebuch](#tagebuch)

## Idea
* QR Code Link using [Zxing](https://github.com/zxing/zxing) library
* Implement an interface that allows two Android phones to send and receive QR codes between each other
* See the current status of our implementation [here](https://github.com/RenatoFarruggio/qrCodeReaderWriter).

## Implementation
Interface with 2 methods:
* transmit(CBOR)
* receive() -> CBOR

## Compatibility
Packet format compatible with log requirements [here](https://github.com/cn-uofbasel/BACnet/blob/master/doc/BACnet-event-structure.md)

## Coordination

<!--
### Group 12:

| Coordination Points | What We Need | What We Give | Status |
|---|---|---|---|
| Sync data for insertion into database. Be able to take our packets and sync these to database without issues | Sync compatibility & Latest log data | Data (text, binary, etc.) for logs to sync | Awaiting more info and group’s vision|
-->

### Group 12: 

| Coordination Points |    What We Need    |                       What We Give                         |      Status      |
|-----------------------------------|--------------------|-------------------------------------------------------|-------------------------|
| Sync data for insertion into database. Be able to take our packets and sync these to database without issues | Sync compatibility & Latest log data | Data (text, binary, etc.) for logs to sync & Number of packets and size | Meeting after implementation |

## Tagebuch

All meeting notes are located in the Tagebuch, [here](https://github.com/cn-uofbasel/BACnet/blob/master/groups/02-soundLink/Tagebuch.md).

