# I&S Security Gruppe 7 - logStore

## Content

*   [Database](#database)
*   [Interfaces](#interfaces)
*   [Algorithms](#algorithms)
*   [Coordination](#coordination)
*   [Protocols](#protocols)
*   [Glossary](#glossary)
*   [Links](#links)

## Database

* Based on [sqLite](https://www.sqlite.org/index.html)
* Accessible with the class `/src/logStore/transconn/database_connector.py` if one requires to only access the byte arrays. Otherwise application specific interfaces will be made available for the different applications.
* There is no direct access to the database due to security concerns and we recommend to only use the provided interfaces.

### Structure of Database:
* The database is currently structured into two distinct database files and one or four tables respectively.
* There is a database for the raw cbor events to be retrieved by feed id and sequence number. It is named `cborDatabase.sqlite` and can be found in the directory from which the database has been created.
* There is a database containing different tables for the different applications to be used to more easily store and retrieve application specific data. It is named `eventDatabase.sqlite`.
* Both databases have specific query functions to be found in `/src/logStore/database/sql_alchemy_connector.py` where the specific data can be retrieved depending on the needs of the applications.

## Interfaces

For the transport layer groups the interface can be found at `/src/logStore/transconn/database_connector.py`. It has methods to retrieve a byte array by the hash value of the previous event. A byte array can only be inserted if it is valid meaning it passes the verification process beforehand.
Groups 3, 9, 10 and 11 will receive independent and application specific interfaces to allow for a swift retrieval of data.

Detailed results concerning the current events can be found at `/src/logStore/README.md`. Also, it is highly advice to use the code provided in the directory `groups/07-14-logCtrl/src` as this directory includes the code from group 14 and will thus provide the groups with all the needed validation methods. We also strongly advice to read the read me at `groups/07-14-logCtrl/src/README.md` as it includes all the necessary information regarding the current status of our project.

## Algorithms

We have decided on using a simple index based database retrieval for most groups, however, we also have included an timestamp based ordering for the application layer groups. Furthermore we allow for more complex algorithms to be implemented if needed. 

The most complex code fragments can be found at `/src/logStore/database/sql_alchemy_connector.py` where we retrieve the different queries from the users. To make it the easiest for users to retrieve data without having to type out sqlite queries, suitable methods to retrieve all kinds of data from the different tables are present.

## Coordination

To furthermore integrate the database correctly into the BACnet, a lot of coordination and communication will be needed. For detailed information look at [Interfaces](#interfaces).

Furthermore, we have had many discussions with several groups concerning their work status and further coordination for the integration phase of the project.

## Protocols

Protocols from meetings can be found [here](https://github.com/cn-uofbasel/BACnet/tree/master/groups/07-logStore/Protocols).

Most importantly, we had many more protocols that we did not directly take a record of, however, many groups can attest that we were regularly in contact and that we worked closely with all of our stake holders from the beginning.

## Links

* [On the timestamps in the tangle](https://assets.ctfassets.net/r1dr6vzfxhev/4iQXZ7bZGwSsE26SkqOQao/2ebf046578dabec5c1d3c48ed442c86f/On_timestamps_in_the_Tangle.pdf)
* [Towards More Reliable Bitcoin Timestamps](https://arxiv.org/pdf/1803.09028.pdf)
* [Indexing Support for Decentralized SSB Apps - a Case Study](https://drive.google.com/file/d/1PyjW1zXxL00kidhn7R9k6mvYNqSiTugD/view?usp=sharing)
* [SqLite documentation](https://docs.python.org/3/library/sqlite3.html)
