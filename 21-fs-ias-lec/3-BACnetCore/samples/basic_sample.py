from ..src.Core.node import Node
from ..src.Replication.udp_channel import UDPChannel
from ..src.Core.com_link import OperationModes
from ..src.Core.Interface.event import Content


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
