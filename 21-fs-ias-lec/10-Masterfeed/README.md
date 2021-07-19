#  10-Masterfeed/Virtualfeed

  

Project of: Matthias Mueller, Patrick Steiner, Reto Krummenacher

  

##  Overview

  

This Project is the realization of letting one user work with multiple devices for one user-feed.

  

![Report](report/IasReport_Gruppe10_Multidevice.pdf)

  

##  Folders

  
 Conceptfiles
 : Directory with several Files of the first conceptual ideas and a short (Jupyter Notes) Demo of functional concept.

 report
: Report files

  tests
 : testfiles for the ui.py

 virtualFeed_env
: Folder of the main programs:
: ui.py and virtualFeed.py

virtualFeed_env/data
	: pcap files and keys of the Hostfeeds
	
virtualFeed_env/data/virtual
	: statsfiles, keys of the Virtualfeed and devices/Hostfeeds which holds the Virtualfeed

virtualFeed_env/lib
: libraries used from BACnet

## Execution

1. First run the [ui.py](virtualFeed_env/ui.py) to create the Hostfeed Key:
```python3
python3 ui.py
```
2. run the [virtualFeed.py](virtualFeed_env/ui.py):
```python3
python3 virtualFeed.py
```
to run the code, it is maybe needet to install additional libraries, do this with:
`
pip install [libraryname]
` or `pip3 install [libraryname]`
