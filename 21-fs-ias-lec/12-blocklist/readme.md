# Blocklist Module
### by Jannick Heisch and Paul Tröger

## Introduction
This module is used to manage and implement Blocklists for BACnet projects. \
They allow you to filter or block content based on the Blocklist and Blocklistsettings.

## How to use

This module is divided into two parts: The Blocklist and the Blocksettings.

### Blocklist
Blocklists save blocked words and authors.
You can import and export a blocklist from a json file or a bacnet feed.



### Blocksettings
Blocklistsettings save how blocking should be implemented. 
The settings can be saved and loaded from a json file.

Blocksettings include:

Blocklevel
 
<ol>
<li>Noblock: Filtering with the help of the own blocklist is disabled.</li>
<li>Softblock: Words, which are part of the blocklist, are censored without deleting the
   whole message. If the author is part of the blocklist, the whole message will be deleted.</li>
<li>Hardblock: If words or authors are part of the blocklist, the whole message will be
   deleted.</li>
</ol>

Suggestion block:

Decide whether you want to consider the suggested blocking or not.

For more information check the report and the comments on each function.