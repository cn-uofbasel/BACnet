import event as event
import pcap as pcap
from feed import FEED
from crypto import ED25519


class Sync:
    print("")


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
            pcap.dump(args.pcapfile1)

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
        if args.keyfile1 is None or args.keyfile2 is None:
            print("Keyfiles missing")
            sys.exit()

        seq1 = pcap.get_seq(args.pcapfile1)
        seq2 = pcap.get_seq(args.pcapfile2)

        if seq1 > seq2:
            fid, signer = load_keyfile(args.keyfile2)
            feed = FEED(args.pcapfile1, fid, signer)
            eventList = pcap.get_meta_and_cont_bits(args.pcapfile1, seq2)
            print(eventList)
            print('-------------------------------------')
            ev = event.EVENT()
            ev.from_wire(eventList[0])
            print(feed.is_valid_extension(ev))
          #  for i in eventList:
          #      feed.write(eval(eventList[i]))

        elif seq2 > seq1:
            fid, signer = load_keyfile(args.keyfile1)
            feed = FEED(args.pcapfile1, fid, signer)
            eventList = pcap.get_meta_and_cont_bits(args.pcapfile2, seq1)
            print(eventList)
            print('-------------------------------------')
            ev = event.EVENT()
            ev.from_wire(eventList[0])
            print(feed.is_valid_extension(ev))
         #   for i in eventList:
         #       print(i)
         #       feed.write(i)
        else:
            print("Already up-to-date")

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
