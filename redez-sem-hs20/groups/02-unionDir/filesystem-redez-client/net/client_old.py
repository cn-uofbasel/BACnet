import os
import getpass
import socket
import math
import json
import shutil
from browser import create, help_functions, inputhandler_old, help
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


    def make_dir(self, path, name):
        path = os.path.join(path, name)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def delete_dir(self, path):
        shutil.rmtree(path)






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


