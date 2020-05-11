# EventCreationTool

This is a simple tool for creating BACnet feeds and events.
Current version is 1.1

## Content

* [Requirements and installation](#requirements-and-installation)
* [Supported signing and hashing algorithms](#supported-signing-and-hashing-algorithms)
* [Quick start guide](#get-started)
* [Full API specification](#full-api-specification)
* [Changelog](#changelog)

## Requirements and installation
In order to use the tool, you have to install the following python packages:
* PyNaCl
* cbor2

We recommend to install them using pip:
```
> pip install cbor2
> pip install pynacl
```

The tool provides a python class PythonCreationTool which you can use as API. To use the tool you need the two 
python files `PythonCreationTool.py` and `Event.py`. Copy them over to your project (you could drop them in a 
separate folder) in order to use the tool.

We are thinking about creating a `pip install` package, but are currently busy.

## Supported signing and hashing algorithms
Currently we support the following signing algorithms:
* ED25519
* HMAC_SHA256

And the following hashing algorithms:
* SHA256

Feel free to contact us if you need different ones!

## Get started 
Once you installed the tool, you probably want to start off by creating a new feed. The simplest way to do so is by 
creating a new object of the class `EventFactory`:
```python
import EventCreationTool
ecf = EventCreationTool.EventFactory()
```
This will create a new feed. If you want to create multiple feeds, you can simply create multiple `EventFactory` 
objects. You can now create events on that feed by using the `next_event()` method  and 
passing your custom content as follows:
```python
new_event = ecf.next_event(content_identifier, content_parameter)
```
When using this, please stick to the conventions for BACnet 
([here at the bottom](https://github.com/cn-uofbasel/BACnet/blob/master/doc/BACnet-event-structure.md)). 
Thus `content_identifier` should be a string like `'yourapp/yourcommand'` and `content_parameter` could 
be whatever you want (but using dictionaries is probably most convenient). 
Our tool does not, however, enforce the convention. 

If you restart your application and need the factory for the same feed again, you can simply obtain the last event 
from your database and pass that event when creating the factory object like this:
```python
last_event =  # Obtain the last event of the feed you want to append to from the database
ecf = EventCreationTool.EventFactory(last_event)
```
Make sure that the event you pass is really the most recent one. Otherwise the event chain of your feed will diversify.

###Additional important information

The call `EventCreationTool.EventFactory()` will automatically create a `.key` file in your current working 
directory (i.e. the directory from which you ran the program that called the EventCreationTool). You can also 
specify another location to store your keys, as specified in the full API specification.

These files contain the private keys to your feeds. MAKE SURE TO NOT LOOSE THEM! If you loose these files, you will 
not be able to create new events (and our tool will throw some custom exceptions as specified 
[below](#full-api-specification))

The tools provides even more functionality as specified in the next section. There you will learn how to set custom 
private key paths, obtain private keys (you need them if you use hmac signing) or even set different signing 
and hashing algorithms.
Also, if you need a tool that allows more control, you could use the `EventCreationTool` class instead of 
`EventFactory`. API is specified below.

## Full API specification
here is some work in progress...

## Changelog
* V1.0: First release for extern use. API as specified [above](#full-api-specification).
* V1.1: Added EventFactory class for even simpler creation of events. Also some bugfixes and renaming.