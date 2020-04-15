# I&S Group 2 – soundLink

## Overview

*	[Idea](#idea)
*	[Compatibility](#compatibility)
* [Coordination](#coordination)
* [Tagebuch](#tagebuch)

## Idea
* Based on [quiet](https://github.com/quiet/org.quietmodem.Quiet)
* Implement quiet as an Android application to transmit messages as sound between Android devices
* See the current status of our implementation [here](https://github.com/RenatoFarruggio/quietmodem).

## Compatibility
Packet format compatible with log requirements [here](https://github.com/cn-uofbasel/BACnet/blob/master/doc/BACnet-event-structure.md), and [Android SurfCity](https://github.com/ckschim/SurfCity-Android).

## Coordination
* Compatibility with groups 4 (logMerge) & 12 (logSync)
* Compatibility with log requirements outlined in the above section with groups 5 (LoRaLink), 6 (longFi), 8 (QR), 9 (LoRaSense)
* Possible UI implementation with group 10 (Kotlin)

### Group 4:

| Coordination Points | What We Need | What We Give| Status|
|------------------------------|---------------------|------------------------------------------------|----------------------------------|
| Merge data for insertion into database. Be able to take our packets and add these to database | Transport requirements – compatibility & Latest log data | Data (text, binary, etc.) for logs to merge | Awaiting more info and group’s vision|

### Group 12:

| Coordination Points | What We Need | What We Give| Status|
|------------------------------|---------------------|------------------------------------------------|----------------------------------|
| Sync data for insertion into database. Be able to take our packets and sync these to database without issues | Sync compatibility & Latest log data | Data (text, binary, etc.) for logs to merge | Awaiting more info and group’s vision|

### Group 5: 

| Coordination Points | What We Need | What We Give| Status|
|------------------------------|---------------------|------------------------------------------------|----------------------------------|
| Packet sizes | Packet size limitations for long-distance communication| None | Awaiting more info and group’s vision|

### Group 6: 

| Coordination Points | What We Need | What We Give| Status|
|------------------------------|---------------------|------------------------------------------------|----------------------------------|
| Transportation requirements | Transportation compatibility, especially if we need to build mini transport layer| None | Awaiting more info and group’s vision|

### Group 8: 

| Coordination Points | What We Need | What We Give| Status|
|------------------------------|---------------------|------------------------------------------------|----------------------------------|
| Potential for QR compatibility| Log requirements for QR| None | Awaiting more info and group’s vision|

### Group 9: 

| Coordination Points | What We Need | What We Give| Status|
|------------------------------|---------------------|------------------------------------------------|----------------------------------|
| Sensor compatibility | Log requirements for sensor| None | Awaiting more info and group’s vision|

### Group 10: 

| Coordination Points | What We Need | What We Give| Status|
|------------------------------|---------------------|------------------------------------------------|----------------------------------|
| UI | UI for sound communication app| Encoder, sender, receiver & decoder for data (text, binary, etc.) packets | Awaiting more info and group’s vision & Figuring out if we just build an economical UI ourselves|

## Tagebuch

All meeting notes are located in the Tagebuch, [here](https://github.com/cn-uofbasel/BACnet/blob/master/groups/02-soundLink/Tagebuch.md).

