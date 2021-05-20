import os
from browser import help_functions

BUFFER_SIZE = 8 * 1024

class Filehandler:

    def __init__(self, unionpath, client):
        self.unionpath = unionpath
        self.client = client

    def send_file(self, hash):
        name, timestamp, type, location, hash, extension, fs_path, mount = self.unionpath.translate_from_hash(hash)
        name = name.replace(" ",".")
        filepath = os.path.join(location, hash)
        self.client.send("FILE {} {} {} {} {} {}".format(hash, name, timestamp, extension, fs_path, mount))
        response = self.client.get()
        if response == "READY":
            try:
                with open(filepath, 'rb') as file:
                    while True:
                        bytes = file.read()
                        if not bytes:
                            break
                        self.client.send_bytes(bytes)
                    self.client.send_bytes(b'\EOF')
                response = self.client.get()
                if response == "FINISHED":
                    return True
            except:
                self.client.send_bytes(b'\INT')
                return False
        else:
            return False

    def send_all_files_of_dir(self, dir):
        files = help_functions.get_all_files_from_dir(dir)
        for f in files:
            self.send_file(f)

    def get_file(self, message, dir=None, mount=None):
        cmd, hash, name, timestamp, extension, fs_path, mount, location = message.split()
        name = name.replace(".", " ")
        if fs_path == "root":
            fs_path = ""
        if extension == "None":
            extension = ""
        if mount == "None" or not mount:
            mount = ""
        self.unionpath.add_to_dictionary(hash, name, type="file",location=location, fs_path=fs_path, extension=extension, mount=mount,timestamp=timestamp)
        self.client.send("READY")
        if dir:
            location = os.path.join(self.unionpath.filesystem_root_dir, dir)
            location = os.path.join(location, hash)
        else:
            location = os.path.join(self.unionpath.filesystem_root_dir, hash)
        with open(location, "wb") as file:
            while True:
                bytes = self.client.server_socket.recv(BUFFER_SIZE)
                file.write(bytes)
                if bytes.strip()[-3:] == b'EOF':
                    break
            file.close()
        self.client.send("FINISHED")
        return True