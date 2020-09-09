from logSync import database_sync as sync
from longFi.src import etherConnection

if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Tool for synchronisation')

    parser.add_argument('--hasPackets', metavar='hasPackets', nargs=1)
    parser.add_argument('--needsPackets', metavar='needsPackets', nargs=1)
    args = parser.parse_args()

    if args.hasPackets is not None:
        hasPackets = etherConnection.EtherUpdater(args.hasPackets[0])  # The argument is the network interface i.e "en0", "en1", ...
        # print(server.get_packet_to_send_as_bytes())

    if args.needsPackets is not None:
        needsPackets = etherConnection.EtherRequester(args.needsPackets[0])  # The argument is the network interface i.e "en0", "en1", ...
        # print(client.get_packet_to_receive_as_bytes())

        # This is the crucial function for the other groups (Synchronisation). The client contains two important lists:
        # A list of files that are going to be extended and their corresponding extensions (groups will enter their
        # received packets instead of client.get_packet_to_receive_as_bytes())
        sync.sync_extensions(needsPackets.get_list_of_needed_extensions(), needsPackets.get_packet_to_receive_as_bytes())

