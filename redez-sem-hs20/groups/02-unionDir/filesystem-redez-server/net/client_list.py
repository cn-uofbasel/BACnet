
class ClientList:

    def __init__(self):
        self.clients = {}

    def add(self, hashk, client):
        self.clients.update({hashk: client})

    def rem(self, hashk):
        del self.clients[hashk]

    def send_to(self, hashk, msg):
        client = self.clients.get(hashk)
        client.send(msg)

    def send_all(self, msg):
        for key in self.clients:
            self.send_to(key, msg)