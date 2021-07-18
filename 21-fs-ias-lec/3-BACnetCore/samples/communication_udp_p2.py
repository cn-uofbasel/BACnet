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
    print("Starting Channel Threads!")
    channel.start()
    time.sleep(10)
    channel.stop()
    #node = Node(OperationModes.MANUAL, channel)
    #master = node.get_master()
    #feed = master.create_feed("feed_1")
    #feed.insert_event(Content("test_identifier", 123))
    #print("Now try to sync() -> Just the masters should be exchanged.")
    #for i in range(1, 3):
    #    node.synchronize()  # synchronize makes the node send a request to get data and to process all received inputs
    #    time.sleep(5)  # wait for other Node to react and send data
    #print("Finished synchronizing...")


if __name__ == "__main__":
    run(str(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
