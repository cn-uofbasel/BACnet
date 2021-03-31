from pathlib import Path
from utils import color
import os, json, math, hashlib, random, string, getpass
from datetime import datetime
from browser import help_functions
from net import client

class Unionpath:

    def __init__(self):
        self._linux_home_path = Path.home()
        self.user_name = getpass.getuser()
        self.uniondir_dir = self._make_dir_in(self._linux_home_path, ".uniondir")
        self.filesystem_root_dir = self._make_dir_in(self.uniondir_dir, ".root")
        self.configuration_dir = self._make_dir_in(self.uniondir_dir, ".config")
        self.dictionary_file = self._make_file_in(self.configuration_dir, "dictionary", "json")
        self.mountlist_file = self._make_file_in(self.configuration_dir, "mounts", "json")
        self.namespace_logger_file = self._make_file_in(self.configuration_dir, "operations", "log")
        self.current_folder = self.filesystem_root_dir
        self.current_mount = None
        self.create_mount_list()
        os.chdir(self.current_folder)
        self.NAME, self.TIME, self.TYPE, self.LOCATION, self.HASH, self.EXTENSION, self.FS_PATH = 0, 1, 2, 3, 4, 5, 6
        self.connected = False
        self.client = client.Client(self)
        self.user_hash = self.get_user_hash()

    def _make_dir_in(self, path, dir):
        path = os.path.join(path, dir)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def _make_file_in(self, path, file, extension=None):
        if extension:
            file += ".{}".format(extension)
        path = os.path.join(path, file)
        if not os.path.exists(path):
            file_item = open(path, "w+")
            if extension == "json":
                json.dump({}, file_item, indent=4)
            file_item.close()
        return path

    def get_server_info(self, info):
        with open(self.mountlist_file, 'r') as data_file:
            server_info = json.load(data_file)
            data_file.close()
        return []

    def add_to_dictionary(self, hash, name, type, location, fs_path, timestamp=None, extension=None, mount=None):
        content_json = open(self.dictionary_file, "r")
        content = json.load(content_json)
        content_json.close()
        if not extension:
            extension = ""
        if not mount:
            mount = ""
        if not timestamp:
            timestamp = self.generate_timestamp()
        info = {"name": name, "time": timestamp, "type": type, "location":location, "extension":extension, "fs_path": fs_path, "mount":mount}
        item = {hash:info}
        content.update(item)
        content_json = open(self.dictionary_file, "w")
        json.dump(content, content_json, indent=4)
        content_json.close()
        if mount == "":
            mount = "None"
        if extension == "":
            extension = "None"
        return timestamp, extension, mount

    def refresh_(self, hash, name, type, location, fs_path, extension=None, mount=None):
        content_json = open(self.dictionary_file, "r")
        content = json.load(content_json)
        content_json.close()
        if not extension:
            extension = ""
        if not mount:
            mount = ""
        info = {"name": name, "time": self.generate_timestamp(), "type": type, "location":location, "extension":extension, "fs_path": fs_path, "mount":mount}
        item = {hash:info}
        content.update(item)
        content_json = open(self.dictionary_file, "w")
        json.dump(content, content_json, indent=4)
        content_json.close()

    def create_mount_list(self):
        with open(self.mountlist_file, 'r') as data_file:
            data = json.load(data_file)
            data_file.close()
        if not data:
            userhash = self.create_hash(str(random.randint(10, 100000)) + self.user_name + str(random.randint(10, 100000)))
            info = {"name": self.user_name, "hash":userhash}
            item = {"user": info}
            mounts = {"mounts":{}}
            servers = {"servers":{}}
            data.update(item)
            data.update(mounts)
            data.update(servers)
            data_file = open(self.mountlist_file, "w")
            json.dump(data, data_file, indent=4)
            data_file.close()

    def edit_mount_list(self, op, property=None, mounthash=None, mountname=None, IP=None, servername = None):
        with open(self.mountlist_file, 'r') as data_file:
            data = json.load(data_file)
            data_file.close()

        if op == "add_mount":
            mounts = data["mounts"]
            mount = {mounthash:{"name": mountname, "IP":IP}}
            mounts.update(mount)
        elif op == "add_server":
            servers = data["servers"]
            server = {IP:servername}
            servers.update(server)
        elif op == "get":
            return data[property]
        elif op == "rem":
            pass

        with open(self.mountlist_file, 'w') as data_file:
            json.dump(data, data_file, indent=4)
            data_file.close()

    def edit_dictionary(self, hash, op, name=None, repl=None, hashdir=None, property=None):
        with open(self.dictionary_file, 'r') as data_file:
            data = json.load(data_file)
            data_file.close()
        for element in data:
            if op == 'del' and hash in element:
                del data[hash]
                break
            elif op == 'ren-name' and hash in element:
                data[hash]['name'] = name
                break
            elif op == 'edit' and hash in element:
                data[hash][property] = name
                break
            elif op == 'get' and hash in element:
                return data[hash][property]
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
            elif op == "timestamp" and hash in element:
                timestamp = self.generate_timestamp()
                data[hash]["time"] = timestamp
                return timestamp
            elif op == 'ren-fs_path_full' and hash in element:
                tmp_fs_path = str(data[hash]['fs_path'])
                dirs = tmp_fs_path.split(os.sep)
                for dir in dirs:
                    if hashdir.get(dir):
                        tmp_fs_path = tmp_fs_path.replace(dir, hashdir.get(dir))
                data[hash]['fs_path'] = tmp_fs_path

        with open(self.dictionary_file, 'w') as data_file:
            json.dump(data, data_file, indent=4)
            data_file.close()

    def create_hash(self, string):
            hash_object = hashlib.sha1((str(datetime.now()) + string + self._create_random_string(5)).encode())
            return hash_object.hexdigest()

    def get_user_hash(self):
        with open(self.mountlist_file, 'r') as data_file:
            data = json.load(data_file)
            data_file.close()
        return data["user"]["hash"]

    def _create_random_string(self, size):
        return ''.join(random.choice(string.ascii_letters) for i in range(size))

    def translate_path(self, tilde=True):
        path_short_form = help_functions.home_path()
        dirs = path_short_form.split(os.sep)
        path = ""
        for dir in dirs:
            info = self.translate_from_hash(dir)
            if info:
                path += info[0] + os.sep
            else:
                path += dir + os.sep
        if tilde:
            return "~" + path[:-1]
        else:
            return path[:-1]

    def hashpath_to_fspath(self, path):
        path_tmp = path.replace(self.filesystem_root_dir, "")
        if os.sep in path_tmp:
            path = path.replace(self.filesystem_root_dir + os.sep, "")
            dirs = path.split(os.sep)
            for dir in dirs:
                name = self.translate_from_hash(dir)[0]
                path = path.replace(dir, name)
            return path
        else:
            return ""

    def fspath_to_hashpath(self, name, fs_path):
        content_json = open(self.dictionary_file, "r")
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

    def translate_from_hash(self, hash):
        try:
            hash = os.path.splitext(hash)[0]
            content_json = open(self.dictionary_file, "r")
            content = json.load(content_json)
            content_json.close()
            name = content.get(hash)['name']
            time = content.get(hash)['time']
            type = content.get(hash)['type']
            location = content.get(hash)['location']
            extension = content.get(hash)['extension']
            fs_path = content.get(hash)['fs_path']
            mount = content.get(hash)['mount']
            content_json.close()
            if extension == "":
                extension = "None"
            if fs_path == "":
                fs_path = "None"
            if mount == "":
                mount = "None"
            return [name, time, type, location, hash, extension, fs_path, mount]
        except:
            return None

    def translate_to_hash(self, name, path, suppress=False):
        content_json = open(self.dictionary_file, "r")
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

    def get_full_path(self, name):
        object = self.translate_from_hash(self.translate_to_hash(name.split(".")[0], self.current_folder))
        if object:
            return object[4], "{}{}{}".format(object[3], os.sep, object[4])
        else:
            return None

    def handle_duplicates(self, matches, name):
        msg = "{} duplicates of {} have been found. Select one by entering the corresponding number:".format(len(matches), name)
        str = ""
        cnt = 0
        for info in matches:
            str += "\r\n[{}] {}: Fingerprint -> {}".format(cnt+1, info[0], info[4])
            cnt += 1
        msg += str
        print(color.yellow(msg))
        while True:
            try:
                choice = input(color.bold(color.purple("{} -> ".format(name))))
                choice = int(choice)
                if choice >= 1 and choice <= len(matches):
                    choice -= 1
                    return choice
                else:
                    print(color.red("Please enter a number between {} and {}.".format(1, len(matches))))
            except:
                print(color.red("Please enter a number between {} and {}.".format(1, len(matches))))

    def create_short_cwd(self, tilde=False):
        current_path = os.getcwd().replace(self.filesystem_root_dir, "")
        if os.sep in current_path:
            dirs = list(filter(None,current_path.split(os.sep)))
            for dir_hash in dirs:
                current_path = current_path.replace(dir_hash, self.translate_from_hash(dir_hash)[0])

        if current_path == "":
            current_path = os.sep

        if tilde:
            current_path = "~" + current_path

        return current_path

    def generate_timestamp(self):
        return math.trunc(datetime.timestamp(datetime.now()))

    def get_filename(self, source):
        source_spl = source.split(os.sep)
        filename = source_spl[-1]
        extension = None
        if "." in filename:
            info = filename.split(".")
            filename = info[0]
            extension = ".{}".format(info[1])
        return filename, extension

    def sort_files_in_dir(self, path, dir_name):
        if len(os.listdir(path)) == 0:
            return
        files = help_functions.get_all_files_from_dir(path)
        dirs = []
        for file in files:
            dirs.append(self.translate_from_hash(file)[6])
        dirs.sort(key=lambda x: x.count(os.sep))
        dirs = help_functions.deduce_dirs(dirs)
        dict = self.create_dirs_in_list(dirs, path)
        self.move_files_in_dirs(files, path, dict)

    def create_dirs_in_list(self, dirs, root_dir):
        mount = root_dir.split(os.sep)[-1]
        dict = {}
        for dir in dirs:
            path = self.filesystem_root_dir
            if os.sep in dir:
                sub = dir.split(os.sep)
                dir = sub[-1]
                dir_hash = self.create_hash(dir)
                for i in range(len(sub) - 1):
                    path = os.path.join(path, sub[i])
                fs_loc = self.hashpath_to_fspath(path)
                os_path = path
                path = os.path.join(path, dir_hash)
                os.mkdir(path)
                self.add_to_dictionary(dir_hash, dir, "directory", os_path, fs_loc, mount=mount)
                dict.update({os.path.join(fs_loc, dir):path})
                for i in range(len(dirs)):
                    dirs[i] = dirs[i].replace(dir, dir_hash, 1)
            else:
                for i in range(len(dirs)):
                    dirs[i] = dirs[i].replace(dir, mount, 1)
                dict.update({dir: root_dir})
        return dict

    def move_files_in_dirs(self, files, mountpath, dict):
        for file in files:
            src = os.path.join(mountpath, file)
            dst = self.edit_dictionary(file, op='get', property="fs_path")
            dst = os.path.join(mountpath, dict.get(dst))
            dst = os.path.join(dst, file)
            os.rename(src, dst)
