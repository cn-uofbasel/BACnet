# Secure Team Chat

A BACnet implementation for secure team chat. Currently it supports creating users with a human reabable alias, following and unfollowing other users, creating a groupchat and inviting other users as well as sending messages to groupchats. 

## Usage

```
python user.py (alias) <command> [options]
```

`alias`:  a human readable username.

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

### user.py (alias) log [-r]

Show the log for the user with the alias `alias`.

#### Log Options: 

* `-r`: Show the raw log.

### user.py (alias) follow (other_alias)

Follow the user `other_alias`. This will make the current user sync the log file of the user with the alias `other_alias`.

### user.py (alias) unfollow (other_alias)

Unfollow the user `other_alias`. This will prevent the current user to sync the log file of the user with the alias `other_alias`.

### user.py (alias) chat (chat_alias)

Create a new group chat with the alias `chat_alias`. The current user is automatically a member and the owner of this group chat.

### user.py (alias) message (chat_alias)

Send a message to the group chat with the alias `chat_alias`. This is only possible if the user is a current member of the group.

The message can be entered interactively in the command, and can't be specified as an argument.

### user.py (alias) invite (chat_alias) (user_alias)

Invite the user `user_alias` to the chat `chat_alias`. This will issue a rekey and send this new key via "direct message" to the new member. This command can only be used if the current user is the owner of the group chat.