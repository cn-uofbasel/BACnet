from ..src.core.node import Node
from ..src.replication.udp_channel import UDPChannel
from ..src.core.com_link import OperationModes
from ..src.core.interface.event import Content

import time
import sys

"""
This sample shows how to import and export feeds from/to the peer Node.
It also shows how the Communication between Nodes work.

If not installed via pip execution of this sample is working from outside the whole package:
>>> .../21-fs-ias-lec>python -m 3-BACnetCore.samples.communication_udp
"""


def run(dest_ip, own_port, dest_port):

    print("Create Channel, Node, a feed and insert sample event")
    channel = UDPChannel(dest_ip, dest_port=dest_port, own_port=own_port)
    node = Node(OperationModes.AUTOSYNC, channel)
    master = node.get_master()
    feed = master.create_feed("feed_1")
    feed.insert_event(Content("test/123", 123))
    print(master.get_known_feeds(with_names=True))
    try:
        while True:
            pass
    except KeyboardInterrupt:
        node.shutdown()


if __name__ == "__main__":
    run(str(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
