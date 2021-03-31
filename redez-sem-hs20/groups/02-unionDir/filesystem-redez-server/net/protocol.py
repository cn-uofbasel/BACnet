

class Protocol:

    def __init__(self, client, unionpath):
        self.client = client
        self.unionpath = unionpath

    def handle(self, message):
        cmd = message.split()
        if cmd[0] == "CON":
            self.unionpath.edit_clientlist("add", hash=cmd[1], name=cmd[2])
            print("{} has connected to the server".format(cmd[2]))