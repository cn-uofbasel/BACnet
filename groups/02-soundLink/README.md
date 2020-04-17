# I&S Group 2 – soundLink

## Overview

*	[Idea](#idea)
* [Implementation](#implementation)
*	[Compatibility](#compatibility)
* [Coordination](#coordination)
* [Tagebuch](#tagebuch)

## Idea
* Based on [quiet](https://github.com/quiet/org.quietmodem.Quiet)
* Implement quiet as an Android application to transmit messages as sound between Android devices
* See the current status of our implementation [here](https://github.com/RenatoFarruggio/quietmodem).

## Implementation
* transmit(CBOR)
* receive() -> CBOR

## Compatibility
Packet format compatible with log requirements [here](https://github.com/cn-uofbasel/BACnet/blob/master/doc/BACnet-event-structure.md), and [Android SurfCity](https://github.com/ckschim/SurfCity-Android).

## Coordination

### Group 12:

| Coordination Points | What We Need | What We Give| Status|
|------------------------------|---------------------|------------------------------------------------|----------------------------------|
| Sync data for insertion into database. Be able to take our packets and sync these to database without issues | Sync compatibility & Latest log data | Data (text, binary, etc.) for logs to sync | Awaiting more info and group’s vision|

### Group 10: 

| Coordination Points | What We Need | What We Give| Status|
|------------------------------|---------------------|------------------------------------------------|----------------------------------|
| UI | UI for sound communication app| Encoder, sender, receiver & decoder for data (text, binary, etc.) packets | Regular meetings|

## Tagebuch

All meeting notes are located in the Tagebuch, [here](https://github.com/cn-uofbasel/BACnet/blob/master/groups/02-soundLink/Tagebuch.md).

