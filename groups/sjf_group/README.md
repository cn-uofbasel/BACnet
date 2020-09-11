# Schweizer Jugend Forscht
## Members
- Carlo Crespi
- Dominik Müller

##Project
The purpose of our project was to implement 
LongFi to the user interface (UI) 
of the subjective_chat and to make it more user-friendly. 
##New implementation and usage

We added some features to the UI of the subjective_chat.
- Button update: allows to send database updates via LongFi connection
- Button request: allows to request for database updates via LongFi connection
- Statusbar: shows what is being executed during a connection between 2 devices
- Menubar: allows to open the feed_control panel from the subjective_chat panel and to refresh the chat history (replacement of the old update button)

### How to set up a connection
In the file `longFi.src.etherConnection.py`
change in class `myThread()` following lines 
```python
etherrequest = EtherRequester("<name of your L2 interface>")
EtherUpdater("<name of your L2 interface>")
```


