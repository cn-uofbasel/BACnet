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
