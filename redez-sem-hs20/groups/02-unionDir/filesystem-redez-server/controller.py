import json
import os
import create

def add_user(client_file, server_file, user, ip, hash):
    client_json = open(client_file, "r")
    client_list = json.load(client_json)
    client_json.close()
    if client_list.get(hash):
        print("returning")
        return
    client_json = open(client_file, "w")
    client_list.update({hash: {"ip": ip, "user":user}})
    json.dump(client_list, client_json, indent=4)
    client_json.close()
    server_json = open(server_file, "r")
    server_list = json.load(server_json)
    server_json.close()
    server_json = open(server_file, "w")
    server_list.update({hash: {}})
    json.dump(server_list, server_json, indent=4)
    server_json.close()

def add_filesystem(server_file, name, hash, path):
    server_json = open(server_file, "r")
    server_list = json.load(server_json)
    server_json.close()
    try:
        accesses = [hash]
        if server_list.get(hash).get(name):
            return "CRET"
        else:
            root_path = os.path.join(create.filesystem_path(),path)
            content_json_path = os.path.join(root_path, "{}.json".format(hash))
            add = {"name":name, "root": root_path, "content_json": content_json_path, "accesses": accesses}
            add = {name: add}
            server_list.get(hash).update(add)
            dump(server_file, server_list)
        return "CNEW"
    except:
        dump(server_file, server_list)

def dump(file, data):
    json_file = open(file, "w")
    json.dump(data, json_file, indent=4)
    json_file.close()

