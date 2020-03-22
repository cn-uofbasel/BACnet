# logMerge: 

This is a draft and not to be considered binding.
We will publish a reworked version later this week.
We are waiting for a link to a similar tool in order to clarify the working principle of our service.

### Content

* Idea
* Software requirements
* Working principle
* API provided to others
* API needed from others

### Idea

logMerge aims to provide a service that can be used to keep some files in sync.
The benefit of using our application is to save network bandwidth by reducing the number of packages that have to be sent.

### Software requirements

Our application needs access to the files on the computer it is installed on.
For needed API see chapter below.

### Working principle

The application that communicates over the web and wants to synchronize data, passes the files/folders to our API.
Our application then sends a request to the other client to accept the file. If the file is accepted our tool manages to update the file via the provided network api.
Our application either checks from scratch which elements have to be updated or saves this data inside a log on the clients computers.

### API provided to others

synchronize(destination_client, filepath)
synchronizeAll() /* updates all known synchronized file */

### API needed by us

Network layer: send() and receive() methods togheter with socket object in order to send data.

Application layer: method to check if files from other person are accepted. (ex: check(file)), anwser reject() or accept(filepath), where the file will be stored at filepath.
