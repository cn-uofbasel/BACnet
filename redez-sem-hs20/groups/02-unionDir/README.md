<div style="text-align:center"><img src="https://user-images.githubusercontent.com/55445584/108355250-daad2b80-71ea-11eb-92fc-5a43e6669f79.png" /></div>

# UnionDir

## Going beyond namespaces

*UnionDir* is an application that applies a centralized approach to file systems, where each user has complete control over their data. It allows going beyond the limits of superficial file or folder names and allows users to cooperate directly by mounting file systems.

*UnionDir* was developed by Leonardo Salsi, Ken Rotaris, and Tunahan Erbay as part of the seminar "Re-decentralizing the Internet" during the Fall 2020 semester. 

## Functionality

The server maintains all file systems and takes care of hash key resolution. This method allows to differentiate files and folders not depending on their name, but on their content, origin and creation date. 

To create a file system on a server, the client is needed. Any control of the file system is done through it. 

_Attention_: Local hidden folders are created. If information in the JSON-files or the content of these folders is changed, there is a risk that the file system will be corrupted.

## Usage

### Entry points

| Server  | Client  |
|---|---|
|server.py|terminal.py|

1. Start the server. It creates a folder for maintaining data that is uploaded to the server.
2. Restart the server to put it into operation
3. Register with the IP of the server and a name that you can choose freely. The syntax is as follows:
`register <IP> <name>`
4. Now you are registered with a file system. You are free to create as many file systems on the server as you like.
5. If you lose track of the servers you are connected to and the file systems you have, use the ``serverlist``-command to display a list of all known connections.

_Note_: In order for UnionDir to function, make sure to create a virtual environment with the file provided in this repository.

## Operator list

| Command  | Alias  | Description  |
|---|---|---|
| cd  | chdir  | Change the current working directory.  |
| ls | list, l| List all files and folders of the current directory. |
| ls+ | list+, l+| List all files and folders of the current directory and display additional info on them. |
|mk|mkd, mkdir, makedir|Created an empty folder.|
| add |put| Add a file from outside to the file system, also works with directories.|
| rm | remove, delete, del | Remove a file and or folder from the file system.
| mount | mt, mnt |Mounts another file system to the the own file system. |
|mv|move|Moves a file/folder (and all subfolders and files if there are any) into the new location.|
|cp|copy|Copies a file/folder (and all subfolders and files if there are any) into the new location.|
|rn|rename|Renames a file/folder.|
|q|-q, quit|Quits the program.|
|--help|-help, -h, help, hlp, h|Get list of all commands. If speciffic operator is given as secon argument, it prints out only the help section for that operator.|
|clear|clc, c, clean|Clears the program terminal.|



## Known Issues
* As of now, it is not possible to mount file systems into each other.
* There is a minor chance that images do not get uploaded completely due to packet loss.
* If the server goes offline whilst users are online, they might experience trouble logging off.
* After a failed mounting attempt, when trying to mount an existing file system, the server acts as if it does not exist. Only on the second attempt it recognizes the file system and acts accordingly.

