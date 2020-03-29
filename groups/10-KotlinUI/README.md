# Kotlin SSB UI

## Idea
Our aim is to further develop the source code of an existing app called Android SurfCity which is a SSB client-prototype. We want to add modifications and new features to the app.
Android SurfCity is a social media application developed as a bachelor project by Cerdik Schimsar.
There are three different places we‘ll be working at.

* Onboarding: New SSB clients can only start their first interaction with other clients by finding new peers with the help of pubs. In our case, we want to be able to abstain form the internet.
For example, a SSB user should have the possibility to connect to their first friend by using bluetooth, sound or QR-Code to exchange ID‘s.


* Log format: Each log entry has the same log format. A log is formatted in ASCII and JSON and has rules how it must be constructed. The goal is to exchange the previous format (ASCII and JSON) with a binary format.


* Interchanging data: TBD


## Requirements
For the project each member needs a computer with Android Studio installed. An Android smartphone is desired but optional since Android studio allows to run apps in an Android VM for testing purposes.

## Links
* Android Surf City repository: https://github.com/ckschim/SurfCity-Android
* Our fork: https://github.com/TravisPetit/SurfCity-Android
* Christian Tschudin’s non-Android implementation of Surf City: https://github.com/cn-uofbasel/SurfCity
