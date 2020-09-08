from logSync import database_sync
import udp_connection

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Tool for synchronisation')

    parser.add_argument('--server', metavar='server', nargs=1)
    parser.add_argument('--client', metavar='client', nargs=1)
    args = parser.parse_args()

    if args.server is not None:
        server = udp_connection.Updater(args.server[0])

    if args.client is not None:
        client = udp_connection.Requester(args.client[0])

        # This is the crucial function for the other groups (Synchronisation). The client contains two important lists:
        # A list of files that are going to be extended and their corresponding extensions (groups will enter their
        # received packets instead of client.get_packet_to_receive_as_bytes())

        database_sync.sync_database(client.get_list_of_needed_extensions(), client.get_packet_to_receive_as_bytes())
