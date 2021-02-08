import json

from BaseHandler import BaseHandler
from TCPClient import TCPClient


class RawTcpHandler(BaseHandler):

    def __init__(self):
        self.handlers = {}
        self.tcp_client: TCPClient = None
        self.set_handler("init", self.handle_init)
        self.set_handler("stop", self.handle_stop)
        self.set_handler("do_stuff", self.do_stuff)
        pass

    def handle_tcp(self, payload):
        # Here we can handle some tcp request and then append it into the BACnet
        print('payload')

    def handle_init(self, event, json_payload):
        payload = json.loads(json_payload)
        host = payload['host']
        port = payload['port']
        self.tcp_client = TCPClient(self)
        return {"success": self.tcp_client.connect(host, port)}

    def handle_stop(self, event, json_payload):
        if not self.check():
            return None
        return {"success": self.tcp_client.stop()}

    def do_stuff(self, event, json_payload):
        if not self.check():
            return None
        # Here we could translate some BACnet request into a TCP request

    def check(self):
        if self.tcp_client is not None:
            return self.tcp_client.connected
        return False
