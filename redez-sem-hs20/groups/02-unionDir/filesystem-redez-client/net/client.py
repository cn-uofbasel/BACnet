import os
import getpass
import socket
import math
import json
import shutil
from browser import create, help_functions, inputhandler, help
from net.protocol import handle_message
from utils import color, hash_
from datetime import datetime


class Client:

    def __init__(self):
        self.superroot = os.getcwd()
        os.chdir(self.superroot)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.IP = None
        self.PORT = 65184
        self.user = getpass.getuser()
        self.current_folder = os.getcwd()
        self.filesystem_path = create.filesystem()
        self.serverlist_file = create.serverlist_file(self.user, self.filesystem_path)
        self.serverlist = create.serverlist(self.serverlist_file)
        self.servername = None
        self.root_dir = None
        self.content_file = None
        self.current_fs_folder = None
        self.filesystem_hash = None
        self.NAME, self.TIME, self.TYPE, self.LOCATION, self.HASH, self.EXTENSION, self.FS_PATH = 0, 1, 2, 3, 4, 5, 6

    def print_properties(self):
        print(color.cyan(self.filesystem_path))
        print(color.cyan(self.servername))
        print(color.cyan(self.root_dir))
        print(color.cyan(self.content_file))
        print(color.cyan(self.current_fs_folder))


    def translate_path(self, tilde=True):
        path_short_form = help_functions.home_path()
        dirs = path_short_form.split(os.sep)
        path = ""
        for dir in dirs:
            info = self.translate_from_hash(dir)
            if info:
                path += info[0]+os.sep
            else:
                path += dir + os.sep
        if tilde:
            return "~" + path[:-1]
        else:
            return path[:-1]

    def hashpath_to_fspath(self, path):
        path_tmp = path.replace(self.root_dir, "")
        if os.sep in path_tmp:
            path = path.replace(self.root_dir+os.sep, "")
            dirs = path.split(os.sep)
            for dir in dirs:
                name = self.translate_from_hash(dir)[0]
                path = path.replace(dir, name)
            return path
        else:
            return ""

    def fspath_to_hashpath(self, name, fs_path):
        content_json = open(self.content_file, "r")
        content = json.load(content_json)
        content_json.close()
        matches = []
        paths = []
        hashes = []
        extensions = []
        for obj in content:
            info = self.translate_from_hash(obj)
            if info[self.NAME] == name and info[self.FS_PATH] == fs_path:
                matches.append(info)
                paths.append(info[self.LOCATION])
                hashes.append(info[self.HASH])
                extensions.append(info[self.EXTENSION])
        if len(matches) == 0:
            return None
        elif len(matches) == 1:
            return os.path.join(paths[0], hashes[0] + extensions[0])
        else:
            choice = self.handle_duplicates(matches, fs_path)
            return os.path.join(paths[choice], hashes[choice] + extensions[choice])

    def disconnect_dialog(self):
        while True:
            response = input(color.yellow("Disconnect from {}? [Y/N]: ".format(self.servername)))
            if help.check_if_alias(response, 'y'):
                return True
            elif help.check_if_alias(response, 'n'):
                return False

    def _connect(self, IP):
        try:
            self.server_socket.connect((IP, self.PORT))
            return True
        except:
            return False

    def get_connection(self):
        self.servername = input(color.yellow('● Enter File Server name: '))
        srvcmd = self.servername.split()
        if self.servername.lower() == "test":
            print(color.purple("Entered test environment"))
            return
        elif self.servername in self.serverlist:
            if self._connect(self.serverlist.get(self.servername)["ip"]):
                if self.serverlist.get(self.servername)["hash"]:
                    self.filesystem_hash = self.serverlist.get(self.servername)["hash"]
                    if self._verify_identification(self.filesystem_hash, self.servername):
                        print(color.green("Successfully connected to {}".format(self.servername)))
                        self.IP = self.serverlist.get(self.servername)["ip"]
                        self.root_dir = self.serverlist.get(self.servername)["path"]
                        self.content_file = create.content_file(self.root_dir, self.filesystem_hash)
                        return True
                    else:
                        print(color.red("Server was unable to verify your hash"))
                        self.server_socket.close()
                        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        return False
                else:
                    print(self.serverlist.get(self.servername))
            else:
                print(color.red("Unable to connect to {} ({}). Register again to the server.".format(self.servername,
                                                                                                     self.serverlist.get(
                                                                                                         self.servername)[
                                                                                                         "ip"])))
                self.server_socket.close()
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                return False

        elif help.check_if_alias(srvcmd[0], 'reg'):
            if len(srvcmd) != 3:
                print(color.red("Please enter new server with: register <IP> <name>"))
            else:
                if self._connect(srvcmd[1]):
                    print(color.green("Successfully connected to {}".format(srvcmd[1])))
                    self.servername = srvcmd[2]
                    self.root_dir = self.filesystem_path + os.sep + self.servername
                    self.filesystem_hash = self._register_to_server(self.servername)
                    create.save_server_info(self.serverlist_file, srvcmd[1], self.servername,
                                            self.filesystem_hash,
                                            self.filesystem_path)
                    self.content_file = create.content_file(self.root_dir, self.filesystem_hash)
                    self.IP = srvcmd[1]
                    return True
                else:
                    print(color.red("Unable to connect to {}".format(srvcmd[1])))
                    return False
        elif help.check_if_alias(srvcmd[0], 'srv'):
            for srv in self.serverlist:
                ip = self.serverlist.get(srv)["ip"]
                if not ip == "127.0.0.1":
                    print(color.cyan("{} -> {}").format(srv, ip))
            return False
        elif help.check_if_alias(srvcmd[0], 'quit') and len(srvcmd) == 1:
            return "quit"
        else:
            print(color.red("{} is not a valid server. Type serverlist for all available inputs.").format(
                self.servername))
            return False

    def send(self, msg):
        self.server_socket.send(str.encode(msg))

    def send_bytes(self, bytes):
        self.server_socket.send(bytes)

    def _register_to_server(self, name):
        self.server_socket.send(str.encode("NEW {} {}".format(self.user, name)))
        msg = self.server_socket.recv(2048)
        if msg:
            return handle_message(msg.decode("utf-8"))

    def _verify_identification(self, hash_val, fs_name):
        to_send = "RET {} {} {}".format(self.user, hash_val, fs_name)
        self.send(to_send)
        msg = self.server_socket.recv(2048)
        if (msg.decode("utf-8") == "CRET"):
            return True
        else:
            return False

    def _handle_message(msg):
        msg_spl = msg.split()
        cmd = msg_spl[0]
        arg = msg_spl[1]
        if cmd == "CNEW":
            return arg

    def add_to_dict(self, hash, name, type, location, extension="", fs_path = "", timestamp=None):
        content_json = open(self.content_file, "r")
        content = json.load(content_json)
        content_json.close()
        if not timestamp:
            timestamp = math.trunc(datetime.timestamp(datetime.now()))
        info = {"name": name, "time": timestamp, "type": type, "location":location, "extension":extension, "fs_path":fs_path}
        item = {hash:info}
        content.update(item)
        content_json = open(self.content_file, "w")
        json.dump(content, content_json, indent=4)
        content_json.close()

    def translate_from_hash(self, hash):
        try:
            hash = os.path.splitext(hash)[0]
            if hash == self.filesystem_hash:
                return None
            content_json = open(self.content_file, "r")
            content = json.load(content_json)
            content_json.close()
            name = content.get(hash)['name']
            time = content.get(hash)['time']
            type = content.get(hash)['type']
            location = content.get(hash)['location']
            extension = content.get(hash)['extension']
            fs_path = content.get(hash)['fs_path']
            content_json.close()
            return [name, time, type, location, hash, extension, fs_path]
        except:
            return None

    def make_dir(self, path, name):
        path = os.path.join(path, name)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def delete_dir(self, path):
        shutil.rmtree(path)

    def translate_to_hash(self, name, path, suppress=False):
        if name == "{}.json".format(self.filesystem_hash):
            return None
        content_json = open(self.content_file, "r")
        content = json.load(content_json)
        content_json.close()
        matches = []
        hashes = []
        for obj in content:
            info = self.translate_from_hash(obj)
            if info[0] == name and info[3] == path:
                matches.append(info)
                hashes.append(obj)
        if suppress:
            if len(matches) == 0:
                return None
            elif len(matches) == 1:
                return hashes[0]
            else:
                return hashes[-1]
        else:
            if len(matches) == 0:
                return None
            elif len(matches) == 1:
                return hashes[0]
            else:
                return hashes[self.handle_duplicates(matches, name)]


    def handle_duplicates(self, matches, name):
        msg = "{} duplicates of {} have been found. Select one by entering the corresponding number:".format(len(matches), name)
        str = ""
        cnt = 0
        for info in matches:
            str += "\r\n[{}] {}: Fingerprint -> {}".format(cnt+1, info[0], info[1])
            cnt += 1
        msg += str
        print(color.yellow(msg))
        while True:
            try:
                choice = input(color.bold(color.green('● ' + self.user + "@{}".format(self.IP))) + color.purple(":{} -> ".format(name)))
                choice = int(choice)
                if choice >= 1 and choice <= len(matches):
                    choice -= 1
                    return choice
                else:
                    print(color.red("Please enter a number between {} and {}.".format(1, len(matches))))
            except:
                print(color.red("Please enter a number between {} and {}.".format(1, len(matches))))
        return None


    def get_mounts(self):
        with open(self.serverlist_file, 'r') as data_file:
            server_info = json.load(data_file)
            data_file.close()
        return server_info.get(self.servername)['mounts']

    def update_serverlist(self, op, hash):
        with open(self.serverlist_file, 'r') as data_file:
            server_info = json.load(data_file)
            data_file.close()

        for element in server_info:
            if op == 'add-mount' and self.servername in element:
                mounts = server_info.get(self.servername)['mounts']
                mounts.append(hash)
                server_info.get(self.servername)['mounts'] = mounts
            elif op == 'rem-mount' and self.servername in element:
                mounts = server_info.get(self.servername)['mounts']
                mounts.remove(hash)
                server_info.get(self.servername)['mounts'] = mounts

        with open(self.serverlist_file, 'w') as data_file:
            json.dump(server_info, data_file, indent=4)
            data_file.close()

    def edit_content_file(self, hash, op, name=None, repl=None, hashdir=None):
        with open(self.content_file, 'r') as data_file:
            data = json.load(data_file)
            data_file.close()
        for element in data:
            if op == 'del' and hash in element:
                del data[hash]
                break
            elif op == 'ren-name' and hash in element:
                data[hash]['name'] = name
                break
            elif op == 'ren-fs_path' and hash in element:
                tmp_fs_path = str(data[hash]['fs_path'])
                if tmp_fs_path:
                    if os.sep in tmp_fs_path:
                        dirs = tmp_fs_path.split(os.sep)
                        for i in range(len(dirs)):
                            if dirs[i] == name:
                                dirs[i] = repl
                        tmp_fs_path = ""
                        for i in range(len(dirs) - 1):
                            tmp_fs_path += dirs[i] + os.sep
                        tmp_fs_path += dirs[len(dirs) - 1]
                        data[hash]['fs_path'] = tmp_fs_path
                    else:
                        data[hash]['fs_path'] = repl
                break
            elif op == 'ren-fs_path_full' and hash in element:
                tmp_fs_path = str(data[hash]['fs_path'])
                dirs = tmp_fs_path.split(os.sep)
                for dir in dirs:
                    if hashdir.get(dir):
                        tmp_fs_path = tmp_fs_path.replace(dir, hashdir.get(dir))
                data[hash]['fs_path'] = tmp_fs_path

        with open(self.content_file, 'w') as data_file:
            json.dump(data, data_file, indent=4)
            data_file.close()

    def sync(self):
        self.send("SYNC {}".format(self.user))
