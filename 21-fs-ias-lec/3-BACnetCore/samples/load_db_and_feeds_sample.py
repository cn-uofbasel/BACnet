from ..src.core.node import Node
from ..src.replication.udp_channel import UDPChannel
from ..src.core.com_link import OperationModes

"""
This test should be run after the first sample "create_feed_sample", otherwise line 28 should raise an error.
It initializes the Node, tries to get the Masterfeed (which should be created when fresh database)
and queries events with different methods

If not installed via pip execution of this sample is working from outside the whole package:
>>> .../21-fs-ias-lec>python -m 3-BACnetCore.samples.load_db_and_feeds_sample
"""


def run():
    print("Create channel...")
    channel = UDPChannel("192.168.2.178")
    print("Load Node...")
    node = Node(OperationModes.MANUAL, channel)
    print("Get Master...")
    master = node.get_master()
    print("Try to load a feed...")
    feed = master.get_feed_by_name("TestFeed")
    print(f"Current seq nom is {feed.get_current_seq_num()}.")
    print("load Event with get_my_last_event()...")
    event = feed.get_last_event()
    print(f"The Content of the last Event is: {event.content.data}")
    print("Test get_content()...")
    event2 = feed.get_event(0)
    # test the string representation of events
    print(event2)


if __name__ == "__main__":
    run()
