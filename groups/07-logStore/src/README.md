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
* [Contributing](#contributing)
* [License](#license)
* [Contributing](#contributing)
* [Changelog](#changelog)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install logStore.

```bash
cd {path to downloaded library}/logStore
pip install .
```

## Usage

Usage of logStore can be split up in the usage for the application layer groups and the network layer groups. Important for usage is that the groups use the [EventCreationTool](https://github.com/cn-uofbasel/BACnet/tree/master/groups/04-logMerge/eventCreationTool) provided by group 04.

#### Application layer:

Most application layer groups have requested specific interfaces for their applications which have been subsequently implemented by us. If your applications needs another interface please don't hesitate to contact us.

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

cf.send_msg(event)

cf.get_feed_ids()
cf.get_last_msg_from_chat_id(chat_id)
cf.get_all_msgs_from_chat_id(chat_id)
```

Application groups that don't want to have their own interface and instead want to implement their own search and filter methods can use the same interfaces as the Network layer groups described next.

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

Further methods are planned.

The functionality can be used as described following:

```python
from logStore.transconn.database_connector import DatabaseConnector as dc

chat_id = '21b1235u4'

dc.add_event(event)

dc.get_current_seq_no(feed_id)
dc.get_event(feed_id, seq_no)
dc.get_current_event(feed_id)
dc.get_all_feed_ids()
```

The further connection and integration to the network layer groups is currently being discussed and will soon be disclosed here.

##### Goal:
The ultimate goal would be to integrate our product into the application written by group 14 to place the database into the same folder as the feed control application.

Furthermore is planned to have the check functionality which verifies the feeds and control which feeds will be copied by group 4 or 12 to be placed within this application in the directory `logStore/verific/verify_insertion.py` and which then would be called every time either group 4 or 12 would want to include some data into the database.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Changelog

* V1.0: Initial functionality implemented and proper readMe written.
