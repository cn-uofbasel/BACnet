import json
from net import controller
import os
from util import color, hash_, create
import math
import _thread
import re
import shutil
from datetime import datetime
from pathlib import Path

BUFFER_SIZE = 8 * 1024

class Client:
    def __init__(self, conn, addr, clients_path, config_path, filesystem_path, hash=None):
        self.conn = conn
        self.addr = addr
        self.IP = self.addr[0]
        self.client_list_path = clients_path
        self.filesystem_list_path = config_path
        self.hash = hash
        self.root_dir = None
        self.fs_content_file = None
        self.filesystem_path = filesystem_path
        _thread.start_new_thread(self.client_thread, ())

    def send(self, msg):
        print(color.yellow("Sending {}".format(msg)))
        self.conn.send(str.encode(msg))

    def send_bytes(self, msg):
        self.conn.send(msg)

    def send_file(self, src):
        try:
            with open(src, 'rb') as file:
                while True:
                    bytes = file.read()
                    if not bytes:
                        break
                    self.send_bytes(bytes)
                self.send_bytes(b'\EOF')
            return
        except:
            self.send_bytes(b'\INT')
            print(color.red("{} was not found.".format(src)))
            return

    def print_client_properties(self):
        print(color.purple(self.hash))
        print(color.purple(self.root_dir))
        print(Path.home())
        print(color.purple(self.fs_content_file))

    def client_thread(self):
        try:
            while True:
                message = self.conn.recv(2048)
                if message:
                    resp = self.handle_message(message)
                    if resp:
                        print(color.yellow(resp))
                        if resp == "DMNT":
                            continue
                        else:
                            self.conn.send(str.encode(resp))
                        if resp == 'DEN':
                            break
                        if resp == 'CQUIT':
                            self.conn.close()
                            break

        except:
            print(color.red("Connection to {}@{} lost".format(self.hash, self.IP)))
            self.conn.close()
            return

    def handle_message(self, msg):
        msg = msg.decode('utf-8')
        msg_spl = msg.split()
        cmd = msg_spl[0]
        if cmd == "SYNC":
            None
        elif cmd == "NEW":
            return self.register_user(msg_spl)
        elif cmd == "RET":
            return self.returning_user(msg_spl)
        elif cmd == "ADD":
            return self.get_file(msg_spl)
        elif cmd == "DIR":
            return self.make_folder(msg_spl)
        elif cmd == "SYNC":
            return self.synchronize(msg_spl)
        elif cmd == "REM":
            return self.remove(msg_spl)
        elif cmd == "DEL":
            return self.delete(msg_spl)
        elif cmd == "QUIT":
            return self.quit()
        elif cmd == "MNT_USER":
            return self.mount(msg_spl)
        elif cmd == "TEST":
            return self.test()
        else:
            return

    def synchronize(self):
        return "CSYNC"

    def register_user(self, msg_spl):
        hashk = hash_.get_hash_from_string(self.addr[0] + msg_spl[1])
        folder = os.path.join(hashk, msg_spl[2])
        file = os.path.join(folder, "{}.json".format(hashk))
        controller.add_user(self.client_list_path, self.filesystem_list_path, msg_spl[1], self.addr[0], hashk)
        res = controller.add_filesystem(self.filesystem_list_path, msg_spl[2], hashk, folder)
        create.folder(hashk)
        create.folder(folder)
        create.json_file(file)
        self.root_dir = os.path.join(self.filesystem_path, folder)
        self.fs_content_file = os.path.join(self.filesystem_path, file)
        self.hash = hashk
        return "{} {}".format(res, hashk)

    def returning_user(self, msg_spl):
        name = msg_spl[1]
        hash = msg_spl[2]
        fs_name = msg_spl[3]
        self.hash = hash
        try:
            clientlist = create.get_json_content(self.client_list_path)
            print(clientlist[hash])
            if name == clientlist[hash]['user']:
                serverlist = create.get_json_content(self.filesystem_list_path)
                fs_info = serverlist.get(hash).get(fs_name)
                if fs_info:
                    self.root_dir = fs_info['root']
                    self.fs_content_file = fs_info['content_json']
                    return "CRET"
        except:
            return "DEN"

    def test(self):
        None

    def get_file(self, msg_spl):
        flag = False
        src = msg_spl[1]
        dst = msg_spl[2]
        print(color.purple("ADD {} {}".format(src, dst)))
        dir = self._get_dir(dst)
        filename = self._get_filename(src)
        extension = os.path.splitext(filename)[1]
        path = os.path.join(self.hash, dir)
        filepath = create.file_path_in_filesystem(os.path.join(path, filename))
        print(color.green(filename))
        with open(filepath, "wb") as file:
            while True:
                bytes = self.conn.recv(BUFFER_SIZE)
                file.write(bytes)
                if bytes.strip()[-3:] == b'EOF':
                    break
                elif bytes.strip()[-3:] == b'INT':
                    flag = True
                    break
            file.close()
        if flag:
            os.remove(filepath)
            return "NCADD"
        timestamp = math.trunc(datetime.timestamp(datetime.now()))
        hashname = hash_.get_hash_from_string(filepath + str(timestamp))
        new_filepath = filepath.replace(filename, "{}{}".format(hashname, extension))
        timestamp = self.add_to_dict(hashname, filename, "file", extension=extension, timestamp=timestamp)
        os.rename(filepath, new_filepath)
        try:
            os.remove(filepath)
        except:
            None
        return "CADD {} {}".format(hashname, timestamp)

    def mount(self, msg_spl):
        try:
            user = msg_spl[1]
            user_hash = msg_spl[2]
            fs_name = msg_spl[3]
            clientlist = create.get_json_content(self.client_list_path)
            user_matches = ""
            for reg_hash in clientlist:
                if reg_hash != user_hash and clientlist.get(reg_hash)['user'] == user:
                    user_matches += "[\"{}\",\"{}\",\"{}\"],".format(reg_hash, clientlist.get(reg_hash)['user'], clientlist.get(reg_hash)['ip'])
            user_matches = "["+user_matches + "]"
            user_matches = user_matches.replace("],]","]]")
            self.send(user_matches)
            user = self.conn.recv(2014)
            user = user.decode("utf-8")
            serverlist = create.get_json_content(self.filesystem_list_path)
            fs_of_user = serverlist.get(user)
            json_loc = ""
            fs_root = ""
            if fs_of_user:
                fs = fs_of_user.get(fs_name)
                if fs:
                    json_loc = fs['content_json']
                    fs_root = fs['root']
                    fs = json_loc.split(os.sep)[-1].replace(".json","")
                    fs = "{}".format(fs)
                else:
                    fs = "None"
            else:
                fs = "None"
            timestamp = math.trunc(datetime.timestamp(datetime.now()))
            info = "DIR {} {}".format(fs, timestamp)
            self.send(info)
            notification = self.conn.recv(2014)
            notification = notification.decode("utf-8")
            if notification != "DIR_DONE":
                self.send("DMNT")
                return "DMNT"
            dirs, files = self._get_dirs_and_files(fs_root, json_loc)
            if not dirs:
                self.send("DMNT")
                return "DMNT"
            file_hashes = [re.sub('[.][^.]+$','',x.split(os.sep)[-1]) for x in files]
            if not dirs:
                self.send("DMNT")
                return "DMNT"
            content_info = create.get_json_content(json_loc)
            for dir in dirs:
                dir_hash = dir.split(os.sep)[-1]
                obj = content_info.get(dir_hash)
                name = obj['name']
                time = obj['time']
                type = obj['type']
                info = "DIR {} {} {} {} {} ".format(dir.replace(fs_root,""), dir_hash, name, time, type)
                self.send(info)
                notification = self.conn.recv(2014)
            print("SEND DIR_DONE")
            self.send("DIR_DONE")
            notification = self.conn.recv(2014)
            notification = notification.decode("utf-8")
            if not notification == "DIRS_DONE":
                self.send("DMNT")
                return "DMNT"
            for i in range(len(files)):
                obj = content_info.get(file_hashes[i])
                name = obj['name']
                time = obj['time']
                type = obj['type']
                extension = obj['extension']
                if extension == "":
                    extension = "None"
                info = "FILE {} {} {} {} {} {}".format(files[i].replace(fs_root, "")[1:], file_hashes[i], name, time, type, extension)
                print(color.purple(info))
                self.send(info)
                notification = self.conn.recv(5)
                notification = notification.decode("utf-8")
                if not notification == "CFILE":
                    self.send("DMNT")
                    return "DMNT"
                else:
                    self.send_file(files[i])
                    notification = self.conn.recv(6)
                    notification = notification.decode("utf-8")
                    if not notification == "CCFILE":
                        self.send("DMNT")
                        return "DMNT"
            self.send("CMNT")
            return "CMNT"
        except:
            self.send("DMNT")
            return "DMNT"

    def make_folder(self, msg_spl):
        curr = msg_spl[1]
        dir = msg_spl[2]
        if curr.__eq__("root"):
            loc = self.root_dir
        else:
            loc = self.root_dir + os.sep + curr
        if os.sep in dir:
            dirs = dir.split(os.sep)
            for i in range(len(dirs) - 1):
                loc += os.sep + dirs[i]
            dir = dirs[-1]
        timestamp = math.trunc(datetime.timestamp(datetime.now()))
        hashname = hash_.get_hash_from_string(str(timestamp) + dir)
        loc = os.path.join(loc, hashname)
        os.mkdir(loc)
        self.add_to_dict(hashname, dir, "directory", timestamp=timestamp)
        return "CDIR {} {}".format(hashname, timestamp)

    def remove(self, msg_spl):
        curr = msg_spl[1]
        hash = msg_spl[2]
        extension = msg_spl[3]
        if extension == "None":
            extension = ""
        print(color.purple(curr))
        print(color.purple(hash))
        if curr.__eq__("root"):
            loc = self.root_dir
        else:
            loc = self.root_dir + curr
        loc = os.path.join(loc, hash)
        if "." in extension:
            loc += extension
        if os.path.isfile(loc):
            print(loc)
            os.remove(loc)
            self.edit_content_file(hash, 'del')
            return "CREM"
        elif os.path.isdir(loc):
            shutil.rmtree(loc)
            return "CREM"
        else:
            print("NOT A FILE {}".format(loc))
            return "DREM"

    def quit(self):
        return "CQUIT"

    def delete(self, msg_spl):
        hash = msg_spl[1]
        self.edit_content_file(hash, 'del')
        return "CDEL"

    def _get_dirs_and_files(self, src, json_file):
        try:
            dirs = []
            files = []
            for dirname, dirnames, filenames in os.walk(src):
                # print path to all subdirectories first.
                for subdirname in dirnames:
                    dirs.append(os.path.join(dirname, subdirname))

                # print path to all filenames.
                for filename in filenames:
                    files.append(os.path.join(dirname, filename))
            files.remove(json_file)
            return dirs, files
        except:
            return None, None


    def add_to_dict(self, hash, name, type, extension="", timestamp=None):
        content_json = open(os.path.join(str(Path.home), self.fs_content_file), "r")
        content = json.load(content_json)
        content_json.close()
        if not timestamp:
            timestamp = math.trunc(datetime.timestamp(datetime.now()))
        info = {"name": name, "time": timestamp, "type": type, "extension":extension}
        item = {hash:info}
        content.update(item)
        content_json = open(self.fs_content_file, "w")
        json.dump(content, content_json, indent=4)
        content_json.close()
        return timestamp

    def _get_dir(self, dst):
        ret = re.sub("[a-zA-z0-9/]*/.filesystem/", "", dst)
        return ret

    def _get_filename(self, src):
        src_spl = src.split(os.sep)
        return src_spl[-1]

    def edit_content_file(self, hash, op, name=None):
        with open(self.fs_content_file, 'r') as data_file:
            data = json.load(data_file)

        for element in data:
            if op == 'del' and hash in element:
                del data[hash]
                break
            elif op == 'ren' and hash in element:
                None

        with open(self.fs_content_file, 'w') as data_file:
            json.dump(data, data_file)