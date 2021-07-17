from ..src.core.node import Node
from ..src.replication.udp_channel import UDPChannel
from ..src.core.com_link import OperationModes
from ..src.core.interface.event import Content


def main():
    channel = UDPChannel("192.168.2.178")
    node = Node(OperationModes.MANUAL, channel)
    master = node.get_master()
    feed = master.create_feed("TestFeed")
    content = Content("Test/Test", {"Test": "Message"})
    feed.insert_event(content)
    node.get_storage().sync()


if __name__ == "__main__":
    main()
