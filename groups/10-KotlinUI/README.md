# Kotlin SSB UI

## Idea
Our aim is to develop an Android application that serves as a BACnet client.
It will be a user interface where the back-end is provided by the other groups.
We want to create an application whose visual/interactive design is inspired by popular Secure Scuttlebutt applications. It's designed to be user friendly.

## Implementation
Since we work with Java/Kotlin and most of the groups work with Python we ensured compatibility through Chaquopy.
Chaquopy is a Python SDK for Android that enables developers to intermix Java,Kotlin and Python.

## Dependency
At the time of this writing we depend on group 7, log store. They will provide us a database and an interface to retrieve and insert information. 

## Project state
At this moment we can call functions written in Python from Java/Kotlin to process the data. The test database provided by group 7 is already integrated into the android project. The whole front-end is written in Java/Kotlin.

## Next steps
Currently we are working with the demo code from the BACnet repository. As soon as group 7 finishes their implementation of the functions we need, we will no longer work with PCAP files and we will store out feeds directly in the database.
We still need to figure out how to integrate *Onboarding. We hope to clarify this matter in the next workshop.

*Onboarding: New SSB clients can only start their first interaction with other clients by finding new peers with the help of pubs. In our case, we want to be able to abstain form the internet.
For example, a SSB user should have the possibility to connect to their first friend by using bluetooth, sound or QR-Code to exchange ID‘s.



## Requirements
For the project each member needs a computer with Android Studio installed. An Android smartphone is desired but optional since Android studio allows to run apps in an Android VM for testing purposes.

## Links
* Our fork: https://github.com/TravisPetit/chaquopy-console
* Chaquopy: https://chaquo.com/chaquopy
