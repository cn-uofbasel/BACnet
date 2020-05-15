# logMerge: 

THIS FILE IS MOSTLY OUT OF DATE. WE WILL UPDATE IT SOON.
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

##Needed interfaces from Group 7 logStore

####get_current_seq_no(feed_id): seq_no 
***We could drop this requirement, please contact us if you dont want to implement it***<br>
Parameter: feed id as bytes() python object (bytestring)<br>
Return value: sequence number as integer of the most recent event for the given feed id (the event with the highest sequence number from the database)<br>
This method should return -1 if there is no event for this feed id

####get_event(feed_id, seq_no): event
Parameters:<br> 
feed id as bytes() python object (bytestring)<br>
sequence number of the requested event<br>
Return value: The event for the specified parameters as cbor encoded bytes() object<br>
This method should return None if no such event exists

####get_current_event(feed_id): event
Parameter: feed id as bytes() python object (bytestring)<br>
Return value: the newest (highest sequence number) event from the database as cbor encoded bytes() python object<br>
This method should return None if no event for the feed_id exists

####add_event(feed_id, seq_no, event): void
Parameters:<br>
feed_id: feed id of the event that is saved as bytes()<br>
seq_no: sequence number of the event for the feed id as integer<br>
event: the cbor encoded event as bytes() 

####get_secret_hmac_key(feed_id): secret_key
***The key that is obtained in this method must be inserted by an application layer group into the database***<br>
Parameter: feed id as bytes() python object (bytestring)<br>
Returns hmac secret key if there is one for the given feed id (as bytes())<br>
This method should return None if no hmac secret key for this feed id exists

