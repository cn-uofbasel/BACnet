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
* Accessible with the class Database
* Should not be accessible for any other group than this. There are specific interfaces for the interaction with the other groups.

## Interfaces

To supply the service of a well working database to either applications of group 3, 9, 10 or 11 or to the groups 4 and 12, we have to define well working as well as well serving interfaces.

### Group 3:

| Requirements                                           | Incoming Interfaces | Outgoing Interfaces                            | Current state                       | Responsible Person |
|--------------------------------------------------------|---------------------|------------------------------------------------|-------------------------------------|--------------------|
| Chat history for different chats with different people | None                | get_chats_for_feed(feed_id, last_message=None) | group will send us a file with methods they would like to have in our interface | Viktor             |

### Group 9:

| Requirements | Incoming Interfaces | Outgoing Interfaces | Current state                              | Responsible Person |
|--------------|---------------------|---------------------|--------------------------------------------|--------------------|
| Unclear      | None                | Unclear             | Mail sent to group for initial information | Moritz             |

### Group 10: 

| Requirements | Incoming Interfaces | Outgoing Interfaces | Current state                              | Responsible Person |
|--------------|---------------------|---------------------|--------------------------------------------|--------------------|
| Unclear      | None                | Unclear             | new information shows that this group doesn't need our data | Viktor             |

### Group 11:

| Requirements | Incoming Interfaces | Outgoing Interfaces | Current state                              | Responsible Person |
|--------------|---------------------|---------------------|--------------------------------------------|--------------------|
| Unclear      | None                | Unclear             | Mail sent to group for initial information | Moritz             |

### Group 14:

| Requirements                                                                                 | Incoming Interfaces                 | Outgoing Interfaces | Current state                              | Responsible Person |
|----------------------------------------------------------------------------------------------|-------------------------------------|---------------------|--------------------------------------------|--------------------|
| We need to obtain the currently subscribed feeds to update and clean our database regularly. | get_current_subscribed_feeds(feeds) | None                | Mail sent to group for initial information | Moritz             |

### Groups 4 and 12:

| Requirements                                                                                                                        | Incoming Interfaces | Outgoing Interfaces         | Current state                                                    | Responsible Person |
|-------------------------------------------------------------------------------------------------------------------------------------|---------------------|-----------------------------|------------------------------------------------------------------|--------------------|
| They need to obtain the last appended logs to merge/sync their data. Furthermore, they need a way to insert data into the database. | None                | get_last_log_for_feed(feed) | Initial communication established, further communication needed. | Moritz & Viktor    |
|                                                                                                                                     |                     | get_since_log_x(log)        |                                                                  |                    |
|                                                                                                                                     |                     | append_log(log)             |                                                                  |                    |

## Algorithms

The database will have to perform certain actions which will involve algorithms. For example [topological sort](https://en.wikipedia.org/wiki/Topological_sorting) or [similar](https://en.wikipedia.org/wiki/Category:Database_algorithms) algorithms will be used. 

Further information will be uploaded continuously.

## Coordination

To furthermore integrate the database correctly into the BACnet, a lot of coordination and communication will be needed. For detailed information look at [Interfaces](#interfaces).

## Protocols

Protocols from meeting can be found [here](https://github.com/cn-uofbasel/BACnet/tree/master/groups/07-logStore/Protocols).

## Glossary

Will be filled shortly.

## Links

* [On the timestamps in the tangle](https://assets.ctfassets.net/r1dr6vzfxhev/4iQXZ7bZGwSsE26SkqOQao/2ebf046578dabec5c1d3c48ed442c86f/On_timestamps_in_the_Tangle.pdf)
* [Towards More Reliable
Bitcoin Timestamps](https://arxiv.org/pdf/1803.09028.pdf)
* [Indexing Support for Decentralized SSB Apps - a Case Study](https://drive.google.com/file/d/1PyjW1zXxL00kidhn7R9k6mvYNqSiTugD/view?usp=sharing)
