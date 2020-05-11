# EventCreationTool

This is a simple tool for creating BACnet feeds and events.
Current version is 1.0

## Content

* [Requirements and installation](#requirements-and-installation)
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

## Get started 
Once you installed the tool, you probably want to start off by creating a new feed. 


## Full API specification
The class contains the following methods:

## Changelog
* V1.0: First release for extern use. API as specified [above](#full-api-specification).
* V1.1: Added EventFactory class for even simpler creation of events. Also some bugfixes and renaming.