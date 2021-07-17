from ..src.core.node import Node
from ..src.replication.udp_channel import UDPChannel
from ..src.core.com_link import OperationModes
from ..src.core.interface.event import Content


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
