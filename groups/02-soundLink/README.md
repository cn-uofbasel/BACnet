# ~~soundLink~~ -> qrLink

## Contributors
* Renato Farruggio
* Caroline Steiblin

## Idea
Implement an interface that allows two Android phones to send and receive QR codes between each other, using [Zxing](https://github.com/zxing/zxing) library. 
Synchronize any database from BACnet from an Android device to another Android device over qr codes.


## Usage
Our code is completely integrated into group 10 exKotlinUI. See their implementation [here](https://github.com/TravisPetit/chaquopy-console).  
User A can synchronize with user B over qr codes. They interchange codes until synchronization is complete. This synchronisation is asynchronous, which means that a synchronisation from A to B only updates B.  

We offer audio feedback:  
Higher beep (50ms): Already received this qr code  
Lower beep (50ms): New qr code received  
Lower beep (2000ms): Synchronization complete  
**Note**: Without a license of Chaquopy the usage time is limited to 10 minutes continuously. We do have a license, but are not allowed to make it public.

## Compatibility
Packet format compatible with [BACnet log requirements](https://github.com/cn-uofbasel/BACnet/blob/master/doc/BACnet-event-structure.md). But we can send any bytes that standard UDP packets can send. We have adapted our code to the transport interface of logSync.


## API

To open the ScanCodeActivity, the following code has to be implemented in an onClickListener().
```java
// Sender (Device A)
Intent startScannerIntent = new Intent(getApplicationContext(), ScanCodeActivity.class);

startScannerIntent.putExtra("device", 'A');
startScannerIntent.putExtra("packetsize", 12);

startActivity(startScannerIntent);
```
```java
// Receiver (Device B)
Intent startScannerIntent = new Intent(getApplicationContext(), ScanCodeActivity.class);

startScannerIntent.putExtra("device", 'B');
startScannerIntent.putExtra("packetsize", 12);

startActivity(startScannerIntent);
```
In addition, the xml files activity_scan_code.xml and image_layout.xml have to be imported, aswell as the whole python packet.


## Transport-Protocol
The we use the protocol described by [logSync](https://github.com/cn-uofbasel/BACnet/tree/master/groups/12-logSync).

## Diary
All meeting notes are located in [the diary](https://github.com/cn-uofbasel/BACnet/blob/master/groups/02-soundLink/documents/Tagebuch.md).

## TODO:
* ~~Write proper README~~
* ~~Access front camera~~
* ~~Implement [asking user for permission to use camera](https://github.com/ParkSangGwon/TedPermission)~~
* ~~Test if QR code gets recognized through front camera (It does!)~~
* ~~Implement beep sound as feedback for qr code recognition~~
* ~~Disable screen rotation~~
* ~~Implement [Android Image Dialog/Popup](https://stackoverflow.com/questions/7693633/android-image-dialog-popup) and test if it works as expected.~~
* ~~In case, above Image Dialog does not work, find another way to display qr code while having the camera open.~~
* ~~Implement dialog over qr code~~
* ~~Make qr code size adaptive to screen size (maximal but not bigger than screen)~~
* ~~Implement packet splitting (doesn't seem like we need that)~~
* ~~Find out how many bps we can send (around 500bytes/packet, maybe up to 2k) should be fine !~~
* ~~Add [Chaquopy](https://chaquo.com/chaquopy/) to our project to run python files~~
* ~~Fix __fatal__ bug: Chaquopy can't import python library "cbor2" (Fix by downgrading to cbor)~~
* ~~__Encode and Decode qr code in base64 encoding__ (Does not work with our current setup afaik)~~
* ~~If Chaquopy works as exspected, add it to the documentation over on [BACnet](https://github.com/cn-uofbasel/BACnet/tree/master/groups/02-soundLink)~~
* ~~Merge readme from [BACnet](https://github.com/cn-uofbasel/BACnet/tree/master/groups/02-soundLink) into this readme.~~
* ~~Figure out how to use the [eventCreationTool](https://github.com/cn-uofbasel/BACnet/tree/master/groups/04-logMerge/eventCreationTool) on our android app, according to [this](https://chaquo.com/chaquopy/doc/current/java.html)~~
* ~~Make a license file (preferably the same, BACnet uses)~~
* ~~Get a [license for Chaquopy](https://chaquo.com/chaquopy/license/?app=ch.unibas.qrscanner)~~
* ~~Specify Interface with group 12 (syncLog). In the ideal case, we can import their code like the eventCreationTool above.~~
* ~~__Import logSync__~~
* ~~Interface testing: Can we import logSync?~~
* ~~Interface testing: Do callbacks work from python back to java?~~
* ~~Rewrite [API](#api)~~
* ~~Rewrite [Execution](#execution)~~
* ~~Rewrite [Python-Example](#python-example)~~
* ~~Remote add this repo to BACnet and pull~~
* ~~Implement packet splitting~~
* Write down theoretical advanced transport protocol
* ~~Implement advanced transport protocol~~
* ~~Integrate updated logSync code~~
* ~~Integrate into exKotlinUI~~
* ~~Add 2 input variables for ScanCodeActivity. One for Path (by calling getApplicationContext().getFilesDir().getPath()), One for Device ('A' or 'B')~~
* ~~Get logSync to run successfully~~
* ~~Fix audio errors~~
* Get License for Chaquopy
* ~~Add functionality to exit qr code at any time.~~
* (Figure out where "[ZeroHung]zrhung_get_config: Get config failed for wp[0x0008]" error is coming from)
* Disable automatic screen rotation
* Tap to open QR code again
* Add some kind of feedback on how many packets were sent and on which step they are.
* Make a demo video
