from browser import help, help_functions
from net import filehandler
from util import color
import os

class Protocol:

    def __init__(self, unionpath):
        self.unionpath = unionpath
        self.client = self.unionpath.client
        self.filehandler = filehandler.Filehandler(self.unionpath, self.client)


    def send_connection_info(self):
        hash = self.unionpath.user_hash
        name = self.unionpath.user_name
        self.client.send("CON {} {}".format(hash, name))
        return self.client.get()

    def send_file_changed(self, hash, timestamp):
        self.client.send("UPD {} {}".format(hash, timestamp))
        return self.client.get()

    def send_mount_instruction(self, info):
        info = info.split()
        if info[1] == "upload":
            self.client.send("MNT-U {} {} {}".format(info[2], info[3], info[4]))
            answer = self.client.get()
            print(color.green("{} has been successfully upladed.".format(info[2])))
            if answer == "DONE":
                return
            elif answer == "GIVE":
                self.filehandler.send_all_files_of_dir(os.path.join(self.unionpath.filesystem_root_dir, info[2]))
                self.client.send("DONE")
        elif info[1] == "download":
            self.client.send("MNT-D {}".format(info[2]))
            answer = self.client.get()
            if answer == "NONE":
                print(color.yellow("There are no mounts named {} on the server.".format(info[2])))
                return
            elif answer == "ONE":
                self.client.send("OK")
                mount = self.client.get().split()[1]
                mountpath = os.path.join(self.unionpath.filesystem_root_dir, mount)
                os.mkdir(mountpath)
                self.unionpath.add_to_dictionary(mount, info[2], "directory", self.unionpath.filesystem_root_dir, "", timestamp=None, extension=None,mount=mount)
                self.client.send("GIVE")
                while (True):
                    message = self.client.get()
                    if message == "DONE":
                        break
                    elif message == "\EOF":
                        continue
                    self.filehandler.get_file(message + " {}".format(mountpath), dir=mount)
            elif answer == "MORE":
                self.client.send("OK")
                mounts = self.client.get().split(".")
                msg = "{} duplicates of {} have been found. Select one by entering the corresponding number:".format(len(mounts), info[2])
                str = ""
                cnt = 0
                for mount in mounts:
                    str += "\r\n[{}] {}: Identifier -> {}".format(cnt + 1, info[2], mount)
                    cnt += 1
                msg += str
                while True:
                    try:
                        choice = input(color.bold(color.purple("{} -> ".format(info[2]))))
                        choice = int(choice)
                        if choice >= 1 and choice <= len(mounts):
                            choice -= 1
                            break
                        else:
                            print(color.red("Please enter a number between {} and {}.".format(1, len(mounts))))
                    except:
                        print(color.red("Please enter a number between {} and {}.".format(1, len(mounts))))
                self.client.send("{}".format(choice))
                mount = self.client.get().split()[1]
                mountpath = os.path.join(self.unionpath.filesystem_root_dir, mount)
                os.mkdir(mountpath)
                self.unionpath.add_to_dictionary(mount, info[2], "directory", self.unionpath.filesystem_root_dir, "",timestamp=None, extension=None, mount=mount)
                self.client.send("GIVE")
                while (True):
                    message = self.client.get()
                    if message == "DONE":
                        break
                    elif message == "\EOF":
                        continue
                    self.filehandler.get_file(message + " {}".format(mountpath), dir=mount, mount=mount)
            self.unionpath.edit_mount_list(op="add_mount", mounthash= mount, mountname=info[2], IP=self.client.IP)
            self.unionpath.sort_files_in_dir(os.path.join(self.unionpath.filesystem_root_dir, mount), info[2])

    def handle(self, message):

        if not self.unionpath.connected:
            if message == "END":
                return message
            return

        # prevent KeyError when enter is pressed
        if len(message) == 0:
            return

        cmds = message.split()

        # [reg, register]
        if help.check_if_alias(cmds[0], 'reg'):
            return self.send_connection_info()

        # [con, conn, connect]
        elif help.check_if_alias(cmds[0], 'con'):
            return self.send_connection_info()

        # [open, op]
        elif help.check_if_alias(cmds[0], 'open'):
            return self.send_file_changed(cmds[1], cmds[2])

        # [mk, mkd, mkdir, makedir]
        elif help.check_if_alias(cmds[0], 'mk'):
            self.operator.mk(cmds)

        # [mk, write, put, set, mkd, mkdir, makedir, makefile]
        elif help.check_if_alias(cmds[0], 'add'):
            return self.send_file(cmds[1])

        # [rm, unlink, delete, del, remove]
        elif help.check_if_alias(cmds[0], 'rm'):
            self.operator.rm(cmds)

        # [mt, mount]
        elif help.check_if_alias(cmds[0], 'mt'): #TODO
            self.send_mount_instruction(message)

        # [mv, move]
        elif help.check_if_alias(cmds[0], 'mv'):
            self.operator.mv(cmds)

        # [cp, copy]
        elif help.check_if_alias(cmds[0], 'cp'):
            self.operator.cp(cmds)

        # [rn, rename]
        elif help.check_if_alias(cmds[0], 'rn'):
            self.operator.rn(cmds)

        # [q,-q,quit]
        elif help.check_if_alias(cmds[0], 'quit'):
            return self.operator.quit(cmds)

        # [unknown]
        else:
            self.operator.unknown(cmds)

