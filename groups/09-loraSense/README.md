### Members

- Alexander Oxley
- Carlos Tejera

### Idea

Our task is to create an API in which it is possible to synchronize two databases. The entries/objects are compared to each other to add data that is missing in one of the databases. In addition we have to consider certain filters, because not every user needs the same logs (there is a kind of feed subscriptions). So our API will make sure that the databases are correctly "updated" when they are synchronized with others.

### Requirements

To achieve our goal, we need the filter functions of group 14 (feedCtrl) and of course the data storage functions of group 7 (logStore).

### API

We offer our API to groups such as 2, 5, 6 and 8 as they will need the synchronization.

The function we will provide will look similar to this:

```
    def syncDB(db1, db2, filter1, filter):
        return db1, db2
```

The exchange of data will obviously run in the background.

### LOG

- Update 29.3.20: Pascal has left the group
- Update 15.4.20: half-way point presentation ready and Idea, Requirements and API set