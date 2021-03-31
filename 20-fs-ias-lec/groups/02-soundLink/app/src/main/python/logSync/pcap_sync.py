import os

import event as event
import pcap as pcap
from feed import FEED
from crypto import ED25519
import cbor


class FileInfo:

    def __init__(self, file):
        self.file = file
        try:
            self.fid, self.seq = pcap.get_fid_and_seq(file)
        except:
            self.fid = None
            self.seq = -1


class Sync:

    def __init__(self, file1, file2=None):

        if file2 is None:
            self.__old_file = FileInfo(file1)
            return

        file1 = FileInfo(file1)
        file2 = FileInfo(file2)

        self.up_to_date = False

        # Compare sequence numbers. The file with the higher sequence number should be the up-to-date file.
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

    """ 
    The files (new and old) are already given, when an instance of the class Sync was created.
    The method opens the older file by converting it to its corresponding form of a feed log.
    The necessary log extension (the new part of the new file) gets filtered and if it is valid, it gets appended to the
    old file instead of just overwrite it. 
    """

    def sync_files(self, new_files=False, key=None, event_list=None):
        if new_files and key is not None:
            self.__old_file.fid = key

        feed = FEED(self.__old_file.file, self.__old_file.fid, ED25519(), new_files)
        if event_list is None:
            event_list = pcap.get_meta_and_cont_bits(self.__new_file.file, self.__next_seq)

        ev = event.EVENT()
        ev.from_wire(event_list[0])
        if feed.is_valid_extension(ev):
            for i in event_list:
                # TODO: Find a solution to not use a protected method
                feed._append(i)


"""
Send a list of the files we want to actualize and with our actual seq num

This functions compares every file of the given list with the local files. If the files exist, we check the sequence
numbers of these files. If the sequence number of the given list is higher, we need to actualise the local file.
Therefore, we change the sequence number to know from which number on we need the extension.

If the file does not exist, it is a new file. We need the whole file and hence, we set the seq num to 0.

:param list_of_files: List of all files from the server
:type list_of_files: list
:return: Return a list of files from which we need the log extensions
:rtype: list
"""


def compare_files(list_of_files):
    # list_of_files is from the server

    list_for_client = []
    for i, elem in enumerate(list_of_files):
        # TODO: Change directory to database
        file = 'udpDir/' + elem[0]
        if os.path.isfile(file):
            seq_num = pcap.get_seq(file)

            if seq_num < elem[2]:
                elem[2] = seq_num
                list_for_client.append(elem)
        else:
            elem[2] = 0
            list_for_client.append(elem)
    return list_for_client


def create_list_of_files(dir1):
    dir_list = os.listdir(dir1)

    l = []
    for n, elem in enumerate(dir_list):
        file = dir1 + elem
        fid1, seq = pcap.get_fid_and_seq(file)
        l.append([elem, fid1, seq])
    return l


def sync_extensions(compared_files, extensions_files):
    extensions_files = cbor.loads(extensions_files)
    if len(compared_files) != len(extensions_files):
        print("Something went wrong..")
        return

    for i, val in enumerate(compared_files):
        event = extensions_files[i]
        synchro = Sync('udpDir/' + val[0])

        # If the file has to be created, the key is needed
        if val[2] == 0:
            synchro.sync_files(key=val[1], new_files=True, event_list=event)  # 12
        else:
            synchro.sync_files(event_list=event)  # 12
        print("Synchronising " + val[0] + "...")

    print("Finished synchronising!")


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
