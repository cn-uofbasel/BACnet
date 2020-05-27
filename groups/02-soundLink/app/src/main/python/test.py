from logStore.transconn.database_connector import  DatabaseConnector
import cbor
import event



dc = DatabaseConnector()

feed_ids = dc.get_all_feed_ids()
n = dc.get_current_seq_no(feed_ids[1])
print("seq num:", n, "(feed 1)")
tmp = 0
for i in range(0, n + 1):
    l = cbor.loads(dc.get_event(feed_ids[1], i))
    tmp = cbor.dumps(l)
    print(cbor.loads(l[0])) # content bits
    # print(l[1])
    print(cbor.loads(l[2])) # event
    print(event.get_hash(l[0]))
    print("-------------------")

