from feedCtrl.uiFunctionsHandler import UiFunctionHandler
from feedCtrl.uiFunctionsHandler import generate_test_data
from logStore.verific.verify_insertion import Verification
from logStore.funcs.EventCreationTool import EventFactory
from logStore.appconn.feed_ctrl_connection import FeedCtrlConnection
import secrets
from nacl.signing import SigningKey
import sys

class bcolors:
    TRUSTED = '\033[32m'
    BLOCKED = '\033[91m'
    ENDC = '\033[0m'



def split_inp(inp):
    _inp = inp.split(" ")
    return _inp


def cli():
    running = True

    # CLI test
    ufh = UiFunctionHandler()

    commandList = "\n-p: print List \n-t i j: Trust. i equals master index, j equals child index \n-ut i j: Untrust. i equals master index, j equals child index \n-r (int): without argument prints current radius, with argument sets new radius. \n-r: reload from database \n-q: quit"
    trusted = set(ufh.get_trusted())
    blocked = set(ufh.get_blocked())
    hostID = ufh.get_host_master_id()
    masterIDs = ufh.get_master_ids()
    radius = ufh.get_radius()

    print("Welcome to the Feed Control Demo! \n")
    while running:


        inp = input()
        sinp = split_inp(inp)
        cmd = sinp[0]
        args = sinp[1:]

        if cmd == '-p':
            print("Host: " + ufh.get_username(hostID))
            if masterIDs is not None:
                i = 0
                for masterID in masterIDs:
                    i = i + 1
                    print('%d. ' % i + ufh.get_username(masterID))
                    feedIDs = ufh.get_all_master_ids_feed_ids(masterID)
                    j = 0
                    for feedID in feedIDs:
                        j = j + 1
                        appName = ufh.get_application(feedID)
                        if feedID in trusted:
                            print("  %d. " % j + bcolors.TRUSTED + appName + bcolors.ENDC)
                        elif feedID in blocked:
                            print("  %d. " % j + bcolors.BLOCKED + appName + bcolors.ENDC)
                        else:
                            print("  %d. " % j + appName)

        elif cmd == '-t':
            masterID = masterIDs[int(args[0])-1]
            feed_id = masterID
            if int(args[1]) > 0:
                feed_id = ufh.get_all_master_ids_feed_ids(masterID)[int(args[1])-1]
            if feed_id not in trusted:
                ufh.set_trusted(feed_id, True)
                trusted.add(feed_id)

        elif cmd =='-ut':
            masterID = masterIDs[int(args[0]) - 1]
            feed_id = masterID
            if int(args[1]) > 0:
                feed_id = ufh.get_all_master_ids_feed_ids(masterID)[int(args[1]) - 1]
            ufh.set_trusted(feed_id, False)
            if feed_id in trusted:
                trusted.discard(feed_id)
                blocked.add(feed_id)

        elif cmd == '-r':
            if not args:
                print('Radius: %d' % radius)
            else:
                radius = int(args[0])
                ufh.set_radius(radius)

        elif cmd == '-reload':
            trusted = set(ufh.get_trusted())
            blocked = set(ufh.get_blocked())
            masterIDs = ufh.get_master_ids()
            radius = ufh.get_radius()

        elif cmd == '-q':
            running = False

        else:
            print(commandList)


def generate_random_feed_id():
    private_key = secrets.token_bytes(32)
    signing_key = SigningKey(private_key)
    public_key_feed_id = signing_key.verify_key.encode()
    return public_key_feed_id


if __name__ == '__main__':
    ver = Verification()
    fcc = FeedCtrlConnection()
    ecf1 = EventFactory()
    new_event = ecf1.next_event('MASTER/MASTER', {})
    fcc.add_event(new_event)
    last_event = ecf1.next_event('MASTER/Radius', {'radius': 5})
    fcc.add_event(last_event)
    ecf2 = EventFactory()
    new_event = ecf2.next_event('MASTER/MASTER', {})
    fcc.add_event(new_event)
    last_event = ecf2.next_event('MASTER/Radius', {'radius': 5})
    fcc.add_event(last_event)
    ecf3 = EventFactory()
    new_event = ecf3.next_event('MASTER/MASTER', {})
    fcc.add_event(new_event)
    new_event = ecf3.next_event('MASTER/Radius', {'radius': 5})
    fcc.add_event(new_event)
    trusted_id1 = generate_random_feed_id()
    new_event = ecf3.next_event('MASTER/NewFeed', {'feed_id': trusted_id1, 'app_name': 'TestApp'})
    fcc.add_event(new_event)
    trusted_id2 = generate_random_feed_id()
    new_event = ecf2.next_event('MASTER/NewFeed', {'feed_id': trusted_id2, 'app_name': 'TestApp'})
    fcc.add_event(new_event)
    new_event = ecf1.next_event('MASTER/Trust', {'feed_id': trusted_id2})
    fcc.add_event(new_event)
    new_event = ecf2.next_event('MASTER/Trust', {'feed_id': trusted_id1})
    fcc.add_event(new_event)
    result = ver._check_in_radius('TestApp')
    # generate_test_data()
    #print("arg: " + sys.argv[1])
    #if sys.argv[1] == 'cli':
    #    cli()
