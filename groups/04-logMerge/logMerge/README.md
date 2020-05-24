# LogMerge

This is our project that provides an API to BACnet transport layer groups for importting 
and exporting events from the local BACnet database.

## Content

* [Requirements and installation](#requirements-and-installation)
* [Supported signing and hashing algorithms](#supported-signing-and-hashing-algorithms)
* [Quick start guide](#quick-start-guide)
  - [Additional important information](#additional-important-information)
* [Full API specification](#full-api-specification)
  - [Private key file format](#private-key-file-format)
  - [exception HashingAlgorithmNotFoundException](#exception-hashingalgorithmnotfoundexception)
  - [exception SigningAlgorithmNotFoundException](#exception-signingalgorithmnotfoundexception)
  - [exception KeyFileNotFoundException](#exception-keyfilenotfoundexception)
  - [exception IllegalArgumentTypeException](#exception-illegalargumenttypeexception)
  - [class EventFactory](#class-eventfactory)
  - [class EventCreationTool](#class-eventcreationtool)
* [Changelog](#changelog)

## Requirements and installation
In order to use the tool, you have to install the following python packages:
* PyNaCl
* cbor2
* sqlalchemy (for dependencies)
* testfixtures (for dependencies)

We recommend to install them using pip:
```
> pip install cbor2
> pip install pynacl
> pip install sqlalchemy
> pip install testfixtures
```

The needed dependencies to use this tool come together with our package. Just make sure you have the packages installed 
as mentioned above. The API provides 3 basic functions, that are described in the section 
[API](#full-api-specification).
You can simply copy over the folder `logMerge` to your project and there you go!

We are thinking about creating a `pip install` package, but are currently busy. As for now, you can install the 
dependencies by running `pip install path/to/logMerge` (or simply `pip install .` if your command line 
is inside the `logMerge` folder). 

## Supported signing and hashing algorithms
Currently we support the following signing algorithms:
* ed25519

And the following hashing algorithms:
* sha256

Feel free to contact us if you need different ones!

## Quick start guide 
Please also look at the [**Additional important information**](#additional-important-information) below!


## Full API specification
#### class EventFactory
The class logMerge is the API of this tool.

```python
__init__(last_event=None, path_to_keys=None, path_to_keys_relative=True,
             signing_algorithm='ed25519', hashing_algorithm='sha256')
```
* Returns: A new object of the class.
* Throws: `SigningAlgorithmNotFoundException`, `HashingAlgorithmNotFoundException`
* Parameters:
  - optional `last_event`: Type: `bytes` (cbor encoded as you can get it from the database).
  Event on which base the object is created. Sets up the created factory to yield following events. If this is not 
  specified, a new feed will be created.
  - optional `path_to_keys`: Type: `str`. If you need a specific path to private keys. Can be a relative or absolute 
  path (See following parameter). Default is the current working directory.
  - optional `path_to_keys_relative`: Type: `bool`. Must be set to `False` if the above specified path was an absolute 
  path.
  - optional `signing_algorithm`: Type: `str`. The signing algorithm you want to use. Refer to 
  [here](#supported-signing-and-hashing-algorithms) for supported algorithms.
  - optional `hashing_algorithm`: Type: `str`. The hashing algorithm you want to use.
* NOTE: After creating a new feed (creating EventFactory object not using `last_event` parameter), you will have to 
immediately create a first event using the `first_event()` method and add it to the database. See also in the quick 
start guide.
* NOTE2: `signing_algorithm` and `hashing_algorithm` will be ignored if you specify a `last_event`. In this case, the 
algorithms will be chosen to match the previous events of the feed. This is to protect you from misusing a feed.

```python
get_feed_id()
```
* Returns: Type: `bytes`. The feed id (i.e. the public key) of the associated feed.

```python
get_private_key()
```
* Returns: Type: `bytes`. The private key of the associated feed. If you need to obtain the key for a partner when using 
the `hmac` signing algorithms.
* Throws: `KeyFileNotFoundException`
