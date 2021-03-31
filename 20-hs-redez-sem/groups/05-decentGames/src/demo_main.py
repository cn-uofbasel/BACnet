import os
from logSync import database_sync
import udp_connection


def check_dir(dir1):
    print(dir1)
    if not os.path.isdir(dir1):
        print("Directories do not exist")
        sys.exit()


#if __name__ == '__main__':
def main(self, argv):
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Tool for synchronisation')

    parser.add_argument('--sync', metavar='DIR', nargs=2)
    parser.add_argument('--dump', metavar='DIR')
    parser.add_argument('--server', metavar='server', nargs=1)
    parser.add_argument('--client', metavar='client', nargs=1)
    args = parser.parse_args()

    if args.server is not None:
        server = udp_connection.Server(args.server[0])
        # print(server.get_packet_to_send_as_bytes())

    if args.client is not None:
        client = udp_connection.Client(args.client[0])
        # print(client.get_packet_to_receive_as_bytes())

        # This is the crucial function for the other groups (Synchronisation). The client contains two important lists:
        # A list of files that are going to be extended and their corresponding extensions (groups will enter their
        # received packets instead of client.get_packet_to_receive_as_bytes())

        # sync.sync_database(client.get_list_of_needed_extensions(), client.get_packet_to_receive_as_bytes())
        database_sync.sync_database(client.get_list_of_needed_extensions(), client.get_packet_to_receive_as_bytes())
