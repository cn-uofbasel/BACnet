from ..src.core.node import Node
from ..src.replication.udp_channel import UDPChannel
from ..src.core.com_link import OperationModes
from ..src.core.interface.event import Content

"""
This sample introduces some basic functionality of channel, node and feeds.
"""

# Channel creation
channel = UDPChannel("127.0.0.1", dest_port=6000, own_port=6000)

# Node creation
node = Node(operation_mode=OperationModes.MANUAL, channel=channel)
node_autosync = Node(operation_mode=OperationModes.AUTOSYNC, channel=channel)

# Manual sync
node.manual_synchronize()

# Master operations
master = node.get_master()
master.get_known_feeds(with_names=True)
master.get_last_event()
master.set_radius(3)

# Create feed and insert event
feed = master.create_feed("feed_1")
feed.insert_event(Content("test/123", 123))
feed.get_last_event()
feed.get_feed_meta()
feed.get_feed_id()

feed2 = master.get_feed_by_name("feed_2")

# Node shutdown (autosync)
node_autosync.shutdown()



