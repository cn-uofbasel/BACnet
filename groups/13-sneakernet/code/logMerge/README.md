# LogMerge

This is our project that provides an API to BACnet transport layer groups for importing 
and exporting events from the local BACnet database.

## Content

* [Requirements and installation](#requirements-and-installation)
* [Supported signing and hashing algorithms](#supported-signing-and-hashing-algorithms)
* [Quick start guide](#quick-start-guide)
* [Full API specification](#full-api-specification)
  - [API that we provide](#api-that-we-provide)
  - [API that we use](#api-that-we-need-from-others)

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
In order to use LogMerge, you need to import this whole folder to your project. Just add this folder to your source tree 
and follow the installation guide [above](#requirements-and-installation). The whole API is inside the file 
`LogMerge.py`.

When you as transport group come to us, you probably want to import the `.pcap` files that you have ready for us into 
the database. To do so, just do the following:
```python
import LogMerge
lm = LogMerge.LogMerge()
lm.import_logs(path_to_folder_with_pcap_files)
```
, where `path_to_folder_with_pcap_files` is the path to the folder wherefrom all `.pcap` files will be imported. (All 
`.pcap` files from subfolders will be imported too.)

Now, that you imported your files, you probably want to know which feeds are available for export in the local database. 
Therefore you can use the following code:
```python
status_dictionary = lm.get_database_status()
```
The status_dictionary will now contain all feed ids that you can get from the database and their highest available 
sequence numbers as values. I.e. the structure thereof is:
```python 
status_dictionary = {feed_id_1: max_seq_no, feed_id_2: max_seq_no, feed_id_3: max_seq_no, ...}
```
The feed ids will be of type `bytes` and the sequence numbers will be of type `int`.

Last but not least you might want to export events from the database in order to transport them to the next BACnet user. 
Therefore, please use the following API:
```python
lm.export_logs(path_to_pcap_folder, dict_feed_id_current_seq_no)
```
In this call, the first parameter specifies the path to the folder where our program will write the `.pcap` files to. 
The second parameter should be a dictionary with all the feed ids (as `bytes`) you want to export as keys. The value for 
each feed should be the highest sequence number that you do not need (or `-1` if you want all events). Only events with 
a higher number will be exported. Thus the dictionary should look somehow like this:
```python
dict_feed_id_current_seq_no = {feed_id_1: highest_already_exported_seq_no, feed_id_2: highest_already_exported_seq_no, ...}
```

If you want to limit the events that will be written into the `.pcap` files, you can set the optional parameter of the 
`export_logs` method. Please look in the [full api](#api-that-we-provide) for further information.

## Full API specification
### API that we provide
#### class LogMerge
The class LogMerge is the API of this tool.

```python
get_database_status()
```
* Returns: Type: `dict` (keys: `bytes`, values: `int`). A dictionary that contains all feed ids that you can export 
from this database together with the highest available sequence number as value.

```python
export_logs(path_to_pcap_folder, dict_feed_id_current_seq_no, maximum_events_per_feed_id=-1)
```
* Returns: Nothing, but `.pcap` files are created.
* Parameters:
  - `path_to_pcap_folder`: Type: `str`. The path to the folder where the `.pcap` files will be saved (if any). For each 
  feed a new file is created. If there are too many events for one `.pcap` file, multiple files are created.
  - `dict_feed_id_current_seq_no`: Type: `dict` (keys: `bytes`, values: `int`). A dictionary that contains all feed ids 
  that you want to export from this database together with the highest sequence number you already have as value. 
  Only events with higher sequence numbers will be exported. The sequence number should be `-1` if you want all events 
  of the specified feed. This must not be null! If you want just the master feeds, please pass an empty dictionary `{}` 
  instead.
  - opitonal `maximum_events_per_feed_id`: Type: `int`. The maximum number of events that will be exported per feed. This can be 
  used to reduce the payload of the transport medium. If this value is `-1`, then there is no limit of events.
* NOTE: `.pcap` files that are already in the folder will be **OVERWRITTEN** if the names match. Thus it is a good idea 
to export always to a new folder.

```python
import_logs(path_of_pcap_files_folder)
```
* Parameters:
  - `path_of_pcap_files_folder`: Type: `str`.
  The path to the folder that contains the `.pcap` files that should be imported. All subdirectories are also searched 
  for `.pcap` files. All events are read in from the files, verified and eventually imported into the database. (They 
  also checked by Group 14 first.)

### API that we need from others

We are using the API provided by Group 7 logStore and their adapter for Group 14 feedCtrl. The full specification of 
the API can be found [here](https://github.com/cn-uofbasel/BACnet/blob/master/groups/07-14-logCtrl/src/README.md).
