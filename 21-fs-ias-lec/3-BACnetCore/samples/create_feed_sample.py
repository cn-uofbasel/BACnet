from ..src.core.node import Node
from ..src.replication.udp_channel import UDPChannel
from ..src.core.com_link import OperationModes
from ..src.core.interface.event import Content

"""
This test is can be run with an already created Database or not (both cases should be fine)
It initializes the Node, tries to get the masterfeed(which should be created when fresh database), creates a new feed
and inserts an event.

If not installed via pip execution of this sample is working from outside the whole package:
>>> .../21-fs-ias-lec>python -m 3-BACnetCore.samples.create_feed_sample

Things to check:(using database-discovery)
- was the master-feed created/loaded successfully
- was the test-feed created successfully
"""


def run():
    print("Create channel...")
    channel = UDPChannel("192.168.2.178")
    print("Create Node...")
    node = Node(OperationModes.MANUAL, channel)
    print("Get Master...")
    master = node.get_master()
    print("Try to create a new feed...")
    feed = master.create_feed("TestFeed")
    content = Content("Test/Test", {"Test": "Message"})
    print("Insert Event...")
    feed.insert_event(content)


if __name__ == "__main__":
    run()
