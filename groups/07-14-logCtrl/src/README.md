# logStore

logStore is a Python library to enable both application groups as well as the network layer groups to store, retrieve and filter the data they need to provide their respective services.

## Content

* [Installation](#installation)
* [Usage](#usage)
  - [Application layer](#application-layer)
    * [What we need to build you an interface](#what-we-need-to-build-an-interface-for-your-application-group)
    * [Example for requirements](#example-for-requirements)
    * [How to use it in code](#how-to-use-it-in-code)
  - [Network layer](#network-layer)
    * [Current status](#current-status)
    * [Goal](#goal)
* [Testing](#testing)
* [Contributing](#contributing)
* [License](#license)
* [Contributing](#contributing)
* [Changelog](#changelog)

## Installation

Download the package 07-14-logCtrl from the [Github repository](https://github.com/cn-uofbasel/BACnet/tree/master/groups/07-14-logCtrl)

Unzip the package into any folder. 

## Usage

Usage of logCtrl can be split up in the usage for the application layer groups and the network layer groups. Important for usage is that the groups use the [EventCreationTool](https://github.com/cn-uofbasel/BACnet/tree/master/groups/04-logMerge/eventCreationTool) provided by group 04.

#### Application layer:

Most application layer groups have requested specific interfaces for their applications which have been subsequently implemented by us. If your applications needs another interface please don't hesitate to contact us.

If an application group would prefer to implement the functionality themselves they may access the same functionalities as the newtork layer groups to get and insert cbor events into the database. Those methods can be found in `groups/07-14-logCtrl/src/logStore/appconnconnection.py`.

##### What we need to build an interface for your application group:

We would need the data format you are using, especially the content identifier (has to have the form `application/action`) and the corresponding content parameters (which may also be empty). It is easiest if you provide us with some detailed use cases of you applications so that we may implement the necessary database functionality to allow your application to retrieve the data in a timely fashion.

##### Example for requirements:

An example could be:

| content identifier | corresponding setter | data format |
|-------------|-----------------|---|
| `chat/msg`    | `send_msg(event)` where event is an event created by the `eventCreationTool` and of type `bytes` | `{'msg': 'Hello', 'Timestamp': 1234, 'chatId': 'sda3432d34'}` |
| `chat/newChat`  | `create_chat(event)` where event is as described before | `{'chatId': 'sda3432d34', 'status': 'open'}` | 
| `chat/closeChat` | `close_chat(event)` where event is as described before | `{'chatId': 'sda3432d34', 'status': 'closed'}` | 

| function name | parameter | return value |
|-------------|-----------------|---|
| `get_feed_ids`    | empty | returns a list of all currently open chatIds |
| `get_last_msg_from_chat_id`  | `chat_id` type string | returns a message as `string` and the corresponding timestamp as `int` | 
| `get_all_msgs_from_chat_id` | `chat_id` type string | returns a list of tuples of message as `string` and the corresponding timestamp as `int` | 

##### How to use it in code:

The application group would then get a corresponding class where all those functions can be imported from. In this example we would call this class `chat_connection` and it could be used correspondingly:

```python
from logStore.appconn.chat_connection import ChatFunction as cf

chat_id = '21b1235u4'
ecf = EventFactory()
new_event = ecf.next_event('whateverapp/whateveraction', {'oneKey': 'somevalue', 'someotherkey': 1})
cf.insert_chat_msg(new_event)

cf.get_chat_since(application, timestamp, feed_id, chat_id)
cf.get_full_chat(application, feed_id, chat_id)
cf.get_last_event(feed_id)
```

#### Requirements

Before you can start your Application for the first time you'll have to run the feed controller for at least ones!

``python feed_control.py cli`` for using the command-line interfae

*Coming soon!*
``python feed_control.py gui`` for using the graphical interface 

Your own masterfeed will then be generated, without a masterfeed the database won't accept your data. 

Inside the feedcontroller you can then configure on who to trust and whom you won't. The list of feeds is generated from the masterfeeds from other user. So before you can start trusting other users you'll have to collect masterfeeds.

There are multiple usages for the CLI:

|cmd|parameter|return value|explanation|
|-------------|-----------------|---|-------|
|`-p`| |`list` of `feeds`|Prints a list of feeds with their corresponding index. For each masterfeed the childfeeds will be printed indented.|
|`-t`|`i` master index `j` child index| |Sets a given feed to trusted.|
|`-ut`|`i` master index `j` child index| |Sets a given feed to untrusted.|
|`-r`| |current radius|Prints the current radius on to the console.|
|`-r`|`radius` as integer| |Changes the current set radius to the new value.|
|`-n`| |current name|Prints the current username you have.|
|`-n`|`name`| |Changes your username to the new name.|
|`-reload`| | |If there were any changes to database on runtime you can load the new data with this command.|
|`-q`| | |Exit the program|

#### Network layer:

##### Current status:
Currently both group 4 and 12 can access the database with the functions inside `logStore/transconn/database_connection` and currently consist of:

| function name | parameter | return value |
|-------------|-----------------|---|
| `add_event(event)`    | `event` type `bytes` | adding an event originally created by an `eventCreationTool` to the database |
| `get_current_seq_no(feed_id)`  | `feed_id` type `bytes` | returns the highest sequence number as `int` or -1 if no sequence number exists to this feed id | 
| `get_event(feed_id, seq_no)` | `feed_id` type `bytes`, `seq_no` type `int` | returns an event as `bytes` or None if no such event exists | 
| `get_current_event(feed_id)` | `feed_id` type `bytes` | returns an event as `bytes` or None if no such event exists | 
| `get_all_feed_ids()` | empty | returns a list of feed ids of type `bytes` | 
| `check_incoming(feed_id, app_name)` | bool | returns whether an incoming feed id is trusted | 
| `check_outgoing(feed_id)` | bool | returns whether an outgoing feed id is trusted | 


The functionality can be used as described following:

DatabaseConnector:

```python
from logStore.transconn.database_connector import DatabaseConnector as dc

chat_id = '21b1235u4'

dc.add_event(event)

dc.get_current_seq_no(feed_id)
dc.get_event(feed_id, seq_no)
dc.get_current_event(feed_id)
dc.get_all_feed_ids()
```

Verification:

```python
from logStore.verific.verify_insertion import Verification

# If the feed is a master feed
ver = Verification()
ver.check_incoming(master_id, 'MASTER') # returns true

#If the feed is a child feed
ver.check_incoming(feed_id, 'ExampleApp1')
```
##### Verification:
The Idea for `check_incoming()` and `check_outgoing()` is to verify if we wan't to import or export a given feed to the database. It's recommended to run the test before importing a feed into the database, depending on the result a feed is accepted or not. Else a feed won't be validated and can be corrupted.

## Testing:
The module has been extensively tested by us and there are unit tests for most if not all functionalities. For use cases please have a look at the unit tests as those represent on how the code is intended to be used.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Changelog

* V1.0: Initial functionality implemented and proper readMe written.
* V2.0: The packages of group 7 and group 14 are now merged into one package.