# I&S Group 2 – soundLink

## Overview

*	[Idea](#idea)
* [Implementation](#implementation)
*	[Compatibility](#compatibility)
* [Coordination](#coordination)
* [Tagebuch](#tagebuch)

## Idea
* Based on [quiet for android](https://github.com/quiet/org.quietmodem.Quiet)
* Implement an interface that allows users of the app Android SurfCity to reliably synchronize their logs over audible sound.
* See the current status of our implementation [here](https://github.com/RenatoFarruggio/quietmodem).

## Implementation
Interface with 2 methods:
* transmit(CBOR)
* receive() -> CBOR

## Compatibility
Packet format compatible with log requirements [here](https://github.com/cn-uofbasel/BACnet/blob/master/doc/BACnet-event-structure.md), and [Android SurfCity](https://github.com/ckschim/SurfCity-Android).

## Coordination

### Group 12:

| Coordination Points | What We Need | What We Give | Status |
|---|---|---|---|
| Sync data for insertion into database. Be able to take our packets and sync these to database without issues | Sync compatibility & Latest log data | Data (text, binary, etc.) for logs to sync | Awaiting more info and group’s vision|

### Group 10: 

| Coordination Points |    What We Need    |                       What We Give                         |      Status      |
|---------------------|--------------------|------------------------------------------------------------|------------------|
|         UI          | UI for Android app | Interface to transmit and receive CBOR packages over sound | Regular meetings |

## Tagebuch

All meeting notes are located in the Tagebuch, [here](https://github.com/cn-uofbasel/BACnet/blob/master/groups/02-soundLink/Tagebuch.md).

