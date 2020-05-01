import sys


if __name__ == "main":
    if len(sys.argv) != 2:
        print("please specify a path to your .pcap file")
    else:
        path = sys.argv[1]

