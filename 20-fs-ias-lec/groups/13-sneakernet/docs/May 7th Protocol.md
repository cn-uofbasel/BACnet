# Protocol from May 7th 2020

### Present parties:
* Group 13 representatives: Patrik Bütler, **Luka Obser**
* Group 4 representative: Nikodem Kernbach

### Agenda:
* Discussion of integration of each other

### Discussion of integration:
* The interfaces provided by group 4 are the following two (a third is going to be added at a later stage)
    * an import function which takes the path to a directory containing pcap files that are to be merged into the local BACnet representation.
    * an export function that takes:
        * a path to an existing folder in which the pcap files will be dumped
        * a python dictionary with feed_ids as key and seq_nos as values
        * an Integer stating the maximum amount of events to be exported per feed
* Group 13s main objective will be to calculate and provide the python dictionary mentioned in the export function. The functional requirements in the scope statement will be updated accordingly.

#### Results:
* Group 4 will provide another interface which will provide a python dictionary for a specific user of the BACnet. This dictionary will contain the feed_ids as key and the newest events seq_no as value.

#### Next meeting:
Group 13 plans to meet multiple times during the weekend for coding sessions with the aim to finish integration of group 4s functionality. A protocol will only be written if considered necessary.
