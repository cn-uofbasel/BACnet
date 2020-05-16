from Databridge import *


def split_inp(inp):
    _inp = inp.split(" ")
    return _inp

running = True

followList = FLDataBridge("fl")
whitelist = WLDataBridge("wl")


commandList =  "\n-h List of all commands \n-p (fl/wl) prints list \n-add (fl/wl) [LogID] adds a new logID to the given list \n-rm (fl/wl) [LogID] Removes given LogId from the list \n-check (fl/wl) [LogID] Checks if given LogID is on the list \n-sst (fl/wl) [Bool] Sets the state of the given list \n-state (fl/wl) Returns the current state of the given list \nRadius is not yet implemented, because there are some missing featuers we need from an other group. This will be added after we have Acces to those features" 


if __name__ == "__main__":
    print("Welcome to the Feed Controll Demo! \n")
    while running:
        inp = input()
        sinp = split_inp(inp)
        cmd = sinp[0]
        args = sinp[1:]
        if  cmd == "-h":
            print(commandList)

        if cmd == "-p":
            if args[0] == "fl":
                print(followList.get_data())

            if args[0] == "wl":
                print(whitelist.get_data())

        if cmd == "-add":
            if args[0] == "fl":
                followList.append(args[1])

            if args[0] == "wl":
                whitelist.append(args[1])

        if cmd == "-rm":
            if args[0] == "fl":
                followList.remove(args[1])

            if args[0] == "wl":
                whitelist.remove(args[1])

        if cmd == "-check":
            if args[0] == "fl":
                print(followList.exists(args[1]))

            if args[0] == "wl":
                print(whitelist.exists(args[1]))

        if cmd == "-sst":
            if args[0] == "fl":
                if args[1] == "true":
                    followList.set_state(True)
                    
                if args[1] == "false":
                    followList.set_state(False)
            if args[0] == "wl":
                if args[1] == "true":
                    whitelist.set_state(True)
                    
                if args[1] == "false":
                    whitelist.set_state(False)

        if cmd == "-state":
            if args[0] == "fl":
                print(followList.get_state())

            if args[0] == "wl":
                print(whitelist.get_state())
