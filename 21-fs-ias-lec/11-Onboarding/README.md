# Onboarding 2.0


## Requirements and installation
Additionally to the already needed python packages, you have to install the following:
* pybluez2
* openpyxl

## Quick start guide 
This project is already integrated within the Demo D Version.
To use the new Onboarding Feature you can simply start it through the Feed Control User Interface.
Start it with:

```
python feed_control.py ui
```
Afterwards select the `Bluetooth-Onboarding` Button. A new window should open with the option to choose between `Client` or `Server`. You and your partner both have to choose one of them. It is important both of you have Bluetooth turned on on your device. If you chose the Client, you have to enter the name of your partner's device into the terminal.  
Afterwards you should receive the ID of your partner and if it was your first time connecting to someone, a new Excel-File called `data.xlsx` should have been generated with the received ID written inside. If you have already generated your data.xlsx make sure to have it closed before choosing between Client or Server.

## Check if it worked!
Before you connect with your partner  via Bluetooth, it should not be possible to see your partner's feed with the `UpdateFeedIDs` Button inside the Feed Control User Interface.   
After connecting with your partner it should appear normally ready to be trusted!  

**Note:** _For all needed steps see  Video of Demo_D_Procedure until the first appearance of the feed in the Feed Control UI._
