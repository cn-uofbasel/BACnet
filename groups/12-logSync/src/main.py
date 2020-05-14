import os
import sys
import pcap
from sync import Sync


def check_dir(dir1):
    if not os.path.isdir(dir1[0]) or not os.path.isdir(dir1[1]):
        print("Directories do not exist")
        sys.exit()


def create_list_of_files(dir1):
    dir_list = os.listdir(dir1)

    l = []
    for n, elem in enumerate(dir_list):
        file = dir1 + elem
        fid1, seq = pcap.get_fid_and_seq(file)
        l.append([elem, fid1, seq])
    return l


def sync_directories(dir_list):
    check_dir(args.sync)
    dir1 = dir_list[0]
    dir2 = dir_list[1]
    list1 = create_list_of_files(dir1)
    list2 = create_list_of_files(dir2)

    print("sync...")

    new_file_list1 = []
    for i in list1:
        found = False
        for j in list2:
            file1, key1 = i[:2]
            file2, key2 = j[:2]
            if key1 == key2:
                found = True
                synchro = Sync(dir1 + file1, dir2 + file2)
                # Only syncs if files are not up-to-date
                if not synchro.up_to_date:
                    synchro.sync_files()
                # Pops element of the second list if match was found to avoid unnecessary iterations
                list2.pop(list2.index(j))
                continue
        # If no match was found for the element of the first list, that means that the file is new and needs to be
        # added to the second list, respectively second directory. This is done below.
        if not found:
            new_file_list1.append(i)

    list1 = new_file_list1
    print(list1)
    print(list2)

    if list1:
        for i in list1:
            file, key = i[:2]
            synchro = Sync(dir1 + file, dir2 + file)
            synchro.sync_files(True, key)

    if list2:
        for i in list2:
            file, key = i[:2]
            synchro = Sync(dir1 + file, dir2 + file)
            synchro.sync_files(True, key)


def dump_directories_cont(dir_list):
    check_dir(dir_list)
    list1 = create_list_of_files(dir_list[0])
    list2 = create_list_of_files(dir_list[1])
    for i in list1:
        print(dir_list[0] + i[0] + ':')
        pcap.dump(dir_list[0] + i[0])
        print("-------------------------------")

    print('||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||')

    for i in list2:
        print(dir_list[1] + i[0] + ':')
        pcap.dump(dir_list[1] + i[0])
        print("-------------------------------")


if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Tool for synchronisation')

    parser.add_argument('--sync', metavar='DIR', nargs=2)
    parser.add_argument('--dump', metavar='DIR', nargs=2)
    args = parser.parse_args()

    if args.dump is not None:
        dump_directories_cont(args.dump)

    if args.sync is not None:
        sync_directories(args.sync)
