# SneakerNet

new main command: ```sneakernet.py```

## (old) commands

```
users.py [-new_name]
  - if necessary, creates and initializes a new local user, prompts for a name
  - lists all known feedIDs and associated names
  - with the option '-new_name', one can change one's own name

import-from.py DIR
  - scans the given DIR directory
  - scans the 'logs' directory
  - imports those events from DIR which extend a log in 'logs',
    including creating a new log if that feed had not been seen so far.

export-to.py DIR
  - scans the 'logs' directory
  - scans the given DIR directory
  - exports those events from 'logs' which are not in DIR,
    into a 'export' file with a random name of the form x???????.pcap

dump-log.py [LOG_FILE]
  - pretty-prints for each event the sequence number and event body

```

## file conventions

```
MyFeedID.json    private and public key of local user
logs             directory for all (replicated) logs, events must be sorted
logs/1.pcap      log of local user
logs/2 ...       log of other users
```
