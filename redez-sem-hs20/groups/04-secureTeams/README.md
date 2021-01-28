# Secure Team Chat

A BACnet implementation for secure team chat.

## Usage

```
python user.py (alias) <command> [options]

alias: a human readable username.

```
<!-- 
command:
 * create:    creates a new user with the given alias
 * log:       show the user log
    options:  -r: show the raw log
 * info:      print user information (fid, follows, channels)
 * follow:    follow another user
    options:  <other_alias>: the alias of the user to follow
 * unfollow:  unfollow another user
    options:  <other_alias>: the alias of the user to unfollow
 * chat:      create a new groupchat
    options:  <chat_alias>: the name of the new chat
 * message:   send a message to the groupchat
    options:  <chat_alias>: the name of the groupchat
    notes:    The chat message can be entered to std_in
 * invite:    add another user to the groupchat
    options:  <chat_alias>: the name of the groupchat
              <other_alias>: the name of the user to invite

-->

### user.py (alias) create

Create a new user with the alias `alias`.

### user.py (alias) log

Show the log for the user with the alias `alias`.

#### Log Options: 

* `-r`: Show the raw log.

### user.py <alias> follow
### user.py <alias> unfollow
### user.py <alias> chat
### user.py <alias> message
### user.py <alias> invite