import event as event
import pcap as pcap
from feed import FEED
from crypto import ED25519


class FileInfo:

    def __init__(self, file):
        self.file = file
        self.fid, self.seq = pcap.get_fid_and_seq(file)


class Sync:

    def __init__(self, file1, file2):
        file1 = FileInfo(file1)
        file2 = FileInfo(file2)

        self.up_to_date = False

        # Compare sequence numbers. The file with the higher sequence number should be the up-to-date file. Therefore,
        # we filter the new (or missing) information to append it to the older file after the verifications.
        if file1.seq > file2.seq:
            self.__old_file = file2
            self.__new_file = file1
            self.__next_seq = file2.seq

        elif file1.seq < file2.seq:
            self.__old_file = file1
            self.__new_file = file2
            self.__next_seq = file1.seq
        else:
            print(file1.file + " is up-to-date")
            self.up_to_date = True

    def sync_files(self):
        feed = FEED(self.__old_file.file, self.__old_file.fid, ED25519())
        eventList = pcap.get_meta_and_cont_bits(self.__new_file.file, self.__next_seq)
        ev = event.EVENT()
        ev.from_wire(eventList[0])
        if feed.is_valid_extension(ev):
            for i in eventList:
                feed._append(i)


if __name__ == '__main__':
    import argparse
    import sys
    import crypto

    def load_keyfile(fn):
        with open(fn, 'r') as f:
            key = eval(f.read())
        if key['type'] == 'ed25519':
            fid = bytes.fromhex(key['public'])
            signer = ED25519(bytes.fromhex(key['private']))
        elif key['type'] == 'hmac_sha256':
            fid = bytes.fromhex(key['feed_id'])
            signer = crypto.HMAC256(bytes.fromhex(key['private']))
        return fid, signer

    parser = argparse.ArgumentParser(description='BACnet feed tool')

    parser.add_argument('--keyfile1')
    parser.add_argument('pcapfile1', metavar='PCAPFILE1', default=None)

    parser.add_argument('--keyfile2')
    parser.add_argument('pcapfile2', metavar='PCAPFILE2', default=None)

    parser.add_argument('CMD', choices=['sync', 'dump', 'get', 'seq', 'check', 'all'])

    args = parser.parse_args()

    # Dump two pcap files
    if args.CMD == 'dump':
        if args.pcapfile1 is not None:
            pcap.dump(args.pcapfile1)
        print('-----------------------------')
        print('-----------------------------')
        if args.pcapfile2 is not None:
            pcap.dump(args.pcapfile2)

    elif args.CMD == 'get':
        if args.pcapfile1 is not None:
            pcap.get_only_context(args.pcapfile1)
        print('-----------------------------')
        print('-----------------------------')
        if args.pcapfile2 is not None:
            pcap.get_only_context(args.pcapfile2)

    elif args.CMD == 'seq':
        if args.pcapfile1 is not None:
            pcap.get_seq(args.pcapfile1)
        print('-----------------------------')
        print('-----------------------------')
        if args.pcapfile1 is not None:
            pcap.get_seq(args.pcapfile2)

    elif args.CMD == 'all':
        if args.pcapfile1 is not None:
            pcap.get_all_info(args.pcapfile1)
        print('-----------------------------')
        print('-----------------------------')
        if args.pcapfile2 is not None:
            pcap.get_all_info(args.pcapfile2)

    elif args.CMD == 'sync':
        print("Synchronisation...")
        Sync(args.pcapfile1, args.pcapfile2).sync_files()

    elif args.CMD == 'check':
        if args.keyfile1 is not None:
            fid, signer = load_keyfile(args.keyfile1)
        else:
            fid, signer = None, None

        f = FEED(args.pcapfile1, fid=fid, signer=signer)
        if f.pcap is None:
            sys.exit()
        f.seq = 0
        f.hprev = None
        print(f"Checking feed {f.fid.hex()}")
        for e in f:
            print(e.content())
            if not f.is_valid_extension(e):
                print(f"-> event {f.seq + 1}: chaining or signature problem")
            else:
                print(f"-> event {e.seq}: ok, content={e.content()}")
            f.seq += 1
            f.hprev = event.get_hash(e.metabits)
