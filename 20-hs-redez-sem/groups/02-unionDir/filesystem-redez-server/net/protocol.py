from net import filehandler
from util import color
import os

class Protocol:

    def __init__(self, client, unionpath):
        self.client = client
        self.unionpath = unionpath
        self.filehandler = filehandler.Filehandler(self.unionpath, self.client)

    def get_mount_from_client(self, dirhash, name, empty):
        contents = []
        dirpath = os.path.join(self.unionpath.filesystem_root_dir, dirhash)
        os.mkdir(dirpath)
        if empty == "True":
            self.client.send("DONE")
        else:
            self.client.send("GIVE")
            while (True):
                message = self.client.get()
                print(color.cyan(message))
                if message == "DONE":
                    break
                contents.append(message.split()[1])
                self.filehandler.get_file(message, dir=dirhash)
        mount = {dirhash:{"name":name, "owner":self.client.hash, "content":contents}}
        self.unionpath.edit_mountlist(op="add", mount=mount)

    def send_mount_to_client(self, name):
        mounts = self.unionpath.get_mounts_by_name(name)
        if len(mounts) == 0:
            self.client.send("NONE")
        elif len(mounts) == 1:
            self.client.send("ONE")
            ok = self.client.get()
            if ok == "OK":
                self.client.send("MOUNT {}".format(mounts[0]))
            give = self.client.get()
            if give == "GIVE":
                self.filehandler.send_all_files_of_dir(os.path.join(self.unionpath.filesystem_root_dir, mounts[0]))
                self.client.send("DONE")
        else:
            str = ""
            for mount in mounts:
                str += mount+"."
            self.client.send("MORE")
            answer = self.client.get()
            if answer == "OK":
                self.client.send(str[:-1])
                choice = self.client.get()
                self.client.send("MOUNT {}".format(mounts[int(choice)]))
                give = self.client.get()
                if give == "GIVE":
                    self.filehandler.send_all_files_of_dir(os.path.join(self.unionpath.filesystem_root_dir, mounts[0]))
                    self.client.send("DONE")

    def handle(self, message):
        cmd = message.split()
        if cmd[0] == "CON":
            self.unionpath.edit_clientlist("add", hash=cmd[1], name=cmd[2])
            self.client.hash = cmd[1]
            self.client.username = cmd[2]
            print("{} ({}) has connected to the server".format(self.client.username, self.client.hash))
            return "CON"
        elif cmd[0] == "UPD":
            self.unionpath.edit_dictionary(op="timestamp", hash=cmd[1], timestamp=cmd[2])
            print("Item {} has been updated -> {}".format(cmd[1], cmd[2]))
            return "UPD"
        elif cmd[0] == "FILE":
            self.filehandler.get_file(message)
        elif cmd[0] == "MNT-U":
            self.get_mount_from_client(cmd[1], cmd[2], cmd[3])
        elif cmd[0] == "MNT-D":
            self.send_mount_to_client(cmd[1])

