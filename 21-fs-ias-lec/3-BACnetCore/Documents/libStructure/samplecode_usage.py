import BACnetCore
import BACnetTransport

"""
Create new Networknode
"""

# Create TransportLayer - Channel
myChannel = BACnetTransport.Paths("/my/usb/drive")

# Create Node from Scratch
myNode = BACnetCore.Node(BACNetCore.AUTOSYNC, channels = [myChannel])

# Create Node from existing Data
storage = BACnetCore.Storage.SQLiteConnector("/path/to/my/db")
myNode2 = BACnetCore.Node(BACNetCore.AUTOSYNC, db = storage, channels = list(myChannel))

"""
Change Node Parameters
"""
myNode.addChannel(myChannel2)

"""
Deal with the Masterfeed
"""
# get Masterfeed Reference
master = myNode.getMaster()

# create new feed
testfeed = master.createFeed(name = "test")

# list and subscribe feeds
print(master.getAvailbableFeeds())
externfeed = master.subscribe("owner/feedID")

# unsubscribe and block
master.unsubscribe("owner/feedID")
# control parameters
master.setRadius(3)
# manually sync
master.syncAll()
master.syncMaster()


"""
Send and Receive
"""

# create Event directly from text
testfeed.push(bytes("hi bob!"))
testfeed.sync()

# receive blocking
data = externfeed.receive(blocking=True, type="Data")
# search Content
event = externfeed.getContent(seq=12, type="Event")
# get last Event
data2 = externfeed.getLastEvent(type="Data")




