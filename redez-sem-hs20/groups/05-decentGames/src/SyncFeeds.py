import udp_connection
import argparse
from logSync import database_sync


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tool for synchronisation')

    parser.add_argument('--sync', metavar='DIR', nargs=2)
    parser.add_argument('--dump', metavar='DIR')
    parser.add_argument('--server', metavar='server', nargs=1)
    parser.add_argument('--client', metavar='client', nargs=1)
    args = parser.parse_args()

    if args.server is not None:
        udp_connection.Server(args.server[0])
    if args.client is not None:
        client = udp_connection.Client(args.client[0])
