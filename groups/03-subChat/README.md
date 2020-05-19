# I&S Security Gruppe 03_SubChat

> Our Group is creating user interface for a chat. The user interface has to be intuitive and should integrate the data given to us foremost by group 07. Since the creation of a User Interface is our main objective, it's intuitiveness is of critical importance to us

## Content
1. [Prototype](#Prototype)
    1. [Structure](#Structure)
    2. [Nice-to-know](#NiceToKnow)
2. [Final Version](#Final)
    1. [Prerequisites](#Prerequisites)
    2. [How to use the app](#HowTo)
3. [Protocols](#Protocols)
4. [Links](#Links)

## Prototyp
### Structure
The following image explains, how the code is structured

<p align="center"><img src="Grafiken/Datenbank.jpeg" alt="drawing" width="500"/></p>

The Prototype is making use of the demo files (BACnet/src/demo/lib). They have been modified to take inputs from methods (instead of the command line as they were indended to).

### Nice-to-know
How to use the demo files to create entries:

> ./crypto.py >alice.key
> ./feed.py --keyfile alice.key alice.pcap create
> 	["write entries like this!"]
> ./feed.py alice.pcap dump
> 
> 
> ./feed.py --keyfile alice.key alice.pcap append
> 	['write entries like this!']

## Final Version
### Prerequisites 
We had two options to build our User Interface: JavaFX and Python's TkInter. Even though TkInter is much more limited in its functionality if we compare it to our first choice JavaFX, we decided us for TkInter for better integrity with the other groups code. 
We also have other modules which has to be installed on your OS before you can use it. The [links](#Links) to the modules we used are at the end of this README-file. 
Short and sweet for Linux users; They can install the modules with these commands: 
> apt-get install python-tk

> apt install python3-pip

> pip install pickle-mixin

> pip install pyglet

> sudo apt-get install python3-pil python3-pil.imagetk

> pip install pybase64

After these modules are installed, you are ready to use our app.

### How to use the app
Go to the "SubjectiveChat"-folder and open the terminal. From there you can start the python-file "app.py". The login-window should pop up:

<p align="center"><img src="Grafiken/Screenshots/Login.PNG" alt="drawing" width="350"/></p>

Here you can choose your username (must have max. 16 letters) and your personal key file will be created and the main windows comes. 
_Important: The login windows only pops out if you haven't logged in yet._

<p align="center"><img src="Grafiken/Screenshots/Start.PNG" alt="drawing" width="400"/></p>

On the upper-left there is a Bar with two buttons: 

<p align="center"><img src="Grafiken/Screenshots/create-join-bar.PNG" alt="drawing" width="500"/></p>

Example of creating a chat: 

<p align="center"><img src="Grafiken/Screenshots/create-bar.PNG" alt="drawing" width="500"/></p>

Here you can choose between a private chat and a group chat.

<p align="center"><img src="Grafiken/Screenshots/create-group-bar.PNG" alt="drawing" width="500"/></p>

In case you want to create a group chat you can enter a group name (max. 16 letters). Otherwise you will get a chatID which you can confirm. 

Example of joining a chat:

<p align="center"><img src="Grafiken/Screenshots/join-bar.PNG" alt="drawing" width="500"/></p>

Here you can type in the chatID, which you can get from your chatpartner (who created the chat). 
If the chatID is valid you can chat now.

<p align="center"><img src="Grafiken/Screenshots/Chat-Alice-Bob.PNG" alt="drawing" width="1000"/></p>

Example of group chat:

<p align="center"><img src="Grafiken/Screenshots/Group-Chat.PNG" alt="drawing" width="500"/></p>

## Protocols

Protocols from meeting can be found [here](https://github.com/cn-uofbasel/BACnet/tree/master/groups/03-subChat/Protocols).

## Links

[Tkinter](https://docs.python.org/2/library/tkinter.html)
[PIP](https://pypi.org/project/pip/)
[Pickle](https://docs.python.org/3/library/pickle.html)
[Pyglet](https://pypi.org/project/pyglet/)
[Pillow](https://pypi.org/project/Pillow/)
[base64](https://docs.python.org/3/library/base64.html)

